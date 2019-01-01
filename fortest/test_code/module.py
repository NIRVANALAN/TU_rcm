# -*- coding:UTF-8 -*-
from math import *
from operator import itemgetter
import sys
import os
from adjust import *
import xlwt
import xlrd
from xlutils.copy import copy
from xlwt import Style

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


def write_file(list_for_write, filename):
	with open(filename, 'w') as f:
		f.write(str(list_for_write))


def read_file(filename, print_file=False):
	list_data = []
	with open(filename, 'r') as f:
		list_data = f.read()
	if print_file:
		print list_data
	return eval(list_data)


row_num = 1

mask_name = ['Endocardium', 'Midcardium', 'Epicardium', 'Heart_trabe', 'Whole']


def write_excel(file_name, data, patient_no, slide_no):
	global row_num
	rb = xlrd.open_workbook(file_name, formatting_info=False)
	wb = copy(rb)
	ws = wb.get_sheet(0)
	# ws.write(row, col, str, styl)
	# ws.write(row_num, 0, patient_no)
	# ws.write(row_num, 1, slide_no)
	# this circulation writes 4(or less) mask information
	for i, slide_data in enumerate(data):  # every mask
		# 		# 	continue
		# 		# if (slide_no is 4 or slide_no is 5) and i is 2:
		# 		# 	row_num += 1
		# 		# 	continue
		# 		# 	row_num += 1
		if slide_no is 3 and i is 3:
			i += 1
		if (slide_no is 4 or slide_no is 5) and (i is 2 or i is 3):
			i += 1
		ws.write(row_num, 0, patient_no)
		ws.write(row_num, 1, slide_no)
		ws.write(row_num, 2, mask_name[i])
		for j, slide_detail in enumerate(slide_data):
			ws.write(row_num, j + 3, slide_detail)
		row_num += 1
	wb.save(file_name)


def fibrosis(slide, fibrosislevel):
	working_dimensions = slide.level_dimensions[fibrosislevel]
	img = np.array(slide.read_region((0, 0), fibrosislevel, working_dimensions))
	rr, gg, bb, aa = cv2.split(img)
	rgb_img = cv2.merge((bb, gg, rr))
	hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
	hsv_fibrosis = cv2.inRange(hsv, (90, 20, 20), (140, 255, 255))
	return hsv_fibrosis


'''
-1/2/3是一共四层（包含肌小梁）；-4分3层（忽略肌小梁）；-5/6分3层（含1层肌小梁）
'''


def edit_area(level, slide, he_erosion_iteration_time_list=[], masson_erosion_iteration_time_list=[], slide_no=0,
              is_masson=False, patient_id=0, show_img=False):
	if is_masson is True:
		print 'edit MASSON'
	else:
		print "called editHE"
	# n = 21
	print level
	working_dimensions = slide.level_dimensions[level]
	print working_dimensions
	img = np.array(slide.read_region((0, 0), level, working_dimensions))
	# cv2.imshow('img', img)
	b, g, r, a = cv2.split(img)
	rgbimg = cv2.merge((r, g, b))
	hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
	# cv2.imshow("rgb_img", rgbimg)
	if is_masson is True:
		grey_img = cv2.inRange(hsv, (0, 20, 0), (180, 255, 180))
		fibrosis_img = cv2.inRange(hsv, (90, 20, 0), (140, 255, 255))  # can be returned
	# cv2.imshow("fibrosis", fibrosis_img)
	else:
		grey_img = cv2.inRange(hsv, (0, 20, 0), (180, 255, 220))
	average_greyimg = cv2.blur(grey_img, (30, 30))
	# cv2.imshow('average grey img', averagegreyimg)
	# cv2.imwrite("test_images/HE/average_grey_img.jpg", averagegreyimg)
	
	ret, erode = cv2.threshold(average_greyimg, 120, 255, cv2.THRESH_BINARY)
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
	if is_masson is True and slide_no is not 3:
		masson_erosion_iteration_time = masson_erosion_iteration_time_list[slide_no]
		erode = cv2.erode(erode, kernel, iterations=masson_erosion_iteration_time)
	elif slide_no is not 3:
		# slide 04 do not need to ...
		he_erosion_iteration_time = he_erosion_iteration_time_list[slide_no]
		erode = cv2.erode(erode, kernel, iterations=he_erosion_iteration_time)
		pass
	if show_img:
		cv2.imshow("after erosion", erode)
	# cv2.imwrite("test_images/HE/after_erosion.jpg", erode)
	
	# cv2.imshow("")
	#  多次腐蚀，除去小梁
	
	ret, aver_image = cv2.threshold(average_greyimg, 120, 255, cv2.THRESH_BINARY)
	aver_image, avercnts, averhierarchy = cv2.findContours(aver_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# cv2.imshow("aver image", aver_image)
	
	# 得到整体的边界
	
	image, cnts, hierarchy = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# cv2.imshow("contour after erosion", erode)
	# 腐蚀后的边界
	
	object = []
	max_area = 0
	max_area_index = None
	
	for cnt in cnts:
		area = cv2.contourArea(cnt)
		if area > 100:
			points_wall = []
			for i in cnt:
				x = i[0][0]
				y = i[0][1]
				points_wall.append([x, y])
			i = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
			cv2.fillPoly(i, np.array([points_wall], np.int32), 255)
			object.append(i)
			if area > max_area:
				max_area = area
				max_area_index = len(object) - 1
	wall = object[max_area_index]
	# 把每一个区域都分割出来，最大的心肌壁
	
	other = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
	for i in range(0, len(object)):
		if i != max_area_index:
			other = cv2.add(other, object[i])
	
	# 通过矩moments计算重心
	M1 = cv2.moments(wall)
	cx1 = int(M1["m10"] / M1["m00"])
	cy1 = int(M1["m01"] / M1["m00"])
	
	M0 = cv2.moments(other)
	cx0 = int((M0["m10"]) / (M0["m00"]))
	cy0 = int((M0["m01"]) / (M0["m00"]))
	# base angle is like: other->left wall->right x0<x1 y0==y1 attention: The origin point of opencv is at top left corner
	if cx0 - cx1 == 0:
		if cy0 - cy1 > 0:
			base_angle = 90
		else:
			base_angle = -90
	else:
		if cx0 - cx1 > 0:
			base_angle = 180 * math.atan(-(cy0 - cy1) / (cx0 - cx1)) / math.pi
		else:
			base_angle = 180 + 180 * math.atan(-(cy0 - cy1) / (cx0 - cx1)) / math.pi
	
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
	wall = cv2.dilate(wall, kernel, iterations=15)
	other = cv2.dilate(other, kernel, iterations=15)
	if show_img:
		cv2.imshow("wall", wall)
		cv2.imshow("other", other)
	
	image, contours, hierarchy = cv2.findContours(wall, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	image1, contours1, hierarchy1 = cv2.findContours(other, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	points_wall = cv2.approxPolyDP(contours[0], 15, True)
	# 主要功能是把一个连续光滑曲线折线化，对图像轮廓点进行多边形拟合。
	points_other = []
	for i in contours1:  # contours1 : other
		for j in i:
			points_other.append(j)
	points_other = np.array(points_other)
	
	rect_wall = cv2.minAreaRect(points_wall)
	rect_other = cv2.minAreaRect(points_other)
	rect_all = cv2.minAreaRect(np.concatenate([points_wall, points_other]))  # 整体的最小外接矩形，包括心肌壁和小梁
	# 最小外切矩形 （中心(x,y), (宽,高), 旋转角度）
	box_wall = cv2.boxPoints(rect_wall)
	# box_wall = np.int0(box_wall)
	box_other = cv2.boxPoints(rect_other)
	# box_other = np.int0(box_other)
	# 快速排斥实验 判断两条线段是不是相交，相交的话交点所在的边就是内膜
	# 这个办法没用上。。。
	'''
	max(C.x,D.x)<min(A.x,B.x) || max(C.y,D.y)<min(A.y,B.y) ||
	max(A.x,B.x)<min(C.x,D.x) || max(A.y,B.y)<min(C.y,C.y)
	'''
	# for i in range(len(box_wall)):
	# 	if max(cx0, cx1) < min(box_wall[i][0], box_wall[(i + 1) % len(box_wall)][0]) \
	# 			or max(cy0, cy1) < min(box_wall[i][1], box_wall[(i + 1) % len(box_wall)][1]) \
	# 			or max(box_wall[i][0], box_wall[(i + 1) % len(box_wall)][0]) < min(cx0, cx1) \
	# 			or max(box_wall[i][1], box_wall[(i + 1) % len(box_wall)][1]) < min(cy0, cy1):
	# 		continue
	# 	else:
	# 		endocardium_pts = [[box_wall[i][0], box_wall[i][1]],
	# 		                   [box_wall[(i + 1) % len(box_wall)][0], box_wall[(i + 1) % len(box_wall)][1]]]
	# 		break
	
	rect_wall = (rect_wall[0], rect_wall[1], -rect_wall[2])  # minAreaRect 旋转角度小于0
	# get the width & height and compute the height of 'other'
	# if slide_no is 1:
	# 	other_height = rect_other[1]
	if (math.fabs(rect_wall[2] - base_angle) % 360) < 180 * atan(rect_wall[1][1] / rect_wall[1][0]) / math.pi or (
			math.fabs(rect_wall[2] - base_angle) % 360) > 180 - 180 * atan(rect_wall[1][1] / rect_wall[1][0]) / math.pi:
		angle = math.fabs(rect_wall[2] - 90)
		wall_width = rect_wall[1][1]
		wall_height = rect_wall[1][0]
		# all_width = rect_all[1][1]
		all_height = rect_all[1][0]
		other_height = all_height - wall_height
	
	else:
		angle = rect_wall[2]
		wall_width = rect_wall[1][0]
		wall_height = rect_wall[1][1]
		# all_width = rect_all[1][0]
		all_height = rect_all[1][1]
		other_height = all_height - wall_height
	rcm_thickening = [other_height if (slide_no is 1 > 0 and other_height) else min(rect_other[1])]
	points_wall = rotate_points(points_wall, rect_wall[0], -angle)
	# rotate the point matrix, base_angle after rotation should be 0
	for i in avercnts:
		averpoints = rotate_points(i, rect_wall[0], -angle)
	
	width_points = [[], []]
	for i in range(0, len(points_wall)):
		if points_wall[i][0][1] - rect_wall[0][1] > wall_height / 6:
			width_points[0].append(points_wall[i])
		else:
			if points_wall[i][0][1] - rect_wall[0][1] < -wall_height / 6:
				width_points[1].append(points_wall[i])
	
	height_points = [[], []]
	for i in xrange(0, len(points_wall)):
		if points_wall[i][0][0] - rect_wall[0][0] > wall_width / 4:
			height_points[0].append(points_wall[i])
		else:
			if points_wall[i][0][0] - rect_wall[0][0] < -wall_width / 4:
				height_points[1].append(points_wall[i])
	
	avery0 = 0
	for i in range(0, len(width_points[0])):
		avery0 += width_points[0][i][0][1]  # y on base width
	avery0 = avery0 / len(width_points[0])
	avery1 = 0
	for i in range(0, len(width_points[1])):
		avery1 += width_points[1][i][0][1]
	avery1 = avery1 / len(width_points[1])  # y on up width
	
	if (base_angle % 360) < 180:
		if avery1 < avery0:
			# abc = width_points[0]
			# width_points[0] = width_points[1]
			# width_points[1] = abc
			width_points[0], width_points[1] = width_points[1], width_points[0]
	else:
		if avery1 > avery0:
			# abc = width_points[0]
			# width_points[0] = width_points[1]
			# width_points[1] = abc
			width_points[0], width_points[1] = width_points[1], width_points[0]
	origin_width_points = []
	'''
	貌似是找外模和内膜的线的
	因为腐蚀加膨胀
	不再是原来的边界了
	现在通过找最近的方式
	用原来的边界来替换
	下面代码：
	'''
	for i in avercnts:
		for j in i:
			distance0 = 100000
			for k in width_points[0]:
				distance = math.sqrt(
					(j[0][0] - k[0][0]) * (j[0][0] - k[0][0]) + (j[0][1] - k[0][1]) * (j[0][1] - k[0][1]))
				if distance < distance0:
					distance0 = distance
			distance1 = 100000
			for k in width_points[1]:
				distance = math.sqrt(
					(j[0][0] - k[0][0]) * (j[0][0] - k[0][0]) + (j[0][1] - k[0][1]) * (j[0][1] - k[0][1]))
				if distance < distance1:
					distance1 = distance
			if distance1 < distance0 / 2:
				origin_width_points.append(j)
	
	width_points[1] = origin_width_points  # update with origin width points [1]这里是外膜
	
	origin_height_points = []
	for i in avercnts:
		for j in i:
			distance0 = 100000
			for k in height_points[0]:
				distance = math.sqrt(
					(j[0][0] - k[0][0]) * (j[0][0] - k[0][0]) + (j[0][1] - k[0][1]) * (j[0][1] - k[0][1]))
				if distance < distance0:
					distance0 = distance
			distance1 = 100000
			for k in height_points[1]:
				distance = math.sqrt(
					(j[0][0] - k[0][0]) * (j[0][0] - k[0][0]) + (j[0][1] - k[0][1]) * (j[0][1] - k[0][1]))
				if distance < distance1:
					distance1 = distance
			if distance1 < distance0 / 2:
				origin_height_points.append(j)
	height_points[1] = origin_height_points
	
	# sort 保证是从左到右的线
	for i in xrange(0, len(width_points[0])):
		width_points[0][i] = [width_points[0][i][0][0], width_points[0][i][0][1]]
	for i in xrange(0, len(width_points[1])):
		width_points[1][i] = [width_points[1][i][0][0], width_points[1][i][0][1]]
	width_points[0].sort()
	width_points[1].sort()
	for i in xrange(0, len(width_points[0])):
		width_points[0][i] = [[width_points[0][i][0], width_points[0][i][1]]]
	for i in xrange(0, len(width_points[1])):
		width_points[1][i] = [[width_points[1][i][0], width_points[1][i][1]]]
	
	for i in xrange(0, len(height_points[0])):
		height_points[0][i] = [height_points[0][i][0][0], height_points[0][i][0][1]]
	for i in xrange(0, len(height_points[1])):
		height_points[1][i] = [height_points[1][i][0][0], height_points[1][i][0][1]]
	height_points[0].sort()
	height_points[1].sort()
	for i in xrange(0, len(height_points[0])):
		height_points[0][i] = [[height_points[0][i][0], height_points[0][i][1]]]
	for i in xrange(0, len(height_points[1])):
		height_points[1][i] = [[height_points[1][i][0], height_points[1][i][1]]]
	
	# m+n
	x_list = []
	for i in width_points[0]:
		x_list.append((i[0][0], i[0][1], 0))
	for i in width_points[1]:
		x_list.append((i[0][0], i[0][1], 1))
	x_list.sort(key=itemgetter(0))
	
	y_list = []
	for i in height_points[0]:
		y_list.append((i[0][0], i[0][1], 0))
	for i in height_points[1]:
		y_list.append((i[0][0], i[0][1], 1))
	y_list.sort(key=itemgetter(1))
	
	# 几等分线
	cutting_line_points = [[], []]
	y_average_list = []
	for i in range(0, len(x_list)):
		pl = i - 1
		pr = i + 1
		if x_list[i][2] == 0:  # 内膜
			n = 0
			m = 1
		else:  # 外膜
			n = 1
			m = 0
		# while找到最近的对侧的膜上的点，同侧就略过
		while pl >= 0 and x_list[pl][2] == x_list[i][2]:
			pl = pl - 1
		while pr < len(x_list) and x_list[pr][2] == x_list[i][2]:
			pr = pr + 1
		# one cutting line for slide_no 4
		# 以下，通过线性回归找到对边的对应位置的y。两个距离可以用来估计心肌壁厚度
		if pl >= 0 and pr < len(x_list):
			y = (x_list[pl][1]) * (x_list[pr][0] - x_list[i][0]) / (x_list[pr][0] - x_list[pl][0]) + (x_list[pr][1]) * (
					x_list[i][0] - x_list[pl][0]) / (x_list[pr][0] - x_list[pl][0])
			if slide_no != 4 and slide_no != 5:
				cutting_line_points[n].append([[int(x_list[i][0]), int((x_list[i][1] - y) / 3 + y)]])
				cutting_line_points[m].append([[int(x_list[i][0]), int((x_list[i][1] - y) * 2 / 3 + y)]])
			else:
				cutting_line_points[n].append([[int(x_list[i][0]), int((x_list[i][1] - y) / 2 + y)]])
			y_average_list.append(x_list[i][1] - y)
		elif pl < 0:
			if slide_no != 4 and slide_no != 5:
				cutting_line_points[n].append(
					[[int(x_list[i][0]), int((x_list[i][1] - x_list[pr][1]) / 3 + x_list[pr][1])]])
				cutting_line_points[m].append(
					[[int(x_list[i][0]), int((x_list[i][1] - x_list[pr][1]) * 2 / 3 + x_list[pr][1])]])
			else:
				cutting_line_points[n].append(
					[[int(x_list[i][0]), int((x_list[i][1] - x_list[pr][1]) / 2 + x_list[pr][1])]])
			y_average_list.append(x_list[i][1] - x_list[pr][1])
		else:
			if slide_no != 4 and slide_no != 5:
				cutting_line_points[n].append(
					[[int(x_list[i][0]), int((x_list[i][1] - x_list[pl][1]) / 3 + x_list[pl][1])]])
				cutting_line_points[m].append(
					[[int(x_list[i][0]), int((x_list[i][1] - x_list[pl][1]) * 2 / 3 + x_list[pl][1])]])
			else:
				cutting_line_points[n].append(
					[[int(x_list[i][0]), int((x_list[i][1] - x_list[pl][1]) / 2 + x_list[pl][1])]])
			y_average_list.append(x_list[i][1] - x_list[pl][1])
		rcm_thickening.append(np.average(y_average_list))
	#  旋转回去
	width_points[0] = rotate_points(width_points[0], rect_wall[0], angle)
	width_points[1] = rotate_points(width_points[1], rect_wall[0], angle)
	cutting_line_points[0] = rotate_points(cutting_line_points[0], rect_wall[0], angle)
	cutting_line_points[1] = rotate_points(cutting_line_points[1], rect_wall[0], angle)
	
	# height_line_points = [[], []]
	# for i in range(0, len(y_list)):
	# 	pl = i - 1
	# 	pr = i + 1
	# 	if y_list[i][2] == 0:  # 一侧
	# 		n = 0
	# 		m = 1
	# 	else:  # 另一侧
	# 		n = 1
	# 		m = 0
	# 	# while找到最近的对侧的膜上的点，同侧就略过
	# 	while pl >= 0 and y_list[pl][2] == y_list[i][2]:
	# 		pl = pl - 1
	# 	while pr < len(y_list) and y_list[pr][2] == y_list[i][2]:
	# 		pr = pr + 1
	# one cutting line for slide_no 4
	# 	x_average_list = []  # useless...
	# 	if pl >= 0 and pr < len(y_list):
	# 		x = (y_list[pl][0]) * (y_list[pr][1] - y_list[i][1]) / (y_list[pr][1] - y_list[pl][1]) + (y_list[pr][0]) * (
	# 				y_list[i][1] - y_list[pl][1]) / (y_list[pr][1] - y_list[pl][1])
	# 		height_line_points[n].append([[int((y_list[i][0] - x) / 3 + x), int(y_list[i][1])]])
	# 		height_line_points[m].append([[int((y_list[i][0] - x) * 2 / 3 + x), int(y_list[i][1])]])
	# 		x_average_list.append(int(math.fabs(y_list[i][0] - x)))
	# 	elif pl < 0:
	# 		height_line_points[n].append(
	# 			[[int((y_list[i][0] - y_list[pr][0]) / 3 + y_list[pr][0]), int(y_list[i][1])]])
	# 		height_line_points[m].append(
	# 			[[int((y_list[i][0] - y_list[pr][0]) * 2 / 3 + y_list[pr][0]), int(y_list[i][1])]])
	# 		x_average_list.append(int(math.fabs(y_list[i][0] - y_list[pr][0])))
	# 	else:
	# 		height_line_points[n].append(
	# 			[[int((y_list[i][0] - y_list[pl][0]) / 3 + y_list[pl][0]), int(y_list[i][1])]])
	# 		height_line_points[m].append(
	# 			[[int((y_list[i][0] - y_list[pl][0]) * 2 / 3 + y_list[pl][0]), int(y_list[i][1])]])
	# 		x_average_list.append(int(math.fabs(y_list[i][0] - y_list[pl][0])))
	# height_points[0] = rotate_points(height_points[0], rect_wall[0], angle)
	# height_points[1] = rotate_points(height_points[1], rect_wall[0], angle)
	# height_line_points[0] = rotate_points(height_line_points[0], rect_wall[0], angle)
	# height_line_points[1] = rotate_points(height_line_points[1], rect_wall[0], angle)
	# update rcm_thickening
	# rcm_thickening = np.average(y_average_list)
	m = cv2.moments(np.array(width_points[1]))
	cx1 = int(m["m10"] / m["m00"])
	cy1 = int(m["m01"] / m["m00"])
	cutting_line_points[1].reverse()
	width_points[1].reverse()
	#######################################
	if slide_no != 4 and slide_no != 5:
		first = width_points[0] + cutting_line_points[1]
		second = cutting_line_points[0] + cutting_line_points[1]
		third = cutting_line_points[0] + width_points[1]
	else:
		first = width_points[0] + cutting_line_points[0]
		second = cutting_line_points[0] + width_points[1]
		third = []
	#######################################
	# draw the segmentation lines
	first_pts = np.array([cutting_line_points[0]], np.int32)
	second_pts = np.array([cutting_line_points[1]], np.int32)
	first_pts.reshape(-1, 1, 2)
	second_pts.reshape(-1, 1, 2)
	
	cv2.polylines(rgbimg, first_pts, False, (0, 0, 255), 6)
	if slide_no != 4 and slide_no != 5:
		cv2.polylines(rgbimg, second_pts, False, (0, 255, 0), 6)
	
	# height_line_points[1].reverse()
	# height_points[1].reverse()
	# draw height measure line : unnecessary
	# height_first_pts = np.array([height_line_points[0]], np.int32)
	# height_second_pts = np.array([height_line_points[1]], np.int32)
	# height_first_pts.reshape(-1, 1, 2)
	# height_second_pts.reshape(-1, 1, 2)
	# cv2.polylines(rgbimg, height_first_pts, False, (255, 0, 0), 5)
	# cv2.polylines(rgbimg, height_second_pts, False, (255, 0, 0), 5)
	if not os.path.exists("HE_image"):
		os.mkdir("HE_image")
	if not os.path.exists("MASSON_image"):
		os.mkdir("MASSON_image")
	img_name = ('HE_image/HE_' + str(patient_id) + '_' + str(slide_no) + '.jpg' if (is_masson is False)
	            else 'MASSON_image/Masson_' +
	                 str(patient_id) + '_' + str(slide_no) + '.jpg')
	cv2.imwrite(img_name, rgbimg)  # save the img of segmentation result
	#################################################
	i = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
	firstmask = cv2.fillPoly(i, np.array([first], np.int32), 255)  # fillPoly()对于限定轮廓的区域进行填充
	
	# print firstmask[363][154]
	
	i = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
	secondmask = cv2.fillPoly(i, np.array([second], np.int32), 255)
	if show_img:
		cv2.imshow(img_name, rgbimg)  # save the img of segmentation result
		cv2.imshow("firstmask", firstmask)
		cv2.imshow("secondmask", secondmask)
	thirdmask = []
	if slide_no != 4 and slide_no != 5:
		i = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
		thirdmask = cv2.fillPoly(i, np.array([third], np.int32), 255)
	# firstdensity = areaaveragedensity(fibrosis, grey_img, firstmask)
	# seconddensity = areaaveragedensity(fibrosis, grey_img, secondmask)
	# thirddensity = areaaveragedensity(fibrosis, grey_img, thirdmask)
	
	box1 = cv2.boxPoints(rect_other)
	box1 = np.array(box1)
	for i in range(0, 2):
		max_area_index = sqrt((box1[i][0] - cx1) * (box1[i][0] - cx1) + (box1[i][1] - cy1) * (box1[i][1] - cy1))
		n = i
		for j in range(i, 4):
			if sqrt((box1[j][0] - cx1) * (box1[j][0] - cx1) + (box1[j][1] - cy1) * (box1[j][1] - cy1)) > max_area_index:
				max_area_index = sqrt((box1[j][0] - cx1) * (box1[j][0] - cx1) + (box1[j][1] - cy1) * (box1[j][1] - cy1))
				n = j
		k = (box1[i][0], box1[i][1])
		box1[i] = box1[n]
		box1[n] = [k[0], k[1]]
	
	# firstarea = 'Endocardium'
	# thirdarea = 'Epicardium'
	othermask = []
	if slide_no != 3:
		other_line = width_points[0]
		
		if sqrt((box1[0][0] - other_line[0][0][0]) * (box1[0][0] - other_line[0][0][0]) + (
				box1[0][1] - other_line[0][0][1]) * (box1[0][1] - other_line[0][0][1])) > sqrt(
			(box1[1][0] - other_line[0][0][0]) * (box1[1][0] - other_line[0][0][0]) + (
					box1[1][1] - other_line[0][0][1]) * (box1[1][1] - other_line[0][0][1])):
			other_line.append([[box1[0][0], box1[0][1]]])
			other_line.append([[box1[1][0], box1[1][1]]])
		else:
			other_line.append([[box1[1][0], box1[1][1]]])
			other_line.append([[box1[0][0], box1[0][1]]])
		
		i = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
		othermask = cv2.fillPoly(i, np.array([other_line], np.int32), 255)
	# otherdensity = areaaveragedensity(fibrosis, grey_img, othermask)
	if is_masson is True:
		return firstmask, secondmask, thirdmask, othermask, grey_img, hsv, fibrosis_img, rcm_thickening  # [other_height, wall_height]
	else:
		return firstmask, secondmask, thirdmask, othermask, rcm_thickening


def detectprocess(a, hsv):
	b = len(hsv[0])
	c = len(hsv)
	h, s, v = cv2.split(hsv)
	h = cv2.subtract(180, h)
	ret, s = cv2.threshold(s, 20, 255, cv2.THRESH_BINARY_INV)
	gray = cv2.addWeighted(s, -1, h, 1, 0)  # why?
	# cv2.imshow("gray", gray)
	whole_area_space = cv2.countNonZero(gray)
	# print 'myocardium space in this region: ', whole_area_space
	kernel = np.ones((3, 3), np.uint8)
	
	ret, nuclear0 = cv2.threshold(gray, 35, 255, cv2.THRESH_BINARY)
	# cv2.imshow("nuclear", nuclear0)
	
	nuclear0 = cv2.morphologyEx(nuclear0, cv2.MORPH_OPEN, kernel, iterations=2)
	# cv2.imshow("nuclear0", nuclear0)
	sure_bg = cv2.dilate(nuclear0, kernel, iterations=3)
	# cv2.imshow("sure_bg",sure_bg)
	ret, nuclear1 = cv2.threshold(gray, 35, 255, cv2.THRESH_BINARY)
	
	for i in range(0, len(nuclear1[0])):
		nuclear1[0][i] = 0
	
	# cv2.imshow("nuclear1", nuclear1)
	mask = np.zeros((c + 2, b + 2), np.uint8)
	cv2.floodFill(nuclear1, mask, (0, 0), 100)
	nuclear1[nuclear1 == 0] = 255
	nuclear1[nuclear1 == 100] = 0
	
	dist_transform = cv2.distanceTransform(nuclear1, cv2.DIST_L2, 5)
	dist_transform = np.uint8(dist_transform)
	ret, out = cv2.threshold(dist_transform, 5, 255, cv2.THRESH_BINARY_INV)
	# cv2.imshow('out', out)
	nuclear1 = 255 - nuclear1
	gray1 = cv2.subtract(gray, nuclear1)
	# cv2.imshow("gray1", gray1)  # 去掉细胞质，得到细胞的图像
	gray1 = cv2.blur(gray1, (5, 5))
	
	dist_transform = cv2.addWeighted(dist_transform, 1, gray1, 0.1, 0)
	# cv2.imshow("dist_transform", dist_transform)
	max = cv2.dilate(dist_transform, kernel, iterations=10)
	# max = cv2.multiply(max, 0.75)
	max = cv2.multiply(max, 0.90)
	sure_fg = cv2.subtract(dist_transform, max)
	sure_fg = cv2.subtract(sure_fg, out)
	# cv2.imshow('sure_fg', sure_fg)
	ret, sure_fg = cv2.threshold(sure_fg, 0, 255, cv2.THRESH_BINARY)
	# sure_fg ?
	sure_fg = np.uint8(sure_fg)
	unknown = cv2.subtract(sure_bg, sure_fg)
	
	ret, markers = cv2.connectedComponents(sure_fg)
	
	markers = markers + 1
	
	markers[unknown == 255] = 0
	markers = cv2.watershed(a, markers)
	# cv2.imshow('origin', a)
	# a[markers == 89] = [0, 0, 255]
	#
	#  307 need segmentation
	# cv2.imshow('watershed', a)
	# step 11 get nuclear
	nuclear_area_space = []
	non_nuclear_area_space = []
	# detect = [0, 0]
	detect = [0, 0, 0]
	for i in range(2, markers.max() + 1):
		j = np.zeros((c, b), np.uint8)
		# print 'j.size:', j.size
		j[markers == i] = 255  # why?
		area = cv2.countNonZero(j)
		# if area > 361:
		if area > 321:  # 心肌细胞核比较大
			# get arc
			_, contours, hierarchy = cv2.findContours(j, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
			cnt = contours[0]
			perimeter = cv2.arcLength(cnt, True)
			nuclear_area_space.append([i, area, perimeter])
			detect[1] += 1
			if area >= 1334:  # 有可能将两个细胞核识别成一个，这里用一个简单的阈值进行处理
				detect[1] += 1
			jd = cv2.dilate(j, kernel, iterations=2)
			image, lines, hier = cv2.findContours(jd, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
			white = 0
			total = 0
			for k in lines[0]:  # why lines[0]?
				total = total + 1
				if hsv[k[0][1]][k[0][0]][1] < 80:  # 空泡的hsv阈值
					white = white + 1
			if white > total / 2:  # 只有当边缘白色大于一定程度的时候，才计算为空泡
				non_nuclear_area_space.append([i, white])
				detect[0] = detect[0] + 1
		else:
			detect[2] += 1  # 其余非心肌细胞核
	#  返回值空泡 心肌 非心肌 总面积 心肌细胞的面积和周长列表
	return detect[0], detect[1], detect[2], whole_area_space, [i[1:] for i in nuclear_area_space], \
	       [i[1:] for i in non_nuclear_area_space]


def masson_region_slide(slide, working_level, threshold=(), start_pos=(0, 0), is_debug=False, dimension=(500, 500)):
	working_dimensions = slide.level_dimensions[working_level]
	if is_debug is True:
		img = np.array(slide.read_region(start_pos, working_level, working_dimensions))
	else:
		img = np.array(slide.read_region(start_pos, working_level, dimension))
	rr, gg, bb, aa = cv2.split(img)
	bgr_cv_img = cv2.merge((bb, gg, rr))
	cv2.imshow('bgr_img', bgr_cv_img)
	hsv = cv2.cvtColor(bgr_cv_img, cv2.COLOR_BGR2HSV)
	# (155, 140, 50), (175, 180, 255) cardiac
	# (90, 20, 20), (140, 255, 255) fibrosis
	hsv = cv2.inRange(hsv, threshold[0], threshold[1])  # s 50-250 in paper
	region_area = cv2.countNonZero(hsv)
	cv2.imshow('hsv_cardiac_cell', hsv)
	return hsv, region_area
	pass


def fibrosis_slide(slide, fibrosislevel, start_pos=(0, 0), is_debug=False, dimension=(1000, 1000)):
	workingDimensions = slide.level_dimensions[fibrosislevel]
	if is_debug is False:
		img = np.array(slide.read_region(start_pos, fibrosislevel, workingDimensions))
	else:
		img = np.array(slide.read_region(start_pos, 0, dimension))
	rr, gg, bb, aa = cv2.split(img)
	bgr_cv_img = cv2.merge((bb, gg, rr))
	cv2.imshow('bgr_img', bgr_cv_img)
	hsv = cv2.cvtColor(bgr_cv_img, cv2.COLOR_BGR2HSV)
	hsv = cv2.inRange(hsv, (90, 20, 20), (140, 255, 255))  # s 50-250 in paper
	return hsv


def cardiac_cell_slide(slide, working_level, start_pos=(0, 0), is_debug=False, dimension=(1000, 1000)):
	working_dimensions = slide.level_dimensions[working_level]
	if is_debug is False:
		img = np.array(slide.read_region(start_pos, working_level, working_dimensions))
	else:
		img = np.array(slide.read_region(start_pos, working_level, dimension))
	rr, gg, bb, aa = cv2.split(img)
	bgr_cv_img = cv2.merge((bb, gg, rr))
	cv2.imshow('bgr_img', bgr_cv_img)
	hsv = cv2.cvtColor(bgr_cv_img, cv2.COLOR_BGR2HSV)
	hsv = cv2.inRange(hsv, (155, 140, 50), (175, 230, 255))  # s 50-250 in paper
	cv2.imshow('hsv_cardiac_cell', hsv)
	return hsv


if __name__ == '__main__':
	print "main"
