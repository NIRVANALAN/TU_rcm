# coding=utf-8
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import xlwt
import openslide
import xlrd
from xlutils.copy import copy
from xlwt import Style

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
	gray = cv.imread('tmp/0_Endocardium.jpg', 0)
	# ret, gray = cv.threshold(gray, 60, 255, cv.THRESH_BINARY)
	cv.imshow('gray', gray)
	
	def getpos(event, x, y, flags, param):
		if event == cv.EVENT_LBUTTONDOWN:
			print(gray[y, x])
	
	cv.setMouseCallback('gray', getpos)


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


def imgshow(img, read_from_cv=True, cmap=None):
	# b, g, r = cv.split(img)
	# he_image = cv.merge((r, g, b))
	if read_from_cv:
		img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
	else:
		pass
	if cmap is not None:
		plt.imshow(img, cmap=cmap)
	else:
		plt.imshow(img)
	plt.show()


def test_threshold():
	for i in range(2, 3):
		slide_masson = openslide.open_slide('/home/zhourongchen/zrc/rcm/images/MASSON/28330/28330-' + str(i) + '.ndpi')
		# print slide_masson.dimensions
		img = np.array(slide_masson.read_region((0, 0), 5, slide_masson.level_dimensions[5]))
		r, g, b, a = cv.split(img)
		bgr_img = cv.merge((b, g, r))
		hsv = cv.cvtColor(bgr_img, cv.COLOR_BGR2HSV)
		mean = cv.mean(hsv)
		# mask = cv.inRange(hsv, fibrosis_threshold[0], fibrosis_threshold[1])
		mask = cv.inRange(hsv, cardiac_threshold[0], cardiac_threshold[1])
		imgshow(bgr_img)
		t = cv.subtract(bgr_img, cv.cvtColor(mask, cv.COLOR_GRAY2BGR))
		imgshow(t)
		print mean
	pass


def hand_draw_split_test():
	# slide_he = openslide.open_slide('/home/zhourongchen/zrc/rcm/images/MASSON/30638/28330-.ndpi')
	he_image = cv.imread(
		'/home/zhourongchen/lys/rcm_project/fortest/test_code/HE_image/30638/whole/slide4.jpg')
	imgshow(he_image)
	hsv = cv.cvtColor(he_image, cv.COLOR_BGR2HSV)
	mask = cv.inRange(hsv, (166, 43, 43), (180, 255, 255))
	# mask = cv.inRange(hsv, np.array([170, 43, 43]), np.array([180, 255, 255]))
	dst = cv.bitwise_and(he_image, he_image, mask=mask)
	# imgshow(dst)
	# get points on the contours
	_, contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
	points = contours[0]
	for i in contours[1:]:
		if len(i) > 10:
			points = np.append(points, i, axis=0)
	points = np.unique(points, axis=0)  # get unique points
	points = np.array([points], np.int32)  # convert to np.int32 works well
	print points.size
	# sort by x
	# points = points[points[:, 0].argsort()]
	cv.polylines(dst, points, False, color=(0, 255, 0), thickness=5)
	# draw_img0 = cv.drawContours(dst.copy(), contours, -1, (0, 255, 0), 3)
	imgshow(dst)
	print dst.shape
	he_slide = openslide.open_slide('/home/zhourongchen/zrc/rcm/images/HE/30638/30638-5.ndpi')
	print he_slide.dimensions
	slide_img = np.array(he_slide.read_region((0, 0), 6, he_slide.level_dimensions[6]))
	print slide_img.shape
	slide_img = cv.cvtColor(slide_img, cv.COLOR_RGBA2BGR)
	cv.polylines(slide_img, points, False, color=(0, 255, 0), thickness=5)
	imgshow(slide_img)
	# print he_slide.dimensions[0]/dst.shape[0]
	pass


if __name__ == '__main__':
	# normalization test
	hand_draw_split_test()
	pass

cv.destroyAllWindows()
