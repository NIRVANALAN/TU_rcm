import cv2
import openslide
import numpy as np
from coop import *

img_dir = 'G:\Junior\Tsinghua research\images\\'
kk = 1
name = '25845-' + str(kk)
he_imgname = name + '.ndpi'
patients = ['/25845', '/28330', '/29708', '/30638', '/31398', '/35485']
patient = patients[0]
imgname = patient + '-' + str(kk) + '.ndpi'

path = img_dir + 'HE\\' + patient + imgname
path1 = img_dir + 'MASSON\\' + patient + imgname

slide = openslide.open_slide(path)
slide2 = openslide.open_slide(path1)

# mason = averagefibrosis(slide, slide2)

dimension = slide.dimensions
print "dimension", dimension
result = [[], []]

# beilv = dimension[0] / mason['dimensions'][0]
countbodyMax = 0
meanmax = 0
detectmax = 0
avermax = 0
numbermax = 0

# region = numpy.array(slide.read_region((30000, 30000), 0, (1000, 1000)))
# region = cv2.cvtColor(region, cv2.COLOR_RGBA2BGR)
# cv2.imshow("region", region)
# hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
# cv2.imshow('hsv', hsv)
# body = cv2.inRange(hsv, (0, 40, 0), (180, 255, 255))
# cv2.imshow('body', body)
# countbody = cv2.countNonZero(body)
# cv2.imshow("body", body)

# N, W = detectprocess(region, hsv)

max_level = slide.level_count - 1
n = 21
level = max_level - 4
workingDimensions = slide.level_dimensions[level]
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

img = np.array(slide.read_region((0, 0), level, workingDimensions))

b, g, r, a = cv2.split(img)
rgbimg = cv2.merge((r, g, b))
cv2.imwrite("test/he_rgbimg.jpg", rgbimg)
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
cv2.imwrite("test/he_hsv.jpg", hsv)
greyimg = cv2.inRange(hsv, (0, 20, 0), (180, 255, 255))
cv2.imwrite("test/he_grey.jpg", greyimg)

fibrosis = cv2.inRange(hsv, (90, 20, 0), (150, 255, 255))
# cv2.imshow("fibrosis",fibrosis)
averagegreyimg = cv2.blur(greyimg, (30, 30))
# cv2.imshow('he_average grey img', averagegreyimg)
cv2.imwrite("test/he_average_grey_img.jpg", averagegreyimg)

ret, erode = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
# erode = cv2.adaptiveThreshold(averagegreyimg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
erode = cv2.erode(erode, kernel, iterations=13)
# cv2.imshow("after erosion", erode)
cv2.imwrite("test/he_after_erosion.jpg", erode)

# cv2.imshow("")
# get rid of XIAOLIANG

ret, averimage = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
averimage, avercnts, averhierarchy = cv2.findContours(averimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cv2.imshow("aver image", averimage)
# overall contour

image, cnts, hierarchy = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cv2.imshow("contour after erosion", erode)
# cv2.waitKey(0)
cv2.destroyAllWindows()
