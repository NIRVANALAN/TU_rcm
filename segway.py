# coding=utf-8
import numpy
import cv2
import math
from skimage import measure
from PyQt5.QtWidgets import QMessageBox
from skimage.feature import hog
from sklearn import svm
from sklearn.externals import joblib


def density(a, arg, geshi):
	b = len(a[0])
	c = len(a)
	n = 11
	beilv = geshi.b / geshi.bei[geshi.l]
	grey = cv2.cvtColor(a, cv2.COLOR_BGRA2GRAY)
	greyret, greyimg = cv2.threshold(grey, 225, 255, cv2.THRESH_BINARY_INV)
	base = greyimg
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
	greyimg = cv2.dilate(greyimg, kernel, iterations=int(geshi.bei[geshi.la] / geshi.b * beilv / 20))
	greyimg = cv2.erode(greyimg, kernel, iterations=int(geshi.bei[geshi.la] / geshi.b * beilv / 20))
	greyimg = cv2.add(base, greyimg)
	averagegreyimg = cv2.blur(greyimg, (n, n))
	
	bb, gg, rr, aa = cv2.split(a)
	rgbimg = cv2.merge((bb, gg, rr))
	hsv = cv2.cvtColor(rgbimg, cv2.COLOR_BGR2HSV)
	
	fibrosis = cv2.inRange(hsv, (90, 50, 50), (140, 255, 255))
	
	labels = measure.label(fibrosis, connectivity=2)
	number = labels.max() + 1
	totalBlock = 0
	
	for i in range(1, number):
		j = numpy.zeros((c, b), numpy.uint8)
		j[labels == i] = 255
		totalBlock = totalBlock + cv2.countNonZero(j)
	
	if number > 0:
		QMessageBox.about(None, "fibrosis block",
		                  "number:%s" % str(number) + " average area:%s" % str(int(totalBlock / number)))
	
	total = cv2.countNonZero(greyimg[int(2 * c / 5):int(3 * c / 5), int(2 * b / 5):int(3 * b / 5)])
	fibNumber = cv2.countNonZero(fibrosis[int(2 * c / 5):int(3 * c / 5), int(2 * b / 5):int(3 * b / 5)])
	
	averagefibrosis = cv2.blur(fibrosis, (n, n))
	averagedensity = cv2.divide(averagefibrosis, averagegreyimg, None, 255)
	averagedensity = cv2.subtract(averagedensity, cv2.subtract(255, greyimg))
	averagedensity = cv2.cvtColor(averagedensity, cv2.COLOR_GRAY2BGR)
	averagedensity = cv2.rectangle(averagedensity, (int(2 * b / 5), int(2 * c / 5)), (int(3 * b / 5), int(3 * c / 5)),
	                               (0, 0, 255), 2)
	if total > 20:
		averagedensity = cv2.putText(averagedensity, 'density:' + str(100 * float(fibNumber) / float(total))[0:4] + '%',
		                             (int(2 * b / 5), int(2 * c / 5 - 20 * beilv)), cv2.FONT_HERSHEY_COMPLEX,
		                             0.8 * beilv, (0, 0, 255), int(2 * beilv))
	else:
		averagedensity = cv2.putText(averagedensity, 'No cells', (int(2 * b / 5), int(2 * c / 5 - 20)),
		                             cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
	averagedensity = cv2.putText(averagedensity, 'total density:' + str(100 * arg['totaldensity'])[0:4] + '%',
	                             (int(2 * b / 5), int(3 * c / 5 + 20 * beilv)), cv2.FONT_HERSHEY_COMPLEX, 0.8 * beilv,
	                             (0, 0, 255), int(2 * beilv))
	averagedensity = cv2.cvtColor(averagedensity, cv2.COLOR_BGR2BGRA)
	return {'image': averagedensity}


def abjust(a, arg, geshi):
	bbbb = len(a[0])
	c = len(a)
	mason = arg['masonimg']
	dimension = arg['dimensions']
	left = int((geshi.x - geshi.w * geshi.b / 2) / (geshi.wa / dimension[0]))
	top = int((geshi.y - geshi.h * geshi.b / 2) / (geshi.ha / dimension[1]))
	right = int((geshi.x + geshi.w * geshi.b / 2) / (geshi.wa / dimension[0]))
	buttom = int((geshi.y + geshi.h * geshi.b / 2) / (geshi.ha / dimension[1]))
	w = right - left
	h = buttom - top
	img = numpy.zeros((h, w), type(mason[0][0]))
	if left < 0:
		l = -left
		ll = 0
	else:
		l = 0
		ll = left
	if right > len(mason[0]):
		r = len(mason[0]) - right
		rr = len(mason[0])
	else:
		r = len(img[0])
		rr = right
	if top < 0:
		t = -top
		tt = 0
	else:
		t = 0
		tt = top
	if buttom > len(mason):
		b = len(mason) - buttom
		bb = len(mason[0])
	else:
		b = len(img)
		bb = buttom
	ball = mason[tt:bb, ll:rr]
	img[t:b, l:r] = ball
	img = cv2.resize(img, (bbbb, c), cv2.INTER_CUBIC)
	img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
	image = cv2.addWeighted(img, 0.5, a, 1, -128)
	return {'image': image}


def detectprocess(a, arg, geshi):
	if geshi.l > 0:
		return {'image': a}
	else:
		b = len(a[0])
		c = len(a)
		a = cv2.cvtColor(a, cv2.COLOR_BGRA2BGR)
		hsv = cv2.cvtColor(a, cv2.COLOR_BGR2HSV)
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
		better = cv2.cvtColor(dist_transform, cv2.COLOR_GRAY2BGR)
		
		sure_fg = numpy.uint8(sure_fg)
		unknown = cv2.subtract(sure_bg, sure_fg)
		
		ret, markers = cv2.connectedComponents(sure_fg)
		
		markers = markers + 1
		
		markers[unknown == 255] = 0
		markers = cv2.watershed(a, markers)
		a[markers == -1] = [255, 0, 0]
		
		for i in range(0, markers.max() + 1):
			j = numpy.zeros((c, b), numpy.uint8)
			j[markers == i] = 255
			area = cv2.countNonZero(j)
			if area > 321:
				jd = cv2.dilate(j, kernel, iterations=2)
				image, lines, hier = cv2.findContours(jd, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
				white = 0
				total = 0
				for k in lines[0]:
					total = total + 1
					if hsv[k[0][1]][k[0][0]][1] < 80:
						white = white + 1
				
				if white > total / 2:
					m = cv2.moments(j)
					x = int(m["m10"] / m["m00"])
					y = int(m["m01"] / m["m00"])
					cv2.circle(a, (x, y), int(math.sqrt(area) + 10), (0, 0, 255), 2)
		
		a = cv2.cvtColor(a, cv2.COLOR_BGR2BGRA)
		re = cv2.cvtColor(sure_bg, cv2.COLOR_GRAY2BGRA)
		return {'image': a}


def averprocess(a, arg, geshi):
	if geshi.l < 0:
		return {'image': a}
	else:
		b = len(a[0])
		c = len(a)
		a = cv2.cvtColor(a, cv2.COLOR_BGRA2BGR)
		hsv = cv2.cvtColor(a, cv2.COLOR_BGR2HSV)
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
		better = cv2.cvtColor(dist_transform, cv2.COLOR_GRAY2BGR)
		
		sure_fg = numpy.uint8(sure_fg)
		unknown = cv2.subtract(sure_bg, sure_fg)
		
		ret, markers = cv2.connectedComponents(sure_fg)
		
		markers = markers + 1
		
		markers[unknown == 255] = 0
		markers = cv2.watershed(a, markers)
		a[markers == -1] = [255, 0, 0]
		
		number = 0
		for i in range(0, markers.max() + 1):
			j = numpy.zeros((c, b), numpy.uint8)
			j[markers == i] = 255
			area = cv2.countNonZero(j)
			if area > 321:
				number = number + 1
				
				m = cv2.moments(j)
				x = int(m["m10"] / m["m00"])
				y = int(m["m01"] / m["m00"])
				cv2.circle(a, (x, y), int(math.sqrt(area) + 10), (0, 0, 255), 2)
		
		body = cv2.inRange(hsv, (145, 40, 0), (180, 255, 255))
		total = cv2.countNonZero(body)
		
		gray = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
		fd, hog_image = hog(gray, orientations=8, pixels_per_cell=(200, 200), cells_per_block=(1, 1),
		                    block_norm='L2-Hys', visualise=True)
		f = [0] * 200
		if len(fd) < 200:
			n = 0
			while n < 200:
				f[n] = fd[n % len(fd)] * 100
				n = n + 1
		else:
			for j in range(0, 200):
				f[j] = fd[j] * 100
		
		clf = joblib.load('svm.pkl')
		pre = clf.predict([f])
		name = ['none', 'length cutting', '横', '斜', '乱']
		
		if number > 0:
			a = cv2.putText(a, 'Average Area:' + str(int(float(total) / float(number))) + ' ' + name[pre[0]], (20, 30),
			                cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2)
		a = cv2.cvtColor(a, cv2.COLOR_BGR2BGRA)
		# body = cv2.cvtColor(body,cv2.COLOR_GRAY2BGRA)
		return {'image': a}
