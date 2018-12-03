import cv2 as cv
import numpy as np
import os
import sys

img_show = False
# print os.path.realpath(__file__)
# print os.path.abspath('./')
img = cv.imread("../test_images/HE/25845/25845-1.ndpi.jpg", 0)
if img is not None:
	# grey = cv.cvtColor(rgb_img, 0)
	ret, thresh = cv.threshold(img, 127, 255, 0)
	_, contours, hier = cv.findContours(thresh, 1, 2)
	# img contours hierachy
	cnt = contours[100]
	M = cv.moments(cnt)
	area = cv.contourArea(cnt)
	cont_img = cv.drawContours(img, contours, 100, (0, 255, 0), 10)
	cv.imshow('cont_img', cont_img)
	print area
	print M['m10'] / M['m00']
	print M['m01'] / M['m00']
	if img_show:
		cv.imshow('he_2', img)
		cv.imshow('grey', thresh)
	cv.waitKey(0)
	cv.destroyAllWindows()
else:
	print 'file not exist'
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
