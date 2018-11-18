# -*- coding:UTF-8 -*-
from math import *
from operator import itemgetter

from adjust import *


def editareaHE(level, slide):
	print "called editHE"
	# for i in self.annotation.list:
	# 	if i.name.split(":")[0] == 'density':
	# 		i.hide()
	# 		i.deleting()
	# 		del i
	# self.canchange = []
	n = 21
	# if self.geshi.la > 4:
	# 	# 	level = self.geshi.la - 4
	# 	# else:
	# 	# 	level = self.geshi.la - 1
	workingDimensions = slide.level_dimensions[level]
	img = np.array(slide.read_region((0, 0), level, workingDimensions))
	
	b, g, r, a = cv2.split(img)
	rgbimg = cv2.merge((r, g, b))
	hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
	# greyimg = cv2.inRange(hsv, (0, 20, 0), (180, 255, 180))
	greyimg = cv2.inRange(hsv, (0, 20, 0), (180, 255, 220))
	fibrosis = cv2.inRange(hsv, (90, 20, 0), (150, 255, 255))
	# cv2.imshow("fibrosis",fibrosis)
	averagegreyimg = cv2.blur(greyimg, (30, 30))
	# cv2.imshow('average grey img', averagegreyimg)
	# cv2.imwrite("test/HE/average_grey_img.jpg", averagegreyimg)
	
	ret, erode = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
	erode = cv2.erode(erode, kernel, iterations=3)
	# cv2.imshow("after erosion", erode)
	# cv2.imwrite("test/HE/after_erosion.jpg", erode)
	
	# cv2.imshow("")
	#  多次腐蚀，除去小梁
	
	ret, averimage = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
	averimage, avercnts, averhierarchy = cv2.findContours(averimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# cv2.imshow("aver image", averimage)
	
	# 得到整体的边界
	
	image, cnts, hierarchy = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# cv2.imshow("contour after erosion", erode)
	# 腐蚀后的边界
	
	object = []
	maxarea = 0
	max = None
	
	for cnt in cnts:
		area = cv2.contourArea(cnt)
		if area > 100:
			points = []
			for i in cnt:
				x = i[0][0]
				y = i[0][1]
				points.append([x, y])
			i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
			cv2.fillPoly(i, np.array([points], np.int32), 255)
			object.append(i)
			if area > maxarea:
				maxarea = area
				max = len(object) - 1
	wall = object[max]
	# 把每一个区域都分割出来，最大的心肌壁
	
	other = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
	for i in range(0, len(object)):
		if i != max:
			other = cv2.add(other, object[i])
	
	# 通过矩moments计算重心
	M1 = cv2.moments(wall)
	cx1 = int(M1["m10"] / M1["m00"])
	cy1 = int(M1["m01"] / M1["m00"])
	
	M0 = cv2.moments(other)
	cx0 = int((M0["m10"]) / (M0["m00"]))
	cy0 = int((M0["m01"]) / (M0["m00"]))
	
	if cx0 - cx1 == 0:
		if cy0 - cy1 > 0:
			baseangle = 90
		else:
			baseangle = -90
	else:
		if cx0 - cx1 > 0:
			baseangle = 180 * math.atan(-(cy0 - cy1) / (cx0 - cx1)) / math.pi
		else:
			baseangle = 180 + 180 * math.atan(-(cy0 - cy1) / (cx0 - cx1)) / math.pi
	
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
	wall = cv2.dilate(wall, kernel, iterations=15)
	# cv2.imshow("wall", wall)
	other = cv2.dilate(other, kernel, iterations=15)
	# cv2.imshow("other", other)
	
	image, contours, hierarchy = cv2.findContours(wall, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	image1, contours1, hierarchy1 = cv2.findContours(other, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	points = cv2.approxPolyDP(contours[0], 15, True)  # 主要功能是把一个连续光滑曲线折线化，对图像轮廓点进行多边形拟合。
	points1 = []
	for i in contours1:  # contours1 : other
		for j in i:
			points1.append(j)
	points1 = np.array(points1)
	
	rect = cv2.minAreaRect(points)
	rect1 = cv2.minAreaRect(points1)
	# 最小外切矩形
	
	rect = (rect[0], rect[1], -rect[2])  # ?
	if (math.fabs(rect[2] - baseangle) % 360) < 45 or (math.fabs(rect[2] - baseangle) % 360) > 135:
		angle = 90 - rect[2]
		width = rect[1][1]
		height = rect[1][0]
	else:
		angle = rect[2]
		width = rect[1][0]
		height = rect[1][1]
	points = rotatePoints(points, rect[0], -angle)
	
	for i in avercnts:
		averpoints = rotatePoints(i, rect[0], -angle)
	
	notheightPoints = [[], []]
	for i in range(0, len(points)):
		if points[i][0][1] - rect[0][1] > height / 5:
			notheightPoints[0].append(points[i])
		else:
			if points[i][0][1] - rect[0][1] < -height / 5:
				notheightPoints[1].append(points[i])
	
	avery0 = 0
	for i in range(0, len(notheightPoints[0])):
		avery0 = avery0 + notheightPoints[0][i][0][1]
	avery0 = avery0 / len(notheightPoints[0])
	avery1 = 0
	for i in range(0, len(notheightPoints[1])):
		avery1 = avery1 + notheightPoints[1][i][0][1]
	avery1 = avery1 / len(notheightPoints[1])
	
	if (baseangle % 360) < 180:
		if avery1 < avery0:
			abc = notheightPoints[0]
			notheightPoints[0] = notheightPoints[1]
			notheightPoints[1] = abc
	else:
		if avery1 > avery0:
			abc = notheightPoints[0]
			notheightPoints[0] = notheightPoints[1]
			notheightPoints[1] = abc
	
	nothei1 = []
	for i in avercnts:
		for j in i:
			distance0 = 100000
			for k in notheightPoints[0]:
				distance = math.sqrt(
					(j[0][0] - k[0][0]) * (j[0][0] - k[0][0]) + (j[0][1] - k[0][1]) * (j[0][1] - k[0][1]))
				if distance < distance0:
					distance0 = distance
			distance1 = 100000
			for k in notheightPoints[1]:
				distance = math.sqrt(
					(j[0][0] - k[0][0]) * (j[0][0] - k[0][0]) + (j[0][1] - k[0][1]) * (j[0][1] - k[0][1]))
				if distance < distance1:
					distance1 = distance
			if distance1 < distance0 / 2:
				nothei1.append(j)
	
	notheightPoints[1] = nothei1
	
	for i in range(0, len(notheightPoints[0])):
		notheightPoints[0][i] = [notheightPoints[0][i][0][0], notheightPoints[0][i][0][1]]
	for i in range(0, len(notheightPoints[1])):
		notheightPoints[1][i] = [notheightPoints[1][i][0][0], notheightPoints[1][i][0][1]]
	notheightPoints[0].sort()
	notheightPoints[1].sort()
	for i in range(0, len(notheightPoints[0])):
		notheightPoints[0][i] = [[notheightPoints[0][i][0], notheightPoints[0][i][1]]]
	for i in range(0, len(notheightPoints[1])):
		notheightPoints[1][i] = [[notheightPoints[1][i][0], notheightPoints[1][i][1]]]
	
	xlist = []
	for i in notheightPoints[0]:
		xlist.append((i[0][0], i[0][1], 0))
	for i in notheightPoints[1]:
		xlist.append((i[0][0], i[0][1], 1))
	xlist.sort(key=itemgetter(0))
	
	addPoints = [[], []]
	for i in range(0, len(xlist)):
		pl = i - 1
		pr = i + 1
		if xlist[i][2] == 0:
			n = 0
			m = 1
		else:
			n = 1
			m = 0
		while pl >= 0 and xlist[pl][2] == xlist[i][2]:
			pl = pl - 1
		while pr < len(xlist) and xlist[pr][2] == xlist[i][2]:
			pr = pr + 1
		if pl >= 0 and pr < len(xlist):
			y = (xlist[pl][1]) * (xlist[pr][0] - xlist[i][0]) / (xlist[pr][0] - xlist[pl][0]) + (xlist[pr][1]) * (
					xlist[i][0] - xlist[pl][0]) / (xlist[pr][0] - xlist[pl][0])
			addPoints[n].append([[int(xlist[i][0]), int((xlist[i][1] - y) / 3 + y)]])
			addPoints[m].append([[int(xlist[i][0]), int((xlist[i][1] - y) * 2 / 3 + y)]])
		elif pl < 0:
			addPoints[n].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pr][1]) / 3 + xlist[pr][1])]])
			addPoints[m].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pr][1]) * 2 / 3 + xlist[pr][1])]])
		else:
			addPoints[n].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pl][1]) / 3 + xlist[pl][1])]])
			addPoints[m].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pl][1]) * 2 / 3 + xlist[pl][1])]])
	
	notheightPoints[0] = rotatePoints(notheightPoints[0], rect[0], angle)
	notheightPoints[1] = rotatePoints(notheightPoints[1], rect[0], angle)
	addPoints[0] = rotatePoints(addPoints[0], rect[0], angle)
	addPoints[1] = rotatePoints(addPoints[1], rect[0], angle)
	
	m = cv2.moments(np.array(notheightPoints[1]))
	cx1 = int(m["m10"] / m["m00"])
	cy1 = int(m["m01"] / m["m00"])
	
	addPoints[1].reverse()
	notheightPoints[1].reverse()
	first = notheightPoints[0] + addPoints[1]
	second = addPoints[0] + addPoints[1]
	third = addPoints[0] + notheightPoints[1]
	
	i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
	firstmask = cv2.fillPoly(i, np.array([first], np.int32), 255)
	# cv2.imshow("firstmask", firstmask)
	# print firstmask[363][154]
	
	i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
	secondmask = cv2.fillPoly(i, np.array([second], np.int32), 255)
	
	i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
	thirdmask = cv2.fillPoly(i, np.array([third], np.int32), 255)
	
	firstdensity = areaaveragedensity(fibrosis, greyimg, firstmask)
	seconddensity = areaaveragedensity(fibrosis, greyimg, secondmask)
	thirddensity = areaaveragedensity(fibrosis, greyimg, thirdmask)
	
	box1 = cv2.boxPoints(rect1)
	box1 = np.array(box1)
	for i in range(0, 2):
		max = sqrt((box1[i][0] - cx1) * (box1[i][0] - cx1) + (box1[i][1] - cy1) * (box1[i][1] - cy1))
		n = i
		for j in range(i, 4):
			if sqrt((box1[j][0] - cx1) * (box1[j][0] - cx1) + (box1[j][1] - cy1) * (box1[j][1] - cy1)) > max:
				max = sqrt((box1[j][0] - cx1) * (box1[j][0] - cx1) + (box1[j][1] - cy1) * (box1[j][1] - cy1))
				n = j
		k = (box1[i][0], box1[i][1])
		box1[i] = box1[n]
		box1[n] = [k[0], k[1]]
	
	firstarea = 'Endocardium'
	thirdarea = 'Epicardium'
	otherline = notheightPoints[0]
	
	if sqrt((box1[0][0] - otherline[0][0][0]) * (box1[0][0] - otherline[0][0][0]) + (
			box1[0][1] - otherline[0][0][1]) * (box1[0][1] - otherline[0][0][1])) > sqrt(
		(box1[1][0] - otherline[0][0][0]) * (box1[1][0] - otherline[0][0][0]) + (
				box1[1][1] - otherline[0][0][1]) * (box1[1][1] - otherline[0][0][1])):
		otherline.append([[box1[0][0], box1[0][1]]])
		otherline.append([[box1[1][0], box1[1][1]]])
	else:
		otherline.append([[box1[1][0], box1[1][1]]])
		otherline.append([[box1[0][0], box1[0][1]]])
	
	i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
	othermask = cv2.fillPoly(i, np.array([otherline], np.int32), 255)
	otherdensity = areaaveragedensity(fibrosis, greyimg, othermask)
	return firstmask, secondmask, thirdmask, othermask


def detectprocess(a, hsv):
	b = len(hsv[0])
	c = len(hsv)
	h, s, v = cv2.split(hsv)
	h = cv2.subtract(180, h)
	ret, s = cv2.threshold(s, 20, 255, cv2.THRESH_BINARY_INV)
	gray = cv2.addWeighted(s, -1, h, 1, 0)
	
	kernel = np.ones((3, 3), np.uint8)
	
	ret, nuclear0 = cv2.threshold(gray, 35, 255, cv2.THRESH_BINARY)
	nuclear0 = cv2.morphologyEx(nuclear0, cv2.MORPH_OPEN, kernel, iterations=2)
	sure_bg = cv2.dilate(nuclear0, kernel, iterations=3)
	
	ret, nuclear1 = cv2.threshold(gray, 35, 255, cv2.THRESH_BINARY)
	for i in range(0, len(nuclear1[0])):
		nuclear1[0][i] = 0
	mask = np.zeros((c + 2, b + 2), np.uint8)
	cv2.floodFill(nuclear1, mask, (0, 0), 100)
	nuclear1[nuclear1 == 0] = 255
	nuclear1[nuclear1 == 100] = 0
	
	dist_transform = cv2.distanceTransform(nuclear1, cv2.DIST_L2, 5)
	dist_transform = np.uint8(dist_transform)
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
	
	sure_fg = np.uint8(sure_fg)
	unknown = cv2.subtract(sure_bg, sure_fg)
	
	ret, markers = cv2.connectedComponents(sure_fg)
	
	markers = markers + 1
	
	markers[unknown == 255] = 0
	markers = cv2.watershed(a, markers)
	
	detect = [0, 0]
	for i in range(0, markers.max() + 1):
		j = np.zeros((c, b), np.uint8)
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


if __name__ == '__main__':
	print "main"
