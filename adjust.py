import math
import cv2
import numpy as np
import openslide
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
# curPath = os.path.abspath(os.path.dirname(__file__))
# rootPath = os.path.split(curPath)[0]
# sys.path.append(rootPath)


def adjusting(image, adjust):
	width, height, xchange, ychange, xcenter, ycenter, angle, scale = adjust
	M = np.float32([[1, 0, xchange], [0, 1, ychange]])
	image = cv2.warpAffine(image, M, (width, height))
	M = cv2.getRotationMatrix2D((xcenter, ycenter), angle, scale)
	image = cv2.warpAffine(image, M, (width, height))
	yret, image = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
	return image


def densityprocess(slide, level):
	n = 21
	if level > slide.level_count - 1:
		level = slide.level_count - 2
	if slide.level_count > 7:
		level = slide.level_count - 5
	workingDimensions = slide.level_dimensions[level]
	img = np.array(slide.read_region((0, 0), level, workingDimensions))
	img = cv2.resize(img, (
	workingDimensions[0] / (workingDimensions[0] / 1000), workingDimensions[1] / (workingDimensions[0] / 1000)),
	                 cv2.INTER_CUBIC)
	grey = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
	greyret, greyimg = cv2.threshold(grey, 225, 255, cv2.THRESH_BINARY_INV)
	averagegreyimg = cv2.blur(greyimg, (n, n))
	
	surf = cv2.xfeatures2d.SURF_create(5000)
	kp, des = surf.detectAndCompute(averagegreyimg, None)
	return {'key': kp, 'des': des, 'dimensions': (
	workingDimensions[0] / (workingDimensions[0] / 1000), workingDimensions[1] / (workingDimensions[0] / 1000))}


def fibrosis(slide, dimension, fibrosislevel, threshold):
	n = 11
	workingDimensions = slide.level_dimensions[fibrosislevel]
	img = np.array(slide.read_region((0, 0), fibrosislevel, workingDimensions))
	rr, gg, bb, aa = cv2.split(img)
	rgbimg = cv2.merge((bb, gg, rr))
	hsv = cv2.cvtColor(rgbimg, cv2.COLOR_BGR2HSV)
	hsv = cv2.inRange(hsv, (90, 20, 20), (140, 255, 255))
	hsv = cv2.blur(hsv, (n, n))
	ret, hsv = cv2.threshold(hsv, threshold, 255, cv2.THRESH_BINARY)
	return cv2.resize(hsv, dimension, cv2.INTER_CUBIC)


def totaldensity(slide):
	maxLevel = slide.level_count - 1
	if maxLevel > 6:
		workingLevel = maxLevel - 6
	else:
		workingLevel = 1
	workingDimensions = slide.level_dimensions[workingLevel]
	img = np.array(slide.read_region((0, 0), workingLevel, workingDimensions))
	
	grey = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
	greyret, greyimg = cv2.threshold(grey, 225, 255, cv2.THRESH_BINARY_INV)
	
	b, g, r, a = cv2.split(img)
	rgbimg = cv2.merge((r, g, b))
	hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
	fibrosis = cv2.inRange(hsv, (90, 50, 50), (140, 255, 255))
	
	total = cv2.countNonZero(greyimg)
	fibNumber = cv2.countNonZero(fibrosis)
	return {'total': total, 'fibrosis': fibNumber, 'totaldensity': float(fibNumber) / float(total)}


def areaaveragedensity(fibrosis, grey, mask):
	areafibrosis = cv2.subtract(fibrosis, cv2.subtract(255, mask))
	areagreyimg = cv2.subtract(grey, cv2.subtract(255, mask))
	total = cv2.countNonZero(areagreyimg)
	fibNumber = cv2.countNonZero(areafibrosis)
	return float(fibNumber) / float(total)


def rotate(point, center, angle):
	if len(point) == 1:
		if point[0][0] - center[0] == 0:
			if point[0][1] - center[1] > 0:
				oldangle = math.pi / 2
			else:
				oldangle = -math.pi / 2
		else:
			if point[0][0] - center[0] > 0:
				oldangle = math.atan((point[0][1] - center[1]) / (point[0][0] - center[0]))
			else:
				oldangle = math.pi + math.atan((point[0][1] - center[1]) / (point[0][0] - center[0]))
		r = math.sqrt((point[0][1] - center[1]) * (point[0][1] - center[1]) + (point[0][0] - center[0]) * (
					point[0][0] - center[0]))
		newangle = oldangle + (angle * math.pi / 180)
		nx = r * math.cos(newangle) + center[0]
		ny = r * math.sin(newangle) + center[1]
		point = [[int(nx), int(ny)]]
		return point
	else:
		if point[0] - center[0] == 0:
			if point[1] - center[1] > 0:
				oldangle = math.pi / 2
			else:
				oldangle = -math.pi / 2
		else:
			if point[0] - center[0] > 0:
				oldangle = math.atan((point[1] - center[1]) / (point[0] - center[0]))
			else:
				oldangle = math.pi + math.atan((point[1] - center[1]) / (point[0] - center[0]))
		r = math.sqrt((point[1] - center[1]) * (point[1] - center[1]) + (point[0] - center[0]) * (point[0] - center[0]))
		newangle = oldangle + (angle * math.pi / 180)
		nx = r * math.cos(newangle) + center[0]
		ny = r * math.sin(newangle) + center[1]
		point = [int(nx), int(ny)]
		return point


def rotatePoints(points, center, angle):
	for i in range(0, len(points)):
		points[i] = rotate(points[i], center, angle)
	return points
