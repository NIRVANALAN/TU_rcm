# import cv2
# import numpy as np
# from . import module
import sys
import os
# curPath = os.path.abspath(os.path.dirname(__file__))
# rootPath = os.path.split(curPath)[0]
# sys.path.append(rootPath)
print(__file__)
curPath = os.path.abspath(os.path.dirname(__file__))
print(curPath)
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]

print(rootPath)
sys.path.append(rootPath)
print(sys.path)

# firstmask, secondmask, thirdmask, othermask = module.editareaHE(7,)



'''
img = cv2.imread('test_images/rgbimg.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(img, 127, 255, 0)
image, contours, hierarchy = cv2.findContours(thresh, 1, 2)
cnt = contours[0]
M = cv2.moments(cnt)
print (M)
cx = int(M['m10'] / M['m00'])
cy = int(M['m01'] / M['m00'])
print cx
print cy
img = cv2.drawContours(img, contours, -1, (0, 0, 255), 3)
cv2.imshow("test_images", img)
print (cv2.contourArea(contours[1]))
cv2.waitKey(0)
cv2.destroyAllWindows()
'''

