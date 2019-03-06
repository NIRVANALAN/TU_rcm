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


def imgshow(img):
	# npimg = img.numpy()
	img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
	plt.imshow(img)
	plt.show()


if __name__ == '__main__':
	# normalization test
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
cv.destroyAllWindows()
