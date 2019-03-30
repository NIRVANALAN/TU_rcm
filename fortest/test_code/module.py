# -*- coding:UTF-8 -*-
from math import *
from operator import itemgetter
import os
from adjust import *
import xlwt
import xlrd
from xlutils.copy import copy
from xlwt import Style
import matplotlib.pyplot as plt

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

he_patients = []
masson_patients = []
# patient_id = 1
img_dir = './../../rcm_images/'
# he patients
he_filename = os.listdir(img_dir + '/HE')
he_filename.sort(key=lambda x: int(x[:-1]))
for i in he_filename:
	he_patients.append('/' + i)
	pass
masson_filename = os.listdir(img_dir + '/MASSON')
masson_filename.sort(key=lambda x: int(x[:-1]))
for i in masson_filename:
	masson_patients.append('/' + i)
	pass


def distance_between_point_line(line, point):
	"""
	:param line: np.array(vx,vy,x,y) line[0][0] line[1][0] ...
	:param point: np.array([x,y]) x-> point[0] y->point[1]
	:return: distance(int)
	"""
	point_on_line = (point[0], (point[0] - line[2][0]) * line[1][0] / line[0][0] + line[3][0])
	dist = (point_on_line[0] - point[1]) * cos(math.atan(abs(line[1][0] / line[0][0])))
	dist = abs(dist)
	return dist


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


def get_row_num(slide_type="HE"):
	if slide_type is "MASSON":
		with open('Row_Num/masson_row_num.txt', 'r') as masson_row_file:
			return int(masson_row_file.read())
		pass
	else:
		with open('Row_Num/he_row_num.txt', 'r') as he_row_file:
			return int(he_row_file.read())
		pass


def save_row_num(row_no=row_num, slide_type="HE"):
	if slide_type is "MASSON":
		with open('Row_Num/masson_row_num.txt', 'w') as masson_row_file:
			masson_row_file.write(str(row_no))
		pass
	else:
		with open('Row_Num/he_row_num.txt', 'w') as he_row_file:
			he_row_file.write(str(row_no))
		pass


def write_excel(file_name, data, patient_no, slide_no, start_row=-1):
	global row_num
	rb = xlrd.open_workbook(file_name, formatting_info=False)
	wb = copy(rb)
	ws = wb.get_sheet(0)
	# ws.write(row, col, str, styl)
	# ws.write(row_num, 0, patient_no)
	# ws.write(row_num, 1, slide_no)
	# this circulation writes 4(or less) mask information
	if file_name[0] is "H":
		if start_row > 0:
			row_num = start_row
		elif row_num is 1:
			row_num = int(get_row_num("HE"))
		for i, slide_data in enumerate(data):  # every mask
			if slide_no is 3 and i is 3:
				i += 1
			if (slide_no is 4 or slide_no is 5) and (i is 2 or i is 3):
				i += 1
			ws.write(row_num, 0, patient_no)
			ws.write(row_num, 1, slide_no)
			ws.write(row_num, 2, mask_name[i])
			for j, slide_detail in enumerate(slide_data):
				ws.write(row_num, j + 3, slide_detail)
			row_num += 1  # prepare for the next time write
		wb.save(file_name)
		save_row_num(row_num, "HE")
	elif file_name[0] is "M":
		if start_row > 0:
			row_num = start_row
		elif row_num is 1:
			row_num = int(get_row_num("MASSON"))
		ws.write(row_num, 0, patient_no)
		ws.write(row_num, 1, slide_no)
		# ws.write(row_num, 2, mask_name[row_num])
		for i, slide_data in enumerate(data):
			ws.write(row_num, i + 2, slide_data)
		row_num += 1  # prepare for the next time write
		wb.save(file_name)
		save_row_num(row_num, "MASSON")
		pass


def fibrosis(slide, fibrosis_level):
	working_dimensions = slide.level_dimensions[fibrosis_level]
	img = np.array(slide.read_region((0, 0), fibrosis_level, working_dimensions))
	rr, gg, bb, aa = cv2.split(img)
	rgb_img = cv2.merge((bb, gg, rr))
	hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
	hsv_fibrosis = cv2.inRange(hsv, (90, 20, 20), (140, 255, 255))
	return hsv_fibrosis


def imgshow(img, read_from_cv=True, cmap=None):
	# b, g, r = cv.split(img)
	# he_image = cv.merge((r, g, b))
	if read_from_cv and cmap is None:
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	if cmap is not None:
		plt.imshow(img, cmap=cmap)
	else:
		plt.imshow(img)
	plt.show()


def hand_draw_split_test(level, threshes, image_path, slide, show_image=False):
	"""
	:param slide: the pathological slide
	:type threshes: ((),())
	:param level: level the slide will be working on
	:param threshes: (outer_thresh, inner_thresh)
	:param image_path:  specify the path to the image
	:param slide_path:  path to the slide
	:param show_image: denote whether to show the image
	:return: width_points, x_list
	"""
	# slide_he = openslide.open_slide('/home/zhourongchen/zrc/rcm/images/MASSON/30638/28330-.ndpi')
	he_image = cv2.imread(image_path)
	if show_image:
		imgshow(he_image)
	hsv = cv2.cvtColor(he_image, cv2.COLOR_BGR2HSV)
	# slide = openslide.open_slide(slide_path)
	# print he_slide.dimensions
	# level = 5
	origin_level = 6  # level of the hand_drawn slides
	slide_img = np.array(slide.read_region((0, 0), level, slide.level_dimensions[level]))
	print slide_img.shape
	slide_img = cv2.cvtColor(slide_img, cv2.COLOR_RGBA2BGR)
	width_points = [[], [], []]  # add BLUE line for trabe segmentation
	# colors = ((0, 0, 255), (0, 255, 0), (255, 0, 0))
	for t in threshes:
		mask = cv2.inRange(hsv, t[0], t[1])
		# mask = cv.inRange(hsv, np.array([170, 43, 43]), np.array([180, 255, 255]))
		# dst = cv.bitwise_and(he_image, he_image, mask=mask)
		# imgshow(dst)
		# get points on the contours
		_, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		if contours.__len__() is 0:  # now trabe line(blue)
			continue
		points = contours[0]
		for i in contours[1:]:
			if len(i) > 10:
				points = np.append(points, i, axis=0)
		points = np.unique(points, axis=0)  # get unique points
		# draw points in the original image
		points = np.array([points], np.int32)  # convert to np.int32 works well
		# sort by distance
		# dist = (points[0][-1][0][0] - points[0][0][0][0]) / 100
		# print dist
		# print points.size
		# sort by x
		# points = points[points[:, 0].argsort()]
		# draw_img0 = cv.drawContours(dst.copy(), contours, -1, (0, 255, 0), 3)
		# imgshow(dst)
		# print dst.shape
		points *= int(pow(2, origin_level - level))  # cvt points in different dimensions
		# if threshes.index(t) is 0:  # outer
		# 	# cv.polylines(dst, points, False, color=(0, 0, 255), thickness=4)
		# 	# cv2.polylines(slide_img, points, False, color=(0, 0, 255), thickness=5)
		# 	for p in points[0]:
		# 		width_points[0].append([[p[0][0], p[0][1]]])  # outer line
		# 	width_points[0].sort()
		# 	pass
		# else:  # inner
		# 	# cv.polylines(dst, points, False, color=(0, 255, 0), thickness=4)
		# 	# cv2.polylines(slide_img, points, False, color=(0, 255, 0), thickness=5)
		# 	for p in points[0]:
		# 		width_points[1].append([[p[0][0], p[0][1]]])  # inner line
		# 	width_points[1].sort()
		# 	pass
		index = threshes.index(t)
		for p in points[0]:
			width_points[index].append([[p[0][0], p[0][1]]])  # outer line
		width_points[index].sort()
		pass
	
	if show_image:
		imgshow(slide_img)
	# print he_slide.dimensions[0]/dst.shape[0]
	'''
	select some points
	'''
	percentage = 5
	smaller_index = 1 if width_points[0].__len__() > width_points[1].__len__() else 0
	num = int(width_points[smaller_index].__len__() / percentage)  # 1/percentage from original points
	arg0 = np.linspace(0, width_points[0].__len__(), num, endpoint=False, dtype=int)
	arg1 = np.linspace(0, width_points[1].__len__(), num, endpoint=False, dtype=int)
	width_points[0] = [width_points[0][i] for i in arg0]
	width_points[1] = [width_points[1][i] for i in arg1]
	'''
	fit line
	'''
	# (vx,vy,x,y)
	line_outer = cv2.fitLine(np.array(width_points[0]), cv2.DIST_L2, 0, 0.01, 0.01)
	k_outer = line_outer[1] / line_outer[0]
	line_inner = cv2.fitLine(np.array(width_points[1]), cv2.DIST_L2, 0, 0.01, 0.01)
	k_inner = line_inner[1] / line_inner[0]
	
	for outer_point in width_points[0]:
		length = line_outer[2] - outer_point[0][0]
		outer_point[0][1] = (line_outer[3] - k_outer * length).item()
		pass
	
	for inner_point in width_points[1]:
		length = line_outer[2] - inner_point[0][0]
		inner_point[0][1] = (line_inner[3] - k_inner * length).item()
		pass
	
	# length = 300
	# point_out = (line_outer[2] - length, line_outer[3] - k_outer * length), \
	#             (line_outer[2] + length, line_outer[3] + k_outer * length)
	# point_in = (line_inner[2] - length, line_inner[3] - k_inner * length), \
	#            (line_inner[2] + length, line_inner[3] + k_inner * length)
	'''
	m+n
	'''
	x_list = []
	for i in width_points:
		for j in i:
			x_list.append((j[0][0], j[0][1], width_points.index(i)))
	x_list.sort(key=itemgetter(0))
	return width_points, x_list
	pass


'''
-1/2/3是一共四层（包含肌小梁）；-4分3层（忽略肌小梁）；-5/6分3层（含1层肌小梁）
'''

'''
thresh for hand_drawn line extraction
'''
outer_thresh = (166, 43, 46), (180, 255, 255)  # RED
inner_thresh = (35, 43, 46), (77, 255, 255)  # GREEN
trabe_thresh = (100, 43, 46), (124, 255, 255)  # BLUE
thresh = (outer_thresh, inner_thresh, trabe_thresh)


def edit_area(level, slide, he_erosion_iteration_time_list=[], masson_erosion_iteration_time_list=[], slide_no=0,
              is_masson=False, patient_id=0, show_img=False, set_vertical=False, hand_drawn=False, image_path=None):
	calculate_trabe_flag = True
	if slide_no is 3:
		calculate_trabe_flag = False
	if is_masson is True:
		print 'edit MASSON'
	else:
		print "edit HE"
	# n = 21
	print 'level working on' + str(level)
	working_dimensions = slide.level_dimensions[level]
	print 'working dimension:' + str(working_dimensions)
	img = np.array(slide.read_region((0, 0), level, working_dimensions))
	# cv2.imshow('img', img)
	# b, g, r, a = cv2.split(img)
	# rgbimg = cv2.merge((r, g, b))
	rgbimg = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
	hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
	# cv2.imshow("rgb_img", rgbimg)
	
	'''
	convert hsv to grey image, get rid of white area
	'''
	if is_masson is True:
		grey_img = cv2.inRange(hsv, (0, 30, 0), (180, 255, 180))
	# fibrosis_img = cv2.inRange(hsv, (90, 20, 0), (140, 255, 255))  # can be returned
	# cv2.imshow("fibrosis", fibrosis_img)
	else:
		grey_img = cv2.inRange(hsv, (0, 30, 0), (180, 255, 220))
	
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
	g_img = grey_img.copy()
	g_img = cv2.adaptiveThreshold(g_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 5)
	g_img = cv2.morphologyEx(g_img, cv2.MORPH_CLOSE, kernel, iterations=3)
	g_img = cv2.morphologyEx(g_img, cv2.MORPH_OPEN, kernel, iterations=5)
	# imgshow(g_img, cmap='gray')
	average_greyimg = cv2.blur(grey_img, (30, 30))  # blur using filter
	# cv2.imshow('average grey img', averagegreyimg)
	# cv2.imwrite("test_images/HE/average_grey_img.jpg", averagegreyimg)
	rcm_thickening = [0]
	if not hand_drawn:
		'''
		erode grey image, iteration time is specified
		多次腐蚀，除去小梁
		'''
		ret, erode = cv2.threshold(average_greyimg, 120, 255, cv2.THRESH_BINARY)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
		if is_masson is True and calculate_trabe_flag:
			masson_erosion_iteration_time = masson_erosion_iteration_time_list[slide_no]
			erode = cv2.erode(erode, kernel, iterations=masson_erosion_iteration_time)
		elif calculate_trabe_flag:  # for HE
			# slide 04 do not need to ...
			he_erosion_iteration_time = he_erosion_iteration_time_list[slide_no]
			erode = cv2.erode(erode, kernel, iterations=he_erosion_iteration_time)
			pass
		if show_img:
			cv2.imshow("after erosion", erode)
		
		'''
		get boundary of whole and img_after_erosion
		'''
		ret, aver_image = cv2.threshold(average_greyimg, 120, 255, cv2.THRESH_BINARY)
		aver_image, avercnts, averhierarchy = cv2.findContours(aver_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		# cv2.imshow("aver image", aver_image)
		# 得到整体的边界
		image, cnts, hierarchy = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		# cv2.imshow("contour after erosion", erode)
		# 腐蚀后的边界
		
		rcm_object = []
		max_area = 0
		max_area_index = None
		'''
		get all objects in the contour, the largest is the wall
		'''
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
				rcm_object.append(i)
				if area > max_area:
					max_area = area
					max_area_index = len(rcm_object) - 1
		wall = rcm_object[max_area_index]
		# 把每一个区域都分割出来，最大的心肌壁
		
		'''
		get all other objects -> calculate trabe
		'''
		other = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
		for i in range(0, len(rcm_object)):
			if i != max_area_index:
				other = cv2.add(other, rcm_object[i])
		M0 = cv2.moments(other)
		if M0["m00"] == 0.0:
			calculate_trabe_flag = False  # no trabe
		# 对于计算小梁的slide, 通过矩moments计算重心
		
		'''
		calculate trabe position via angle
		'''
		if calculate_trabe_flag:  # 小梁的计算
			M1 = cv2.moments(wall)
			cx1 = int(M1["m10"] / M1["m00"])
			cy1 = int(M1["m01"] / M1["m00"])
			
			# M0 = cv2.moments(other)
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
		else:
			base_angle = 90  # default for slide03
		
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
		wall = cv2.dilate(wall, kernel, iterations=15)  # dilate wall
		'''
		find contours of other
		'''
		if calculate_trabe_flag:
			other = cv2.dilate(other, kernel, iterations=15)
			image1, contours_other, hierarchy1 = cv2.findContours(other, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		if show_img:
			cv2.imshow("wall", wall)
			cv2.imshow("other", other)
		
		image, contours_wall, hierarchy = cv2.findContours(wall, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		points_wall = cv2.approxPolyDP(contours_wall[0], 15, True)
		# 主要功能是把一个连续光滑曲线折线化，对图像轮廓点进行多边形拟合。
		
		'''
		get rect of other, wall and all
		'''
		if calculate_trabe_flag:
			points_other = []
			for i in contours_other:  # contours1 : other
				for j in i:
					points_other.append(j)
			points_other = np.array(points_other)
			rect_other = cv2.minAreaRect(points_other)
			box_other = cv2.boxPoints(rect_other)
			rect_all = cv2.minAreaRect(np.concatenate([points_wall, points_other]))  # 整体的最小外接矩形，包括心肌壁和小梁
		
		rect_wall = cv2.minAreaRect(points_wall)
		# 最小外切矩形 （中心(x,y), (宽,高), 旋转角度） angle -> [-90,0)
		box_wall = cv2.boxPoints(rect_wall)
		rect_wall = (rect_wall[0], rect_wall[1], -rect_wall[2])  # minAreaRect 旋转角度小于0
		# get the width & height and compute the height of 'other'
		# if slide_no is 1:
		# 	other_height = rect_other[1]
		'''
		start calculation
		'''
		if (slide_no is 3 and set_vertical is False) or \
				(calculate_trabe_flag and ((math.fabs(rect_wall[2] - base_angle) % 360) < 180 * atan(
					rect_wall[1][1] / rect_wall[1][0]) / math.pi or
				                           (math.fabs(rect_wall[2] - base_angle) % 360) > 180 - 180 * atan(
							rect_wall[1][1] / rect_wall[1][0]) / math.pi)):
			# print "mark horizontal"
			'''
			calculate wall/other's width and height
			'''
			angle = math.fabs(rect_wall[2] - 90)
			wall_width = rect_wall[1][1]
			wall_height = rect_wall[1][0]
			# all_width = rect_all[1][1]
			if calculate_trabe_flag:
				# 	all_height = wall_height
				# 	other_height = 0
				# else:
				all_height = rect_all[1][0]
				other_height = all_height - wall_height
		
		else:
			if slide_no is 3 and set_vertical:
				print "slide03 set vertical"
			angle = rect_wall[2]
			wall_width = rect_wall[1][0]
			wall_height = rect_wall[1][1]
			# all_width = rect_all[1][0]
			if calculate_trabe_flag:
				all_height = rect_all[1][1]
				other_height = all_height - wall_height
		'''
		get rcm_thickening[0] (trabe_height, wall_height)
		'''
		if calculate_trabe_flag:
			rcm_thickening[0] = other_height if (slide_no is 1 > 0 and other_height) else min(rect_other[1])
		else:
			pass
		# rcm_thickening.append(0)  # no trabe
		points_wall = rotate_points(points_wall, rect_wall[0], -angle)
		# rotate the point matrix, base_angle after rotation should be 0
		for i in avercnts:
			averpoints = rotate_points(i, rect_wall[0], -angle)
		'''
		get width_points and height_points
		'''
		width_points = [[], [], []]
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
		'''
		distinguish outer/inner via average y
		'''
		avery0 = 0
		for i in range(0, len(width_points[0])):
			avery0 += width_points[0][i][0][1]  # y on base width
		avery0 = avery0 / len(width_points[0])
		avery1 = 0
		for i in range(0, len(width_points[1])):
			avery1 += width_points[1][i][0][1]
		avery1 = avery1 / len(width_points[1])  # y on up width
		
		if calculate_trabe_flag:  # 这里代码计算内外膜，和slide03没关系
			if (base_angle % 360) < 180:
				if avery1 < avery0:
					# abc = width_points[0]
					# width_points[0] = width_points[1]
					# width_points[1] = abc
					width_points[0], width_points[1] = width_points[1], width_points[0]
			else:
				if avery1 > avery0:
					width_points[0], width_points[1] = width_points[1], width_points[0]
		
		'''
		貌似是找外模和内膜的线的
		因为腐蚀加膨胀
		不再是原来的边界了
		现在通过找最近的方式
		用原来的边界来替换
		下面代码：
		'''
		origin_width_points = []
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
		
		'''
		简化width_points，sort 保证是从左到右的线
		'''
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
	'''
	finish automatically segmentation calculation
	'''
	if hand_drawn:
		width_points, x_list = hand_draw_split_test(level=level, image_path=image_path, threshes=thresh, slide=slide)
		pass
	'''
	calculate cutting_line_points and rcm_thickening[1] via y_average
	'''
	cutting_line_points = [[], []]
	y_average_list = []
	'''
	rotate back points if not hand_drawn, and construct dividing lines
	'''
	if not hand_drawn:
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
				y = (x_list[pl][1]) * (x_list[pr][0] - x_list[i][0]) / (x_list[pr][0] - x_list[pl][0]) + (
					x_list[pr][1]) * (
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
		rcm_thickening.append(abs(np.average(y_average_list)))
		width_points[0] = rotate_points(width_points[0], rect_wall[0], angle)
		width_points[1] = rotate_points(width_points[1], rect_wall[0], angle)
		cutting_line_points[0] = rotate_points(cutting_line_points[0], rect_wall[0], angle)
		cutting_line_points[1] = rotate_points(cutting_line_points[1], rect_wall[0], angle)
		m = cv2.moments(np.array(width_points[1]))
		cx1 = int(m["m10"] / m["m00"])
		cy1 = int(m["m01"] / m["m00"])
		cutting_line_points[1].reverse()
		width_points[1].reverse()
	#######################################
	if hand_drawn:
		if slide_no != 4 and slide_no != 5:
			for point_index in xrange(width_points[0].__len__()):
				div_point_0 = [width_points[0][point_index][0][0] / 3 + width_points[1][point_index][0][0] / 3 * 2,
				               width_points[0][point_index][0][1] / 3 + width_points[1][point_index][0][1] / 3 * 2]
				div_point_1 = [width_points[0][point_index][0][0] / 3 * 2 + width_points[1][point_index][0][0] / 3,
				               width_points[0][point_index][0][1] / 3 * 2 + width_points[1][point_index][0][1] / 3]
				cutting_line_points[0].append([div_point_0])  # near inner
				cutting_line_points[1].append([div_point_1])  # near outer
				#  euclidean distance
				#  use np to do subtraction
				sub_res = np.array(width_points[0][point_index]) - np.array(width_points[1][point_index])
				y_average_list.append(np.sqrt(np.sum(np.square(sub_res))))
		else:
			for point_index in xrange(width_points[0].__len__()):
				cutting_line_points[0].append(
					[width_points[0][point_index][0][0] / 2 + width_points[1][point_index][0][0] / 2,
					 width_points[0][point_index][0][1] / 2 + width_points[1][point_index][0][1] / 2])
				#  euclidean distance
				y_average_list.append(np.sqrt(np.sum(width_points[0][point_index] - width_points[1][point_index])))
		'''
		end cutting_line_points calculation
		'''
		rcm_thickening.append(abs(np.average(y_average_list)))
		cutting_line_points[1].reverse()
		width_points[1].reverse()
	'''
	construct regions via width_points and cutting_line_points
	'''
	if slide_no != 4 and slide_no != 5:
		first = width_points[0] + cutting_line_points[1]
		second = cutting_line_points[0] + cutting_line_points[1]
		third = cutting_line_points[0] + width_points[1]
	else:
		first = width_points[0] + cutting_line_points[0]
		second = cutting_line_points[0] + width_points[1]
		third = []
	if hand_drawn and width_points[2].__len__() is not 0:
		trabe_points = width_points[1] + width_points[2]
	#######################################
	# draw the segmentation lines
	first_pts = np.array([cutting_line_points[1]], np.int32)
	second_pts = np.array([cutting_line_points[0]], np.int32)
	first_pts.reshape(-1, 1, 2)
	second_pts.reshape(-1, 1, 2)
	'''
	draw lines
	'''
	if not hand_drawn:
		cv2.polylines(rgbimg, first_pts, False, (0, 0, 255), 6)  # red line
		if slide_no != 4 and slide_no != 5:
			cv2.polylines(rgbimg, second_pts, False, (0, 255, 0), 6)  # green line
	else:  # hand_drawn
		cv2.polylines(rgbimg, first_pts, False, (0, 255, 255), 6)  # yellow line
		if slide_no != 4 and slide_no != 5:
			cv2.polylines(rgbimg, second_pts, False, (255, 255, 0), 6)  # light blue
		# imgshow(rgbimg)
		pass
	
	# height_line_points[1].reverse()
	# height_points[1].reverse()
	# draw height measure line : unnecessary
	# height_first_pts = np.array([height_line_points[0]], np.int32)
	# height_second_pts = np.array([height_line_points[1]], np.int32)
	# height_first_pts.reshape(-1, 1, 2)
	# height_second_pts.reshape(-1, 1, 2)
	# cv2.polylines(rgbimg, height_first_pts, False, (255, 0, 0), 5)
	# cv2.polylines(rgbimg, height_second_pts, False, (255, 0, 0), 5)
	'''
	save images and make dirs
	'''
	if not os.path.exists('HE_image' + str(he_patients[patient_id]) + '/segmentation'):
		os.makedirs('HE_image' + str(he_patients[patient_id]) + '/segmentation')
	if not os.path.exists('MASSON_image' + str(masson_patients[patient_id]) + '/segmentation'):
		os.makedirs('MASSON_image' + str(masson_patients[patient_id]) + '/segmentation')
	# othermask_img_name = ('HE_image' + str(he_patients[patient_id]) + '/segmentation/slide_' + str(slide_no) + '.jpg' if (
	# 		is_masson is False)
	#             else 'MASSON_image' + str(masson_patients[patient_id]) + '/segmentation/slide_' + str(slide_no) + '.jpg')
	# cv2.imwrite(othermask_img_name, rgbimg)  # save the img of segmentation result
	#################################################
	'''
	construct masks
	'''
	i = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
	firstmask = cv2.fillPoly(i, np.array([first], np.int32), 255)  # fillPoly()对于限定轮廓的区域进行填充
	
	# print firstmask[363][154]
	
	i = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
	secondmask = cv2.fillPoly(i, np.array([second], np.int32), 255)
	if show_img:
		cv2.imshow(othermask_img_name, rgbimg)  # save the img of segmentation result
		cv2.imshow("firstmask", firstmask)
		cv2.imshow("secondmask", secondmask)
	thirdmask = []
	if slide_no != 4 and slide_no != 5:
		i = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
		thirdmask = cv2.fillPoly(i, np.array([third], np.int32), 255)
	othermask = []
	if calculate_trabe_flag and not hand_drawn:
		box1 = cv2.boxPoints(rect_other)
		box1 = np.array(box1)
		for i in range(0, 2):
			max_area_index = sqrt((box1[i][0] - cx1) * (box1[i][0] - cx1) + (box1[i][1] - cy1) * (box1[i][1] - cy1))
			n = i
			for j in range(i, 4):
				if sqrt((box1[j][0] - cx1) * (box1[j][0] - cx1) + (box1[j][1] - cy1) * (
						box1[j][1] - cy1)) > max_area_index:
					max_area_index = sqrt(
						(box1[j][0] - cx1) * (box1[j][0] - cx1) + (box1[j][1] - cy1) * (box1[j][1] - cy1))
					n = j
			k = (box1[i][0], box1[i][1])
			box1[i] = box1[n]
			box1[n] = [k[0], k[1]]
		
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
	elif hand_drawn:
		# othermask = cv2.fillPoly()
		# i = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
		if width_points[2].__len__() is 0:
			othermask = g_img - firstmask - secondmask - thirdmask
		else:
			i = np.zeros((working_dimensions[1], working_dimensions[0]), np.uint8)
			othermask = cv2.fillPoly(i, np.array([trabe_points], np.int32), 255)
		'''
		add MORPH_OPEN calculation, eliminate areas on the outer side, deprecated in this branch
		'''
		othermask = cv2.morphologyEx(othermask, cv2.MORPH_OPEN, kernel, iterations=5)
		img, other_counters, _ = cv2.findContours(othermask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		#  get mean_point of outer/inner layer
		outer_mean_point = (np.mean([i[0] for i in x_list[:x_list.__len__() / 2]]),
		                    np.mean([i[1] for i in x_list[:x_list.__len__() / 2]]))
		inner_mean_point = (np.mean([i[0] for i in x_list[x_list.__len__() / 2:]]),
		                    np.mean([i[1] for i in x_list[x_list.__len__() / 2:]]))
		#  reconstruct with_point_lines
		# for i in width_points:  # (vx,vy,x,y)
		line_outer = cv2.fitLine(np.array(width_points[0]), cv2.DIST_L2, 0, 0.01, 0.01)
		k_outer = line_outer[1] / line_outer[0]
		line_inner = cv2.fitLine(np.array(width_points[1]), cv2.DIST_L2, 0, 0.01, 0.01)
		k_inner = line_inner[1] / line_inner[0]
		
		length = 300
		point_out = (line_outer[2] - length, line_outer[3] - k_outer * length), \
		            (line_outer[2] + length, line_outer[3] + k_outer * length)
		point_in = (line_inner[2] - length, line_inner[3] - k_inner * length), \
		           (line_inner[2] + length, line_inner[3] + k_inner * length)
		
		cv2.line(rgbimg, point_out[0], point_out[1], (0, 0, 0), 3)
		cv2.line(rgbimg, point_in[0], point_in[1], (255, 255, 255), 3)
		
		# for i in other_counters:
		# 	mean_point = np.array((np.mean([j[0][0] for j in i]),
		# 	                       np.mean([j[0][1] for j in i])), float)
		# 	# if np.sqrt(np.square(np.sum(mean_point - outer_mean_point))) < np.sqrt(
		# 	# 		np.square(np.sum(mean_point - inner_mean_point))):
		# 	if distance_between_point_line(line_outer, mean_point) < \
		# 			distance_between_point_line(line_inner, mean_point):
		# 		# cv2.drawContours(othermask, [i], 0, 0, -1)  # eliminate extra areas
		# 		# cv2.drawContours(othermask, [i], 0, 0, 3)  # eliminate extra areas
		# 		cv2.drawContours(rgbimg, [i], 0, (0, 255, 0), 3)  # eliminate extra areas
		# 		pass
		# points = other_counters[0]
		# for i in other_counters[1:]:
		# 	if len(i) > 10:
		# 		points = np.append(points, i, axis=0)
		# points = np.unique(points, axis=0)  # get unique points
		# draw points in the original image
		# points = np.array([points], np.int32)  # convert to np.int32 works well
		
		'''
		calculate thickness of trabe if hand_drawn, not needed now..
		'''
		# img, other_cnts, _ = cv2.findContours(othermask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		# points_other = cv2.approxPolyDP(other_cnts[0], 15, True)
		# rect_other = cv2.minAreaRect(points_other)
		# slop_of_other_01 = tan((-rect_other[2] + 90) / 180 * pi)
		# slope_of_wall = (np.mean(x_list[:x_list.__len__() / 2][0]) - np.mean(x_list[x_list.__len__() / 2:][0]))
		'''
		show and save images
		'''
		imgshow(rgbimg)
		imgshow(firstmask, cmap='gray')
		imgshow(secondmask, cmap='gray')
		imgshow(thirdmask, cmap='gray')
		imgshow(othermask, cmap='gray')
		othermask_img_name = (
			'HE_image' + str(he_patients[patient_id]) + '/segmentation/slide' + str(slide_no) + '_other_mask.jpg' if (
					is_masson is False)
			else 'HE_image' + str(masson_patients[patient_id]) + '/segmentation/slide' + str(
				slide_no) + '_other_mask.jpg')
		cv2.imwrite(othermask_img_name, othermask)  # save the img of segmentation result
		rgb_img_name = (
			'HE_image' + str(he_patients[patient_id]) + '/segmentation/slide' + str(slide_no) + '_result.jpg' if (
					is_masson is False)
			else 'MASSON_image' + str(masson_patients[patient_id]) + '/segmentation/slide' + str(
				slide_no) + '_result.jpg')
		cv2.imwrite(rgb_img_name, rgbimg)
		pass
	cv2.destroyAllWindows()
	if is_masson is True:
		return firstmask, secondmask, thirdmask, othermask, grey_img, hsv, rcm_thickening  # [other_height, wall_height]
	else:
		return firstmask, secondmask, thirdmask, othermask, rcm_thickening


def detect_process(region, hsv, patient_num, slide_no, processed_mask_name, cardiac_store_remain_num,
                   vacuole_store_remain_num, write_test_image=False, debug_mod=False, extract_mod=False):
	"""

	:rtype: object
	"""
	# cv2.imwrite("tmp/hsv.jpg", hsv)
	b = len(hsv[0])
	c = len(hsv)
	h, s, v = cv2.split(hsv)
	h = cv2.subtract(180, h)
	ret, s = cv2.threshold(s, 20, 255, cv2.THRESH_BINARY_INV)
	gray = cv2.addWeighted(s, -1, h, 1, 0)  # 色调，饱和度相加得到灰度图 S1
	# cv2.imwrite("tmp/gray.jpg", gray)
	whole_area_space = cv2.countNonZero(gray)
	# print 'myocardium space in this region: ', whole_area_space
	kernel = np.ones((3, 3), np.uint8)
	
	ret, nuclear0 = cv2.threshold(gray, 43, 255, cv2.THRESH_BINARY)  # S2 TODO modify the gray threshold
	
	nuclear0 = cv2.morphologyEx(nuclear0, cv2.MORPH_OPEN, kernel, iterations=2)  # S3 OPEN消除极小区域
	
	sure_bg = cv2.dilate(nuclear0, kernel, iterations=3)  # S4 sure background area
	
	ret, nuclear1 = cv2.threshold(gray, 43, 255, cv2.THRESH_BINARY)  # extract sg todo
	
	for i in range(0, len(nuclear1[0])):
		nuclear1[0][i] = 0
	
	# cv2.imshow("nuclear1", nuclear1)
	mask = np.zeros((c + 2, b + 2), np.uint8)
	cv2.floodFill(nuclear1, mask, (0, 0), 100)  # S5 把细胞核内不均匀的浅色填充回细胞和区域
	nuclear1[nuclear1 == 0] = 255
	nuclear1[nuclear1 == 100] = 0
	
	# dist_transform = cv2.distanceTransform(nuclear1, cv2.DIST_L2, 5)  # S6
	# dist_transform = np.uint8(dist_transform)
	# ret, out = cv2.threshold(dist_transform, 5, 255, cv2.THRESH_BINARY_INV)  # todo
	
	nuclear1 = 255 - nuclear1  # 得到的nuclear1此时是细胞质区域
	gray1 = cv2.subtract(gray, nuclear1)
	# cv2.imshow("gray1", gray1)  # 去掉细胞质，得到细胞核的图像
	gray1 = cv2.blur(gray1, (5, 5))
	
	# dist_transform = cv2.addWeighted(dist_transform, 1, gray1, 0.1, 0)
	# cv2.imshow("dist_transform", dist_transform)
	dilation_num = 10
	max = cv2.dilate(gray1, kernel, iterations=dilation_num)
	
	max -= dilation_num
	# max = cv2.multiply(max, 0.90)
	
	# =========get sure ff=============#
	sure_fg = cv2.subtract(gray1, max)
	# sure_fg = cv2.subtract(sure_fg, out)
	ret, sure_fg = cv2.threshold(sure_fg, 0, 255, cv2.THRESH_BINARY)
	sure_fg = np.uint8(sure_fg)
	# if write_test_image:
	# imgshow(region)
	# imgshow(sure_fg, cmap='gray')
	# imgshow(sure_bg, cmap='gray')
	# cv2.imwrite('tmp/gray.jpg', gray)
	# cv2.imwrite("tmp/rgb.jpg", region)
	# cv2.imwrite("tmp/nuclear0.jpg", nuclear0)
	# cv2.imwrite("tmp/sure_bg.jpg", sure_bg)
	# cv2.imwrite('tmp/sure_fg.jpg', sure_fg)
	
	# ============= get unknown area ============#
	unknown = cv2.subtract(sure_bg, sure_fg)
	ret, markers = cv2.connectedComponents(sure_fg)
	markers = markers + 1
	markers[unknown == 255] = 0
	markers = cv2.watershed(region, markers)
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
	cardiac_cell_mask_list = []
	vacuole_cell_contour_list = []
	for i in range(2, markers.max() + 1):
		j = np.zeros((c, b), np.uint8)
		# print 'j.size:', j.size
		j[markers == i] = 255  # why?
		area = cv2.countNonZero(j)
		# if area > 361:
		if area > 400:  # 心肌细胞核比较大,19/3/23设置成400
			cardiac_cell_mask_list.append(i)
			# get arc
			_, contours, hierarchy = cv2.findContours(j, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
			cnt = contours[0]
			perimeter = cv2.arcLength(cnt, True)
			nuclear_area_space.append([i, area, perimeter])
			detect[1] += 1
			if area >= 1334:  # 有可能将两个细胞核识别成一个，这里用一个简单的阈值进行处理
				detect[1] += 1
			j_dilated = cv2.dilate(j, kernel, iterations=2)
			image, lines, hier = cv2.findContours(j_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
			white = 0
			total = 0
			for k in lines[0]:  # why lines[0]?
				total = total + 1
				if hsv[k[0][1]][k[0][0]][1] < 80:  # 空泡的hsv阈值
					white += 1
			if white > total / 2:  # 只有当边缘白色大于一定程度的时候，才计算为空泡
				j_white_dilated = cv2.dilate(j_dilated, kernel, iterations=15)  # 找到更外围一圈的点，判断是不是被心肌包围，去除边界细胞核背景的影响
				_image, dil_lines, _ = cv2.findContours(j_white_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
				_image = region.copy()
				cv2.drawContours(_image, dil_lines, -1, (0, 255, 255), 2)
				# imgshow(_image)
				not_white = 0
				cardiac_area_total = 0
				for k in dil_lines[0]:  # why lines[0]?
					cardiac_area_total = cardiac_area_total + 1
					if hsv[k[0][1]][k[0][0]][1] > 80:  # 空泡的hsv阈值
						not_white += 1
				if not_white > cardiac_area_total / 2:  # h: 139-158 s:36-192
					non_nuclear_area_space.append([i, white])
					detect[0] = detect[0] + 1
					vacuole_cell_contour_list.append(lines)
		
		else:
			detect[2] += 1  # 其余非心肌细胞核
	save_for_vacuole = False
	
	if vacuole_cell_contour_list.__len__() > vacuole_store_remain_num[0]:
		vacuole_store_remain_num[0] = vacuole_cell_contour_list.__len__()
		print 'vacuole'
		print vacuole_store_remain_num[0]
		# save
		vacuole_image = region.copy()
		for contour in vacuole_cell_contour_list:
			cv2.drawContours(vacuole_image, contour[0], -1, (0, 0, 255), 2)
		# if not os.path.exists('HE_image/' + str(patient_num)):
		# 	os.mkdir()
		if not os.path.exists('HE_image/' + str(patient_num) + '/vacuole_cells'):
			os.makedirs('HE_image' + str(patient_num) + '/vacuole_cells')
		if debug_mod:
			imgshow(vacuole_image)
		cv2.imwrite(
			'HE_image' + str(patient_num) + '/vacuole_cells' + "/slide_" + str(
				slide_no) + "_" + processed_mask_name + ".jpg", vacuole_image)  # need more test
		if write_test_image:
			cv2.imwrite(
				"tmp/" + str(
					slide_no) + "_vacuole_" + processed_mask_name + ".jpg", vacuole_image)  # need more test
		save_for_vacuole = True
	# vacuole_store_remain_num[0] -= 1
	if save_for_vacuole or (cardiac_cell_mask_list.__len__() > cardiac_store_remain_num[0]):  # save cardiac cell img
		if not save_for_vacuole:
			cardiac_store_remain_num[0] = cardiac_cell_mask_list.__len__()
		print 'cardiac'
		print cardiac_store_remain_num[0]
		j = np.zeros((c, b), np.uint8)
		# print 'j.size:', j.size
		for i in cardiac_cell_mask_list:
			j[markers == i] = 255
		img_to_save = region.copy()  # copy original rgb img
		# img_to_save[markers == i] = [0, 0, 255]
		_, contours, hierarchy = cv2.findContours(j, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
		cv2.drawContours(img_to_save, contours, -1, (0, 0, 255), 2)
		if not os.path.exists('HE_image' + str(patient_num) + '/cardiac_cells'):
			os.makedirs('HE_image' + str(patient_num) + '/cardiac_cells')
		if save_for_vacuole:
			cv2.imwrite(
				'HE_image' + str(patient_num) + '/vacuole_cells' + "/slide_" + str(
					slide_no) + "_" + processed_mask_name + "_contrast.jpg", img_to_save)
			save_for_vacuole = False
		if debug_mod:
			imgshow(img_to_save)
		cv2.imwrite(
			'HE_image' + str(patient_num) + '/cardiac_cells' + "/slide_" + str(
				slide_no) + "_" + processed_mask_name + ".jpg", img_to_save)
		if write_test_image:
			cv2.imwrite(
				"tmp/" + str(
					slide_no) + "_" + processed_mask_name + ".jpg", img_to_save)
	# cardiac_store_remain_num[0] -= 1
	# end save
	#  返回值空泡 心肌 非心肌 总面积 心肌细胞的面积和周长列表
	return detect[0], detect[1], detect[2], whole_area_space, [i[1:] for i in nuclear_area_space], \
	       [i[1:] for i in non_nuclear_area_space]


def masson_region_slide(slide, working_level, threshold_type, patient_num, slide_no, processed_mask_nam=None,
                        store_remain_no=0, threshold=(),
                        start_pos=(0, 0), is_debug=False,
                        dimension=(500, 500), save_image=False):
	working_dimensions = slide.level_dimensions[working_level]
	if is_debug is True:
		img = np.array(slide.read_region(start_pos, working_level, working_dimensions))
	else:
		img = np.array(slide.read_region(start_pos, working_level, dimension))
	rr, gg, bb, aa = cv2.split(img)
	bgr_cv_img = cv2.merge((bb, gg, rr))
	# cv2.imshow('bgr_img', bgr_cv_img)
	hsv = cv2.cvtColor(bgr_cv_img, cv2.COLOR_BGR2HSV)
	# (155, 140, 50), (175, 180, 255) cardiac
	# (90, 20, 20), (140, 255, 255) fibrosis
	# calculate threshold
	mask = cv2.inRange(hsv, threshold[0], threshold[1])  # s 50-250 in paper
	region_area = cv2.countNonZero(hsv)
	# cv2.imshow('hsv_cardiac_cell', hsv)
	# just global image needed...
	if save_image:
		if not os.path.exists("MASSON_image" + str(patient_num) + '/' + threshold_type):
			os.makedirs("MASSON_image" + str(patient_num) + '/' + threshold_type)
		# subtracted = cv2.subtract(bgr_cv_img, hsv)
		t = cv2.subtract(bgr_cv_img, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR))
		cv2.imwrite(
			"MASSON_image" + str(patient_num) + '/' + threshold_type + "/slide" + str(
				slide_no) + ".jpg", t)  # threshold
		cv2.imwrite(
			"MASSON_image" + str(patient_num) + '/' + threshold_type + "/slide" + str(
				slide_no) + "_rgb.jpg", bgr_cv_img)  # rgb
	# if threshold_type is 'cardiac' and region_area > store_remain_no[0] or (
	# 		threshold_type is 'fibrosis' and region_area > store_remain_no[1]):
	# 	if threshold_type is 'cardiac':
	# 		store_remain_no[0] = region_area
	# 	else:
	# 		store_remain_no[1] = region_area
	# 	# print threshold_type
	# 	# print region_area
	# 	if not os.path.exists("MASSON_image/" + threshold_type + str(patient_num)):
	# 		os.mkdir("MASSON_image/" + threshold_type + str(patient_num))
	# 	cv2.imwrite(
	# 		"MASSON_image/" + threshold_type + str(patient_num) + "/slide_" + str(
	# 			slide_no) + "_" + processed_mask_name + ".jpg", hsv)  # threshold
	# 	cv2.imwrite(
	# 		'MASSON_image/' + threshold_type + str(patient_num) + "/slide_" + str(
	# 			slide_no) + "_" + processed_mask_name + "_rgb.jpg", bgr_cv_img)  # rgb\
	# 	store_remain_no[0] -= 1
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
