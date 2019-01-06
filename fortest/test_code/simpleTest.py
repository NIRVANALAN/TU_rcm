# coding=utf-8
import cv2 as cv
import numpy as np
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


# read_file('Row_Num/test.txt', print_file=True)

# f = xlwt.Workbook(encoding='utf-8')
# sheet1 = f.add_sheet('HE')
# col = eval(list_data)


# print type(col[0])


#
# def write_to_xls():
# 	for i, p in enumerate(col):
# 		sheet1.write(i + 1, 1, p)
# 	f.save('test.xls')


# style = xlwt.easyxf('font:height 240, color-index red, bold on;align: wrap on, vert centre, horiz center');
# write_excel('test.xls', list_data)

# 心肌细胞核数量
# 非心肌细胞核数量
# 非心肌细胞核数量/心肌细胞核数量
# 心肌面积/心肌细胞核数量
# 细胞核面积mean
# 细胞核面积median
# 细胞核面积SD
# 细胞核面积IQR
# 细胞核周径mean
# 细胞核周径median
# 细胞核周径SD
# 细胞核周径IQR
# 细胞核总数量/切片整体面积
# 心肌细胞核面积占心肌细胞的面积比例
# 心肌细胞核周空泡数量
# 心肌细胞核周空泡面积mean
# 心肌细胞核周空泡面积median
# 心肌细胞核周空泡面积SD
# 心内膜厚度（RCM增厚）


# img_show = False
# print os.path.realpath(__file__)
# print os.path.abspath('./')
# slide04_test_img = cv.imread("../test_images/HE/25845/25845-4.ndpi.jpg", 0)
# cv.imshow('slide04', slide04_test_img)
cv.waitKey(0)
cv.destroyAllWindows()
# if img is not None:
# 	# img = np.zeros((512, 512, 3), np.uint8)
# 	# dot_list = np.array([[0, 0], [500, 500], [300, 400], [600, 400]], np.int32)
# 	# dot_list = dot_list.reshape((-1, 1, 2))  # means -1 dimension will be calculated automatically
# 	# # cv.line(img, (0, 0), (500, 500), 255, 5)
# 	# cv.polylines(img, dot_list, False, (0, 0, 255))
#
# 	# img = np.zeros((512, 512, 3), np.uint8)
#
# 	pts = np.array([[0, 0], [300, 400], [500, 500], [600, 650]], np.int32)
# 	pts = pts.reshape(-1, 1, 2)
# 	# cv.polylines(img, [pts], False, (0, 255, 255))
# 	rows, cols = img.shape[:2]
# 	[vx, vy, x, y] = cv.fitLine(pts, cv.DIST_L2, 0, 0.01, 0.01)
# 	lefty = int((-x * vy / vx) + y)
# 	righty = int(((cols - x) * vy / vx) + y)
# 	img = cv.line(img, (cols - 1, righty), (0, lefty), (0, 255, 0), 2)
# 	cv.imshow("line", img)
#
# 	# grey = cv.cvtColor(rgb_img, 0)
# 	# ret, thresh = cv.threshold(img, 127, 255, 0)
# 	# _, contours, hier = cv.findContours(thresh, 1, 2)
# 	# # img contours hierachy
# 	# cnt = contours[100]
# 	# M = cv.moments(cnt)
# 	# area = cv.contourArea(cnt)
# 	# cont_img = cv.drawContours(img, contours, 100, (0, 255, 0), 10)
# 	# cv.imshow('cont_img', cont_img)
# 	# print area
# 	# print M['m10'] / M['m00']
# 	# print M['m01'] / M['m00']
# 	# if img_show:
# 	# 	cv.imshow('he_2', img)
# 	# 	cv.imshow('grey', thresh)
# 	cv.waitKey(0)
# 	cv.destroyAllWindows()
# else:
# 	print 'file not exist'
# hsv = cv.cvtColor(rgb_img, cv.COLOR_RGB2HSV)
# grey_img = cv.inRange(hsv, (0, 20, 0), (180, 255, 220))
# cv.imshow("grey", grey_img)
#
# averagegreyimg = cv.blur(grey_img, (30, 30))
# # cv2.imshow('he_average grey img', averagegreyimg)
# cv.imshow("he_average_grey_img.jpg", averagegreyimg)
#
# ret, erode = cv.threshold(averagegreyimg, 120, 255, cv.THRESH_BINARY)
# # erode = cv2.adaptiveThreshold(averagegreyimg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
# kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (4, 4))
# erode = cv.erode(erode, kernel, iterations=3)
# cv.imshow("erode", erode)

if __name__ == '__main__':
	pass
