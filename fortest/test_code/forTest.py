# coding=utf-8
import sys
import os
from scipy.stats import iqr

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from module import *

# img_dir = 'G:\Junior\Tsinghua research\rcm_images\\'


# beilv = dimension[0] / mason['dimensions'][0]
countbodyMax = 0
meanmax = 0
detectmax = 0
avermax = 0
numbermax = 0

slide = []

# cv2.imshow('hsv', hsv)
# body = cv2.inRange(hsv, (0, 40, 0), (180, 255, 255))
# cv2.imshow('body', body)
# countbody = cv2.countNonZero(body)
# cv2.imshow("body", body)

# N, W = detectprocess(region, hsv)
slide2 = []
level = 0
dimension = ()
result = [[], [], [], ]
whole_res = []


def init():
	img_dir = './../../rcm_images/'
	kk = 1
	name = '25845-' + str(kk)
	he_imgname = name + '.ndpi'
	patients = ['/25845', '/28330', '/29708', '/30638', '/31398', '/35485']
	patient = patients[0]
	imgname = patient + '-' + str(kk) + '.ndpi'
	
	path = img_dir + 'HE\\' + patient + imgname
	global slide
	global slide2
	path1 = img_dir + 'MASSON\\' + patient + imgname
	slide = openslide.open_slide(path)
	# slide2 = openslide.open_slide(path1)
	# mason = averagefibrosis(slide, slide2)
	global dimension
	dimension = slide.dimensions
	'''
	dimension (81920L, 65536L)
	(1280L, 1024L)
	'''
	# print "dimension", dimension
	max_level = slide.level_count - 1
	n = 21
	global level
	level = max_level - 4
	workingDimensions = slide.level_dimensions[level]
	# print workingDimensions
	print "init finished, working dimension: ", workingDimensions, "working level:", level


def test_proc():
	# print dimension
	# region = np.array((slide.read_region((0, 0), level, (1000, 1000))))
	# region = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
	# cv2.imshow("whole_img", region)
	region = np.array(slide.read_region((30000, 30000), 0, (1000, 1000)))
	# region = np.array(slide.read_region((0, 0), 0, (1000, 1000)))
	region = cv2.cvtColor(region, cv2.COLOR_RGBA2BGR)
	# cv2.imshow("region", region)
	hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
	
	# cv2.imshow("origin", hsv)
	# h, s, v = cv2.split(hsv)
	# res, s = cv2.threshold(s, 20, 255, cv2.THRESH_BINARY)
	
	# lower = np.array([0, 20, 100])
	# upper = np.array([255, 180, 255])
	# mask = cv2.inRange(hsv, lower, upper)
	# res = cv2.bitwise_and(hsv, hsv, mask)
	# cv2.imshow("res", res)
	
	detect = detectprocess(region, hsv)
	
	def getpos(event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			print(hsv[y, x])
	
	# cv2.imshow('HSV', hsv)
	cv2.setMouseCallback('HSV', getpos)
	print detect
	return detect


# whole_img = slide.read_region((0, 0), 0, dimension)

# print firstmask
mask_name = ['firstmask', 'secondmask', 'secondmask', 'secondmask', 'whole']


def he_proc():
	global result
	firstmask, secondmask, thirdmask, othermask = editareaHE(level, slide)
	global mask_name
	areas = [firstmask, secondmask, thirdmask, othermask]
	magnify = pow(2, level)
	area_length = 500
	i = 0
	for area in areas:
		for y in range(0, dimension[1] - 1000, 1000):
			for x in range(0, dimension[0] - 1000, 1000):
				# if whole_img[x * magnify + 500][y * magnify + 500] != 0:
				if firstmask[int((y + 500) / magnify)][int((x + 500) / magnify)] != 0:
					print x, y
					region = np.array(slide.read_region((x, y), 0, (1000, 1000)))
					region = cv2.cvtColor(region, cv2.COLOR_RGBA2BGR)
					hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
					detect = detectprocess(region, hsv)
					result[0] += (detect[0])
					result[1] += (detect[1])
					result[2] += (detect[2])
					result[3] += (detect[3])
					result[4].append(detect[4])
		print (mask_name[i], ' : ', sum(result[0]), sum(result[1]), sum(result[2]), sum(result[3]))
		i += 1
		whole_res.append(result)
		result = [[], [], [], ]


def he_statics_persistence(res):
	global mask_name
	index = 0
	for i in xrange(len(res)):
		cardiac_cells_num = res[1]
		non_cardiac_cells_num = res[2]
		vacuole_num = res[0]
		region_area = res[3]
		cardiac_cells_nucleus_area = [i[0] for i in res[4]]
		cardiac_cells_nucleus_perimeter = [i[1] for i in res[4]]
		
		cardiac_cells_ratio = non_cardiac_cells_num / float(cardiac_cells_num)
		cardiac_area_num_ratio = region_area / float(cardiac_cells_num)
		
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
		# intensity = cardiac_cells_num/float(region_area)
		
		# area ratio  心肌细胞核面积占心肌细胞的面积比例
		cardiac_cells_nucleus_area_region_ratio = float(sum(cardiac_cells_nucleus_area)) / region_area
		
		# vacuole calculation
		cardiac_cells_vacuole_area_mean = np.mean(vacuole_num)
		cardiac_cells_vacuole_area_median = np.median(vacuole_num)
		cardiac_cells_vacuole_area_sd = np.std(vacuole_num, ddof=1)
		
		print 'region: ' + mask_name[index]
		print 'Cardiac cells num' + str(res[1])
		print 'vacuole cells num' + str(res[0])
		print 'Non-cardiac cells num' + str(res[2])
		print 'region area: ' + mask_name[index] + str(res[3])
	
	# print
	pass


if __name__ == '__main__':
	init()
	whole_res = test_proc()
	he_statics_persistence(whole_res)
# 空泡 心肌细胞核 非心肌细胞核 区域总面积 列表[编号，细胞核面积，细胞核周长]
# cv2.waitKey(0)
# cv2.destroyAllWindows()
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
# cv2.imwrite("test/he_rgbimg.jpg", rgbimg)
# hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
# cv2.imwrite("test/he_hsv.jpg", hsv)
# greyimg = cv2.inRange(hsv, (0, 20, 0), (180, 255, 255))
# cv2.imwrite("test/he_grey.jpg", greyimg)

# fibrosis = cv2.inRange(hsv, (90, 20, 0), (150, 255, 255))
# cv2.imshow("fibrosis",fibrosis)
# averagegreyimg = cv2.blur(greyimg, (30, 30))
# cv2.imshow('he_average grey img', averagegreyimg)
# cv2.imwrite("test/he_average_grey_img.jpg", averagegreyimg)

# ret, erode = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
# erode = cv2.adaptiveThreshold(averagegreyimg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
# erode = cv2.erode(erode, kernel, iterations=13)
# cv2.imshow("after erosion", erode)
# cv2.imwrite("test/he_after_erosion.jpg", erode)

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
