import cv2 as cv
import numpy as np

rgb_img = cv.imread("test/he_rgbimg.jpg")
hsv = cv.cvtColor(rgb_img, cv.COLOR_RGB2HSV)
grey_img = cv.inRange(hsv, (0, 20, 0), (180, 255, 220))
cv.imshow("grey", grey_img)

averagegreyimg = cv.blur(grey_img, (30, 30))
# cv2.imshow('he_average grey img', averagegreyimg)
cv.imshow("he_average_grey_img.jpg", averagegreyimg)

ret, erode = cv.threshold(averagegreyimg, 120, 255, cv.THRESH_BINARY)
# erode = cv2.adaptiveThreshold(averagegreyimg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (4, 4))
erode = cv.erode(erode, kernel, iterations=3)
cv.imshow("erode", erode)

cv.waitKey(0)
cv.destroyAllWindows()
