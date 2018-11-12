import math
import time
import cv2
import numpy
import openslide
from skimage.feature import hog
from sklearn import svm
from sklearn.externals import joblib
from skimage import measure

kp1 = 0
kp2 = 0
go = 0
ac = 0


def densityprocess(slide, level):
	n = 21
	workingDimensions = slide.level_dimensions[level]
	img = numpy.array(slide.read_region((0, 0), level, workingDimensions))
	grey = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
	greyret, greyimg = cv2.threshold(grey, 225, 255, cv2.THRESH_BINARY_INV)
	averagegreyimg = cv2.blur(greyimg, (n, n))
	'''
	plt.imshow(averagegreyimg)
	plt.show()
	'''
	surf = cv2.xfeatures2d.SURF_create(5000)
	kp, des = surf.detectAndCompute(averagegreyimg, None)
	return {'key': kp, 'des': des, 'dimensions': workingDimensions, 'picture': greyimg}


def fibrosis(slide, fibrosislevel):
	workingDimensions = slide.level_dimensions[fibrosislevel]
	img = numpy.array(slide.read_region((0, 0), fibrosislevel, workingDimensions))
	rr, gg, bb, aa = cv2.split(img)
	rgbimg = cv2.merge((bb, gg, rr))
	hsv = cv2.cvtColor(rgbimg, cv2.COLOR_BGR2HSV)
	hsv = cv2.inRange(hsv, (90, 20, 20), (140, 255, 255))
	return hsv


def averagefibrosis(slide, slide2):
	maxLevel = slide.level_count - 1
	# print 'maxLevel:',maxLevel,slide2.level_count-1
	level = maxLevel - 4
	he = densityprocess(slide, level)
	mason = densityprocess(slide2, level)
	global kp1
	global kp2
	global go
	global ac
	kp1 = len(he['key'])
	kp2 = len(mason['key'])
	bf = cv2.BFMatcher()
	matches = bf.knnMatch(mason['des'], he['des'], k=2)
	
	MIN_MATCH_COUNT = 10
	good = []
	for m, n in matches:
		if m.distance < 0.75 * n.distance:
			good.append(m)
	go = len(good)
	if len(good) > MIN_MATCH_COUNT:
		src_pts = numpy.float32([mason['key'][m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
		dst_pts = numpy.float32([he['key'][m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
		M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
		masonimg1 = cv2.warpPerspective(mason['picture'], M, (len(he['picture'][0]), len(he['picture'])))
		dif = cv2.absdiff(masonimg1, he['picture'])
		difnumber = cv2.countNonZero(dif)
		totnumber = len(he['picture'][0]) * len(he['picture'])
		ac = float(difnumber) / float(totnumber)
	else:
		print
		'Not enough'
		return
	'''
	fibrosislevel = 3
	masonimg = fibrosis(slide2,fibrosislevel)
	bei = slide2.level_dimensions[fibrosislevel][0]/mason['dimensions'][0]
	M[0][2] = M[0][2]*bei
	M[1][2] = M[1][2]*bei
	M[2][0] = M[2][0]/bei
	M[2][1] = M[2][1]/bei
	masonimg = cv2.warpPerspective(masonimg,M,slide.level_dimensions[fibrosislevel])
	return {'masonimg':masonimg,'dimensions':slide.level_dimensions[fibrosislevel]}
	'''


def detectprocess(a, hsv):
	b = len(hsv[0])
	c = len(hsv)
	h, s, v = cv2.split(hsv)
	h = cv2.subtract(180, h)
	ret, s = cv2.threshold(s, 20, 255, cv2.THRESH_BINARY_INV)
	gray = cv2.addWeighted(s, -1, h, 1, 0)
	
	kernel = numpy.ones((3, 3), numpy.uint8)
	
	ret, nuclear0 = cv2.threshold(gray, 35, 255, cv2.THRESH_BINARY)
	nuclear0 = cv2.morphologyEx(nuclear0, cv2.MORPH_OPEN, kernel, iterations=2)
	sure_bg = cv2.dilate(nuclear0, kernel, iterations=3)
	
	ret, nuclear1 = cv2.threshold(gray, 35, 255, cv2.THRESH_BINARY)
	for i in range(0, len(nuclear1[0])):
		nuclear1[0][i] = 0
	mask = numpy.zeros((c + 2, b + 2), numpy.uint8)
	cv2.floodFill(nuclear1, mask, (0, 0), 100)
	nuclear1[nuclear1 == 0] = 255
	nuclear1[nuclear1 == 100] = 0
	
	dist_transform = cv2.distanceTransform(nuclear1, cv2.DIST_L2, 5)
	dist_transform = numpy.uint8(dist_transform)
	ret, out = cv2.threshold(dist_transform, 5, 255, cv2.THRESH_BINARY_INV)
	nuclear1 = 255 - nuclear1
	gray1 = cv2.subtract(gray, nuclear1)
	gray1 = cv2.blur(gray1, (5, 5))
	dist_transform = cv2.addWeighted(dist_transform, 1, gray1, 0.1, 0)
	max = cv2.dilate(dist_transform, kernel, iterations=10)
	max = cv2.multiply(max, 0.75)
	sure_fg = cv2.subtract(dist_transform, max)
	sure_fg = cv2.subtract(sure_fg, out)
	ret, sure_fg = cv2.threshold(sure_fg, 0, 255, cv2.THRESH_BINARY)
	
	sure_fg = numpy.uint8(sure_fg)
	unknown = cv2.subtract(sure_bg, sure_fg)
	
	ret, markers = cv2.connectedComponents(sure_fg)
	
	markers = markers + 1
	
	markers[unknown == 255] = 0
	markers = cv2.watershed(a, markers)
	
	detect = [0, 0]
	for i in range(0, markers.max() + 1):
		j = numpy.zeros((c, b), numpy.uint8)
		j[markers == i] = 255
		area = cv2.countNonZero(j)
		if area > 361:
			detect[1] = detect[1] + 1
			jd = cv2.dilate(j, kernel, iterations=2)
			image, lines, hier = cv2.findContours(jd, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
			white = 0
			total = 0
			for k in lines[0]:
				total = total + 1
				if hsv[k[0][1]][k[0][0]][1] < 80:
					white = white + 1
			if white > total / 2:
				detect[0] = detect[0] + 1
	
	return (detect[0], detect[1])


#######################__main_##########3
startTime = time.time()
clf = joblib.load('/home/zhourongchen/zrc/heart/svm.pkl')
patients = ['/25845', '/28330', '/29708', '/30638', '/31398', '/35485']

for jj in range(0, 6):
	for kk in range(1, 7):
		print
		patients[jj], kk
		imgdir = '/home/zhourongchen/zrc/rcm/images'
		patient = patients[jj]
		imgname = patient + '-' + str(kk) + '.ndpi'
		path = imgdir + '/HE' + patient + imgname
		path1 = imgdir + '/MASSON' + patient + imgname
		name = patient[1:] + '-' + str(kk)
		
		'''
		imgdir = 'C:\Users\lenovo\Desktop\\'
		name = '25845-' + str(kk)
		imgname = name + 'm.ndpi'
		heimgname = name + '.ndpi'
		path = imgdir + heimgname
		path1 = imgdir + imgname
		
		outputPath = './maxresult.txt'
		outputimage = './' + name
		slide = openslide.open_slide(path)
		slide2 = openslide.open_slide(path1)
		mason = averagefibrosis(slide, slide2)
		dimension = slide.dimensions
		'''

		result = [[],[]]
		beilv = dimension[0]/ mason['dimensions'][0]
		countbodyMax = 0
		meanmax = 0
		detectmax = 0
		avermax = 0
		numbermax = 0
		averageBlockMax = 0
		for y in range(0,dimension[1]-1000,1000):
			result[0].append([])
			result[1].append([])
			for x in range(0,dimension[0]-1000,1000):
				print (int(x/1000),int(y/1000))
				region = numpy.array(slide.read_region((x,y),0,(1000,1000)))
				region = cv2.cvtColor(region,cv2.COLOR_RGBA2BGR)
				hsv = cv2.cvtColor(region,cv2.COLOR_BGR2HSV)
				body = cv2.inRange(hsv,(0,40,0),(180,255,255))
				countbody = cv2.countNonZero(body)
				if countbody > 1000*1000*0.5:
					masonimg = mason['masonimg'][int(y/beilv):int((y+1000)/beilv),int(x/beilv):int((x+1000)/beilv)]
					mean = float(cv2.countNonZero(masonimg))/float(countbody)*beilv*beilv
					detect = detectprocess(region,hsv)

					labels = measure.label(masonimg,connectivity=2)
					number = labels.max()+1
					totalBlock = 0
					for i in range(1,number):
						j = numpy.zeros((len(masonimg[0]),len(masonimg)),numpy.uint8)
						j[labels == i] = 255
						totalBlock = totalBlock + cv2.countNonZero(j)
					averageBlock = int(totalBlock/number)

					a = cv2.cvtColor(region,cv2.COLOR_BGR2GRAY)
					fd, hog_image = hog(a,orientations=8, pixels_per_cell=(200, 200),cells_per_block=(1, 1),block_norm='L2-Hys', visualise=True)
					for i in range(0,len(fd)):
						fd[i] = fd[i] * 100
						prediction =  clf.predict([fd])

					result[0][len(result[0])-1].append([countbody,mean,detect[0],detect[1]])
					result[1][len(result[1])-1].append([number,averageBlock,prediction[0]])

					if countbody > countbodyMax:
						countbodyMax = countbody
					if mean > meanmax:
						meanmax = mean
					if detect[0] > detectmax:
						detectmax = detect[0]
					if detect[1] > avermax:
						avermax = detect[1]
					if number > numbermax:
						numbermax = number
					if averageBlock > averageBlockMax:
						averageBlockMax = averageBlock
				else:
					result[0][len(result[0])-1].append([0,0,0,0])
					result[1][len(result[1])-1].append([0,0,0])
				print (result[0][len(result[0])-1][len(result[0][len(result[0])-1])-1],result[1][len(result[1])-1][len(result[1][len(result[1])-1])-1])

		result[0] = numpy.array(result[0])
		result[1] = numpy.array(result[1])
		s,a,b,c = cv2.split(result[0])
		d,e,f = cv2.split(result[1])
		print (countbodyMax,0,meanmax,1,detectmax,2,avermax,3,numbermax,4,averageBlockMax)
		s = cv2.multiply(s,255)
		a = cv2.multiply(a,255)
		b = cv2.multiply(b,255)
		c = cv2.multiply(c,255)
		d = cv2.multiply(d,255)
		e = cv2.multiply(e,255)
		f = cv2.multiply(f,51)
		s = cv2.divide(s,countbodyMax)
		a = cv2.divide(a,meanmax)
		b = cv2.divide(b,detectmax)
		c = cv2.divide(c,avermax)
		d = cv2.divide(d,int(numbermax))
		e = cv2.divide(e,int(averageBlockMax))
		result[0] = cv2.merge([s,a,b,c])
		result[1] = cv2.merge([d,e,f])
		cv2.imwrite(outputimage + '0.png',result[0])
		cv2.imwrite(outputimage + '1.png',result[1])

		outputFile = open(outputPath ,'a+')
		outputFile.write(name + ',' + str(countbodyMax) + ',' + str(meanmax) + ',' +str(detectmax) +',' + str(avermax) +',' + str(numbermax) +',' + str(averageBlockMax) + '\n' )
		outputFile.close()
		print (time.time()-startTime)
		
		
		'''
		outputFile = open('./curray.txt', 'a+')
		outputFile.write(str(kp1) + ' ' + str(kp2) + ' ' + str(go) + ' ' + str(ac) + '\n')
		outputFile.close()
		'''
