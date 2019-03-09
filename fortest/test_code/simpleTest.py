# coding=utf-8
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import xlwt
import openslide
import xlrd
from xlutils.copy import copy
from xlwt import Style
from module import imgshow
from module import hand_draw_split_test, thresh

# list_data = [1.0, 2, 3, 4, [5.0, 6], 7]
list_data = []


def write_file(list_for_write):
	with open('Row_Num/test.txt', 'w') as f:
		f.write(str(56))


def read_file(filename, print_file=False):
	global list_data
	list_read = []
	with open(filename, 'r') as f:
		list_data = f.read()
	if print_file:
		print list_data


l = [1, 2, 3, 4, 5, 4, 3, 2, 1]


# os.mkdir('test')
# print os.path.exists('test')
# write_file(l)
def gray_test():
	gray = cv2.imread('tmp/0_Endocardium.jpg', 0)
	# ret, gray = cv.threshold(gray, 60, 255, cv.THRESH_BINARY)
	cv2.imshow('gray', gray)
	
	def getpos(event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			print(gray[y, x])
	
	cv2.setMouseCallback('gray', getpos)


# gray_test()

# for i in xrange(7):
# 	try:
# 		slide_test = openslide.open_slide('./../../rcm_images/HE/28330/28330-' + str(i+1) + '.ndpi')
# 		print slide_test.dimensions
# 	except:
# 		continue

# cv2.imshow('res_cardiac_HSV', res_cardiac_hsv)
# cv2.imshow('res_fibrosis_hsv', res_fibrosis_hsv)
# cv2.imshow('rgb_masson', bgr_img)

cardiac_threshold = (155, 43, 46), (175, 255, 255)  # cardiac
fibrosis_threshold = (100, 43, 46), (134, 255, 255)  # fibrosis

# def imgshow(img, read_from_cv=True, cmap=None):
# 	# b, g, r = cv.split(img)
# 	# he_image = cv.merge((r, g, b))
# 	if read_from_cv:
# 		img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
# 	else:
# 		pass
# 	if cmap is not None:
# 		plt.imshow(img, cmap=cmap)
# 	else:
# 		plt.imshow(img)
# 	plt.show()


# def test_threshold():
# 	for i in range(2, 3):
# 		slide_masson = openslide.open_slide('/home/zhourongchen/zrc/rcm/images/MASSON/28330/28330-' + str(i) + '.ndpi')
# 		# print slide_masson.dimensions
# 		img = np.array(slide_masson.read_region((0, 0), 5, slide_masson.level_dimensions[5]))
# 		r, g, b, a = cv.split(img)
# 		bgr_img = cv.merge((b, g, r))
# 		hsv = cv.cvtColor(bgr_img, cv.COLOR_BGR2HSV)
# 		mean = cv.mean(hsv)
# 		# mask = cv.inRange(hsv, fibrosis_threshold[0], fibrosis_threshold[1])
# 		mask = cv.inRange(hsv, cardiac_threshold[0], cardiac_threshold[1])
# 		imgshow(bgr_img)
# 		t = cv.subtract(bgr_img, cv.cvtColor(mask, cv.COLOR_GRAY2BGR))
# 		imgshow(t)
# 		print mean
# 	pass


# def hand_draw_split_test(level, threshes, image_path, slide_path):
# 	# slide_he = openslide.open_slide('/home/zhourongchen/zrc/rcm/images/MASSON/30638/28330-.ndpi')
# 	he_image = cv.imread(image_path)
# 	imgshow(he_image)
# 	hsv = cv.cvtColor(he_image, cv.COLOR_BGR2HSV)
# 	slide = openslide.open_slide(slide_path)
# 	# print he_slide.dimensions
# 	# level = 5
# 	origin_level = 6
# 	slide_img = np.array(slide.read_region((0, 0), level, slide.level_dimensions[level]))
# 	print slide_img.shape
# 	slide_img = cv.cvtColor(slide_img, cv.COLOR_RGBA2BGR)
# 	for t in threshes:
# 		mask = cv.inRange(hsv, t[0], t[1])
# 		# mask = cv.inRange(hsv, np.array([170, 43, 43]), np.array([180, 255, 255]))
# 		# dst = cv.bitwise_and(he_image, he_image, mask=mask)
# 		# imgshow(dst)
# 		# get points on the contours
# 		_, contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
# 		points = contours[0]
# 		for i in contours[1:]:
# 			if len(i) > 10:
# 				points = np.append(points, i, axis=0)
# 		points = np.unique(points, axis=0)  # get unique points
# 		points = np.array([points], np.int32)  # convert to np.int32 works well
# 		# sort by distance
# 		num = 100
# 		# dist = (points[0][-1][0][0] - points[0][0][0][0]) / 100
# 		# print dist
# 		print points.size
# 		# sort by x
# 		# points = points[points[:, 0].argsort()]
# 		# draw_img0 = cv.drawContours(dst.copy(), contours, -1, (0, 255, 0), 3)
# 		# imgshow(dst)
# 		# print dst.shape
# 		points *= pow(2, origin_level - level)  # cvt points in different dimensions
# 		if thresh.index(t) is 0:  # outer
# 			# cv.polylines(dst, points, False, color=(0, 0, 255), thickness=4)
# 			cv.polylines(slide_img, points, False, color=(0, 0, 255), thickness=5)
# 		else:  # inner
# 			# cv.polylines(dst, points, False, color=(0, 255, 0), thickness=4)
# 			cv.polylines(slide_img, points, False, color=(0, 255, 0), thickness=5)
#
# 	imgshow(slide_img)
# 	# print he_slide.dimensions[0]/dst.shape[0]
# 	pass


if __name__ == '__main__':
	# normalization test
	slide_path = '/home/zhourongchen/zrc/rcm/images/HE/25845/25845-1.ndpi'
	image_path = '/home/zhourongchen/lys/rcm_project/fortest/test_code/HE_image/25845/whole/25845_slide0.jpg'
	slide_for_test = openslide.open_slide(slide_path)
	hand_draw_split_test(5, thresh, image_path=image_path, slide=slide_for_test)
	pass

cv2.destroyAllWindows()
