# coding=utf-8
from rcm import *

he_dir = os.getcwd() + "/HE_data"
masson_dir = os.getcwd() + "/MASSON_data"


def persist(patient_id, slide_type, set_start_row=False):
	file_path = []
	if slide_type is "MASSON":
		for index in os.listdir(masson_dir):
			if int(index.split("_")[0]) == int(patient_id.split("/")[1]):
				file_path.append(index)
	else:
		for index in os.listdir(he_dir):
			if int(index.split("_")[0]) == int(patient_id.split("/")[1]):
				file_path.append(index)
	for f in file_path:
		xls_persist_slide(f, slide_type, set_start_row)
	pass


# write test image


if __name__ == '__main__':
	init_test_proc()
	# for i in xrange(1, 3):
	# 	he_slide_path, masson_slide_path = get_image_path(i)
	# 	write_test_img(masson_slide_path, is_masson=False)
	# persist process begin#################
	for i in xrange(2, 3):
		# slide_proc(patient_id=0, start=0, end=1, he=False, masson=True)
		# persist(he_patients[1], slide_type="HE")
		persist(masson_patients[i], slide_type="MASSON")
	
	# masson_test_proc()
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()
	
	# he test_images
	# he_test_proc()
	# he_whole_res.append(he_test_proc())
	# he_statics_persistence(he_whole_res)
	# 空泡 心肌细胞核 非心肌细胞核 区域总面积 列表[编号，细胞核面积，细胞核周长]
	# cv2.waitKey(0)
	cv2.destroyAllWindows()
	
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
# cv2.imwrite("test_images/he_rgbimg.jpg", rgbimg)
# hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
# cv2.imwrite("test_images/he_hsv.jpg", hsv)
# greyimg = cv2.inRange(hsv, (0, 20, 0), (180, 255, 255))
# cv2.imwrite("test_images/he_grey.jpg", greyimg)

# fibrosis = cv2.inRange(hsv, (90, 20, 0), (150, 255, 255))
# cv2.imshow("fibrosis",fibrosis)
# averagegreyimg = cv2.blur(greyimg, (30, 30))
# cv2.imshow('he_average grey img', averagegreyimg)
# cv2.imwrite("test_images/he_average_grey_img.jpg", averagegreyimg)

# ret, erode = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
# erode = cv2.adaptiveThreshold(averagegreyimg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
# erode = cv2.erode(erode, kernel, iterations=13)
# cv2.imshow("after erosion", erode)
# cv2.imwrite("test_images/he_after_erosion.jpg", erode)

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
