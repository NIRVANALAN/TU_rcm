# coding=utf-8
import sys
import os
from time import time
from skimage import measure
from scipy.stats import iqr
from simpleTest import write_excel
from module import *

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)

# img_dir = 'G:\Junior\Tsinghua research\rcm_images\\'
slide_he = []
slide_masson = []
max_level = 0
working_level = 0
max_dimension = ()
working_dimension = ()

he_path = []
masson_path = []

img_dir = './../../rcm_images/'
patients = ['/25845', '/28330', '/29708', '/30638', '/31398', '/35485']
patient_id = 1


def init_test_proc():
	# kk = 1
	# name = '25845-' + str(kk)
	# he_img_name = name + '.ndpi'
	# patient_id = patients[0]
	# global patient_id
	global he_path
	global masson_path
	he_path, masson_path = get_image_path(0)
	global slide_he
	global slide_masson
	#  init
	slide_he = openslide.open_slide(he_path[0])
	slide_masson = openslide.open_slide(masson_path[0])
	global max_dimension
	global max_level
	max_dimension = slide_he.dimensions
	'''
	dimension (81920L, 65536L)
	(1280L, 1024L)
	'''
	# print "dimension", dimension
	max_level = slide_he.level_count - 1
	global working_level
	working_level = max_level - 4
	global working_dimension
	working_dimension = slide_he.level_dimensions[working_level]
	# print workingDimensions
	print "init finished, working dimension: ", working_dimension, "working level:", max_level


def get_image_path(patient_no, return_type="both"):
	"""
	:param patient_no: the number of patient in the patients[] list
	:param return_type: "both" default
	:return: the he_path and masson_path
	"""
	patient_no = patients[patient_no]
	for i in xrange(1, 7):
		img_name = patient_no + '-' + str(i) + '.ndpi'
		he_path_iter = img_dir + 'HE' + patient_no + img_name
		masson_path_iter = img_dir + 'MASSON' + patient_no + img_name
		he_path.append(he_path_iter)
		masson_path.append(masson_path_iter)
	if return_type is "both":
		return he_path, masson_path


masson_erosion_iteration_time_list = [10, 10, 15, 15, 15, 13]
he_erosion_iteration_time_list = [3, 3, 8, 3, 13, 9]  # for specifications


def write_file(list_for_write, filename):
	with open(filename, 'w') as f:
		f.write(str(list_for_write))


def read_file(filename, print_file=False):
	list_read = []
	with open(filename, 'r') as f:
		list_data = f.read()
	if print_file:
		print list_data


def he_test_proc():
	# print dimension
	# whole_level = 6
	# print "he_test_proc_dimension:", max_level
	slide_no = 5
	global slide_he
	global slide_masson
	slide_he = openslide.open_slide(he_path[slide_no])
	# slide_masson = openslide.open_slide(masson_path[slide_no])
	firstmask, secondmask, thirdmask, othermask, rcm_thickening = edit_area(6, slide_he, he_erosion_iteration_time_list,
	                                                                        masson_erosion_iteration_time_list,
	                                                                        slide_no,
	                                                                        is_masson=False)

	def write_test_img(is_masson=False):
		if is_masson is False:
			path = he_path
			img_dir_path = './../test_images/HE/'
		else:
			path = masson_path
			img_dir_path = './../test_images/MASSON/'
		for i in path:
			slide_iter = openslide.open_slide(i)
			whole_dimension = slide_iter.level_dimensions[working_level]
			region = np.array((slide_iter.read_region((0, 0), working_level, whole_dimension)))
			region = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
			# cv2.imshow(i, region)
			img_path_iter = img_dir_path + i.split('/')[-2]
			if not os.path.exists(img_path_iter):
				os.mkdir(img_path_iter)
			cv2.imwrite(img_path_iter + '/' + i.split('/')[-1] + '.jpg', region)

	# write_test_img(is_masson=True)
	# region = np.array(slide_he.read_region((30000, 30000), 0, (1000, 1000)))
	# region = np.array(slide.read_region((0, 0), 0, (1000, 1000)))
	# region = cv2.cvtColor(region, cv2.COLOR_RGBA2BGR)
	# cv2.imshow("region", region)
	# hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

	# cv2.imshow("origin", hsv)
	# h, s, v = cv2.split(hsv)
	# res, s = cv2.threshold(s, 20, 255, cv2.THRESH_BINARY)

	# lower = np.array([0, 20, 100])
	# upper = np.array([255, 180, 255])
	# mask = cv2.inRange(hsv, lower, upper)
	# res = cv2.bitwise_and(hsv, hsv, mask)
	# cv2.imshow("res", res)

	# detect = detectprocess(region, hsv)

	# def getpos(event, x, y, flags, param):
	#     if event == cv2.EVENT_LBUTTONDOWN:
	#         print(hsv[y, x])

	# cv2.imshow('HSV', hsv)
	# cv2.setMouseCallback('HSV', getpos)
	# print detect
	# return detect
	pass


# whole_img = slide.read_region((0, 0), 0, dimension)

# print firstmask
he_mask_name = ['Endocardium', 'Midcardium', 'Epicardium', 'Heart_trabe', 'Whole']

he_proc_iter = [0, 0, 0, [0, 0], [], []]
he_whole_res = []


def he_proc(he_slide_no):
	"""
	:param he_slide_no: the slide_no of a patient
	:return: the whole_result_list of this slide will be saved
	"""
	he_proc_start_time = time()
	global he_proc_iter
	# he_slide_no = 0
	mask_level = 6
	slide_processed = openslide.open_slide(he_path[he_slide_no])
	firstmask, secondmask, thirdmask, othermask, rcm_thickening = edit_area(mask_level, slide_processed,
	                                                                        he_erosion_iteration_time_list,
	                                                                        masson_erosion_iteration_time_list,
	                                                                        slide_no=he_slide_no)
	global he_mask_name
	areas = [firstmask, secondmask, thirdmask, othermask]
	magnify = pow(2, mask_level)
	area_length = 1000
	i = 0
	print "dimension working on:", max_dimension[1], max_dimension[0]
	for area in areas:
		if area:
			for y in range(0, max_dimension[1] - area_length, area_length):
				for x in range(0, max_dimension[0] - area_length, area_length):
					# if whole_img[x * magnify + 500][y * magnify + 500] != 0:
					if area[int((y + area_length / 2) / magnify)][int((x + area_length / 2) / magnify)] != 0:
						# 证明这个像素点在对应的Mask里面
						print x, y
						region = np.array(slide_processed.read_region((x, y), 0, (area_length, area_length)))
						region = cv2.cvtColor(region, cv2.COLOR_RGBA2BGR)
						hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
						detect = detectprocess(region, hsv)
						he_proc_iter[0] += (detect[0])  # 空泡
						he_proc_iter[1] += (detect[1])  # 心肌
						he_proc_iter[2] += (detect[2])  # 非心肌
						he_proc_iter[3][0] += (detect[3])  # 总面积
						he_proc_iter[4].append(detect[4])  # 心肌细胞的[area, perimeter]
		# he_proc_iter[5].append(detect[5])  # 空泡的[area] 暂时没算出来，后面算，这里填空
		he_proc_iter[3][1] = rcm_thickening
		print (he_mask_name[i] + "finished!")
		i += 1
		he_whole_res.append(he_proc_iter)
		he_proc_iter = [0, 0, 0, [0, 0], [], []]  # erase the he_proc_ter var
	write_file(he_whole_res, str(patient_id).split('/')[1] + '_' + str(he_slide_no) + '_he_whole_res.txt')
	print "HE patient: " + str(patient_id) + ' slide no:' + str(he_slide_no) + " finished.Time consumed:" + str(
		time() - he_proc_start_time) + " s"


def he_statics_persistence(whole_res):
	"""
	:param whole_res: res is a list that produced by he_proc(), which stores the statics of each mask of a slide
	:return: Calculate and store in .xls
	"""
	global he_mask_name
	print len(whole_res)  # should be 6..
	whole_list_data = []
	for i in xrange(len(whole_res)):
		vacuole_num = whole_res[i][0]
		cardiac_cells_num = whole_res[i][1]
		non_cardiac_cells_num = whole_res[i][2]
		region_whole_area = whole_res[i][3][0]
		region_rcm_thickening = whole_res[i][3][1][1]
		region_trabe_thickening = whole_res[i][3][1][0]
		cardiac_cells_nucleus_area = [j[0] for j in whole_res[i][4]]
		cardiac_cells_nucleus_perimeter = [j[1] for j in whole_res[i][4]]
		# vacuole_area = res[i][5]

		cardiac_cells_ratio = non_cardiac_cells_num / float(cardiac_cells_num)
		cardiac_area_num_ratio = region_whole_area / float(cardiac_cells_num)

		#  cardiac cell nucleus statics
		# mean
		cardiac_cells_nucleus_area_mean = np.mean(cardiac_cells_nucleus_area)
		# median
		cardiac_cells_nucleus_area_median = np.median(cardiac_cells_nucleus_area)
		# SD
		cardiac_cells_nucleus_area_sd = np.std(cardiac_cells_nucleus_area, ddof=1)
		# IQR
		cardiac_cells_nucleus_area_iqr = iqr(cardiac_cells_nucleus_area, rng=(25, 75), interpolation='midpoint')

		# perimeter calculation
		cardiac_cells_nucleus_perimeter_mean = np.mean(cardiac_cells_nucleus_perimeter)
		cardiac_cells_nucleus_perimeter_median = np.median(cardiac_cells_nucleus_perimeter)
		cardiac_cells_nucleus_perimeter_sd = np.std(cardiac_cells_nucleus_perimeter, ddof=1)
		cardiac_cells_nucleus_perimeter_iqr = iqr(cardiac_cells_nucleus_perimeter, rng=(25, 75),
		                                          interpolation='midpoint')

		# nucleus / whole_area 细胞核总数量/切片总面积
		intensity = cardiac_cells_num / float(region_whole_area)

		# area ratio  心肌细胞核面积占心肌细胞的面积比例
		cardiac_cells_nucleus_area_region_ratio = float(sum(cardiac_cells_nucleus_area)) / region_whole_area

		# vacuole calculation
		# cardiac_cells_vacuole_area_mean = np.mean(vacuole_area)
		# cardiac_cells_vacuole_area_median = np.median(vacuole_area)
		# cardiac_cells_vacuole_area_sd = np.std(vacuole_area, ddof=1)

		print 'region: ' + he_mask_name[i]
		print 'Cardiac cells num: ' + str(whole_res[i][1])
		print 'vacuole cells num: ' + str(whole_res[i][0])
		print 'Non-cardiac cells num: ' + str(whole_res[i][2])
		print 'region area: ' + he_mask_name[i] + str(whole_res[i][3])
		list_data_iter = [cardiac_cells_num, non_cardiac_cells_num, cardiac_cells_ratio, cardiac_area_num_ratio,
		                  cardiac_cells_nucleus_area_mean, cardiac_cells_nucleus_area_median,
		                  cardiac_cells_nucleus_area_sd, cardiac_cells_nucleus_area_iqr,
		                  cardiac_cells_nucleus_perimeter_mean, cardiac_cells_nucleus_perimeter_median,
		                  cardiac_cells_nucleus_perimeter_sd, cardiac_cells_nucleus_perimeter_iqr,
		                  intensity,
		                  cardiac_cells_nucleus_area_region_ratio,
		                  vacuole_num,
		                  region_trabe_thickening,
		                  region_rcm_thickening]  # conform to the HE.XLS form now
		whole_list_data.append(list_data_iter)
	write_excel('HE.xls', whole_list_data)
	# print
	pass


# for masson proc later
cardiac_threshold = (155, 140, 50), (175, 230, 255)  # cardiac
fibrosis_threshold = (90, 20, 20), (140, 255, 255)  # fibrosis

masson_mask_name = ['Endocardium', 'Midcardium', 'Epicardium', 'Heart_trabe', 'Whole']

fibrosis_level = 3


def masson_proc(slide_no, masson_working_level=6):  # need debug and fix
	masson_proc_time_start = time()
	masson_whole_result = []
	masson_result_iter = [[], []]
	slide = openslide.open_slide(masson_path[slide_no])
	i = 0
	# print working_level
	working_dimensions = slide.level_dimensions[masson_working_level]
	# rcm_thickening =  [other_height, wall_height]
	firstmask, secondmask, thirdmask, othermask, grey_img, hsv, fibrosis_img, rcm_thickening = edit_area(
		masson_working_level, slide,
		masson_erosion_iteration_time_list=masson_erosion_iteration_time_list,
		slide_no=slide_no,
		is_masson=True)
	areas = [firstmask, secondmask, thirdmask, othermask]
	magnify = pow(2, masson_working_level)
	area_length = 500
	for area in areas:
		if area:
			for y in range(0, working_dimensions[1] - area_length, area_length):
				for x in range(0, working_dimensions[0] - area_length, area_length):
					if area[int((y + area_length / 2) / magnify)][int((x + area_length / 2) / magnify)] != 0:
						print x, y
						_, cardiac_area = masson_region_slide(slide, masson_working_level, cardiac_threshold, (x, y),
						                                      is_debug=False,
						                                      dimension=(500, 500))
						_, fibrosis_area = masson_region_slide(slide, masson_working_level, fibrosis_threshold, (x, y),
						                                       is_debug=False, dimension=(500, 500))
						masson_result_iter[1] += fibrosis_area
						masson_result_iter[0] += cardiac_area
		masson_result_iter[1] *= (pow(2, masson_working_level) ** 2)
		masson_result_iter[0] *= (pow(2, masson_working_level) ** 2)  # statics should be simulated at max_level
		masson_whole_result.append(masson_result_iter)
		masson_result_iter = [[], []]
		print masson_mask_name[i] + " finished" + "time consumed: " + time() - masson_proc_time_start + "s"
		i += 1
	# fibrosis
	labels = measure.label(fibrosis_img, connectivity=2)
	number = labels.max() + 1
	total_fibrosis_block = []
	for i in range(1, number):
		j = np.zeros((len(fibrosis_img[0]), len(fibrosis_img)), np.uint8)
		j[labels == i] = 255
		total_fibrosis_block.append(cv2.countNonZero(j) * (pow(2, fibrosis_level) ** 2))
	# The statics for storage should be the result at max_level : 0
	fibrosis_block_average = int(np.average(total_fibrosis_block) / number)
	fibrosis_block_mean = np.mean(total_fibrosis_block)
	fibrosis_block_sd = np.std(total_fibrosis_block, ddof=1)
	fibrosis_block_info = [fibrosis_block_average, fibrosis_block_mean, fibrosis_block_sd]
	####################################################################################
	masson_whole_result.append(fibrosis_block_info)  # fibrosis statics append
	masson_whole_result.append(rcm_thickening)  # [other_height, wall_height]
	write_file(masson_whole_result, str(patient_id).split('/')[1] + '_' + str(slide_no) + '_masson_whole_res.txt')
	print "masson_proc() finished, time consumed: " + str(time() - masson_proc_time_start) + " s"
	pass


def masson_test_proc(working_level=6):
	global slide_he
	global slide_masson
	print 'working level', working_level
	working_dimension = slide_masson.level_dimensions[working_level]

	# cardiac_threshold = (155, 140, 50), (175, 230, 255)  # cardiac
	# fibrosis_threshold = (90, 20, 20), (140, 255, 255)  # fibrosis

	# hsv = []
	# rgb_img = []

	def pure_test():
		# global hsv
		# global rgb_img
		# region = np.array(slide_masson.read_region((30000, 30000), 0, (1000, 1000)))
		test_level = 2
		test_dimension = slide_masson.level_dimensions[test_level]
		coord = (22000, 22000)
		region = np.array(slide_masson.read_region(coord, test_level, (1000, 1000)))
		print 'test_dimension:' + str(test_dimension)
		# print "relative coordinate:" + str(coord[0]/test_dimension[0]) + ' ' + str(coord[1]/test_dimension[1])
		r, g, b, a = cv2.split(region)
		bgr_img = cv2.merge((b, g, r))
		gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
		hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
		res_fibrosis_hsv = cv2.inRange(hsv, fibrosis_threshold[0],
		                               fibrosis_threshold[1])  # s 50-255 in paper fibrosis
		res_cardiac_hsv = cv2.inRange(hsv, cardiac_threshold[0], cardiac_threshold[1])  # cardiac threshold
		# fat
		circles1 = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1,
		                            600, param1=100, param2=30, minRadius=50, maxRadius=97)
		circles = np.uint16(np.around(circles1))  # 把circles包含的圆心和半径的值变成整数
		for i in circles[0, :]:
			cv2.circle(bgr_img, (i[0], i[1]), i[2], (0, 0, 255), 2)  # 画圆
			cv2.circle(bgr_img, (i[0], i[1]), 2, (0, 0, 255), 2)  # 画圆心
		cv2.imshow('HSV', hsv)
		cv2.imshow('GRAY', gray)
		cv2.imshow('res_cardiac_HSV', res_cardiac_hsv)
		cv2.imshow('res_fibrosis_hsv', res_fibrosis_hsv)
		cv2.imshow('rgb_masson', bgr_img)

		def getpos(event, x, y, flags, param):
			if event == cv2.EVENT_LBUTTONDOWN:
				print(hsv[y, x])

		cv2.setMouseCallback('HSV', getpos)

	# pure_test()

	slide_no = 0
	# slide_he = openslide.open_slide(he_path[slide_no])
	slide_masson = openslide.open_slide(masson_path[slide_no])
	firstmask, secondmask, thirdmask, othermask, greyimg, hsv, fibrosis_img, rcm_thickening = edit_area(
		working_level,
		slide_masson,
		masson_erosion_iteration_time_list=masson_erosion_iteration_time_list,
		slide_no=slide_no,
		is_masson=True)


if __name__ == '__main__':
	# init_test_proc()
	# for
	he_path, masson_path = get_image_path(0)
	he_proc()
	# masson_proc()

	# masson_test_proc()
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()

	# he test_images
	# he_test_proc()
	# he_whole_res.append(he_test_proc())
	# he_statics_persistence(he_whole_res)
	# 空泡 心肌细胞核 非心肌细胞核 区域总面积 列表[编号，细胞核面积，细胞核周长]
	# cv2.waitKey(0)
	cv2.destroyAllWindows()

	# print dimension
	'''
	(1, 136, 236, 919452, [[3, 355, 99.94112491607666], [8, 322, 67.4558436870575], [9, 541, 161.01219260692596], [10, 329, 73.4558436870575], [12, 911, 152.36753106117249], [14, 606, 104.66904675960541], [18, 436, 87.94112491607666], [20, 732, 107.35533845424652], [24, 435, 89.35533845424652],
	'''
# img = numpy.array(slide.read_region((0, 0), level, workingDimensions))
# grey = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
# greyret, greyimg = cv2.threshold(grey, 225, 255, cv2.THRESH_BINARY_INV)
# dst = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
# average_greyimg = cv2.blur(greyimg, (n, n))
# cv2.imshow('adaptive threshold', dst)
# cv2.imshow('greyimg', greyimg)
# cv2.imshow('average_grey', average_greyimg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# print dimension

# img = np.array(slide.read_region((0, 0), level, workingDimensions))
#
# b, g, r, a = cv2.split(img)
# rgbimg = cv2.merge((r, g, b))
# cv2.imwrite("test_images/he_rgbimg.jpg", rgbimg)
# hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
# cv2.imwrite("test_images/he_hsv.jpg", hsv)
# greyimg = cv2.inRange(hsv, (0, 20, 0), (180, 255, 255))
# cv2.imwrite("test_images/he_grey.jpg", greyimg)

# fibrosis = cv2.inRange(hsv, (90, 20, 0), (150, 255, 255))
# cv2.imshow("fibrosis",fibrosis)
# averagegreyimg = cv2.blur(greyimg, (30, 30))
# cv2.imshow('he_average grey img', averagegreyimg)
# cv2.imwrite("test_images/he_average_grey_img.jpg", averagegreyimg)

# ret, erode = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
# erode = cv2.adaptiveThreshold(averagegreyimg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
# erode = cv2.erode(erode, kernel, iterations=13)
# cv2.imshow("after erosion", erode)
# cv2.imwrite("test_images/he_after_erosion.jpg", erode)

# cv2.imshow("")
# get rid of XIAOLIANG

# ret, averimage = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
# averimage, avercnts, averhierarchy = cv2.findContours(averimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cv2.imshow("aver image", averimage)
# overall contour

# image, cnts, hierarchy = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cv2.imshow("contour after erosion", erode)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
