# coding=utf-8
from multiprocessing.dummy import Pool as ThreadPool
from rcm import *

he_dir = os.getcwd() + "/HE_data"
masson_dir = os.getcwd() + "/MASSON_data"


def persist(patient_id, slide_type, set_start_row=False):
	file_path = []
	if slide_type is "MASSON":
		indexes = os.listdir(masson_dir)
		# indexes.sort(key=lambda file_name: int(file_name[:5]))
		# indexes.sort(key=lambda file_name: int(file_name[11:12]))
		indexes.sort()
		for index in indexes:
			if (index.split("_")[0]) == (patient_id.split("/")[1]):  # no fibrosis_block.txt
				file_path.append(index)
	else:
		indexes = os.listdir(he_dir)
		# indexes.sort(key=lambda file_name: int(file_name[:5]))
		# indexes.sort(key=lambda file_name: int(file_name[11:12]))
		indexes.sort()
		for index in indexes:
			if (index.split("_")[0]) == (patient_id.split("/")[1]):
				file_path.append(index)
	for f in file_path:
		try:
			xls_persist_slide(f, slide_type, set_start_row)
		except:
			traceback.print_exc()
	pass


# write test image

def run(start_patient, end_patient, replenish=None, he=True, masson=False, server=False, file_type='.ndpi',
        slide_type='RCM'):
	if replenish is not None:
		args = [start_patient - 1, replenish[0], replenish[1], he, masson,
		        True, server, file_type, slide_type]
		slide_proc(args)
	for i in xrange(start_patient, end_patient):
		args = [start_patient - 1, 0, 6, he, masson,
		        True, server, file_type, slide_type]
		slide_proc(args)
	pass


def run_parallel_slide_proc(start_patient, end_patient, replenish=None, he=True, masson=False, server=False,
                            file_type='.ndpi', slide_type='RCM', threads=12):
	pool = ThreadPool(threads)
	task_list = []
	
	if replenish is not None:
		task_list.append(
			[start_patient - 1, replenish[0], replenish[1], he, masson, True, server, file_type, slide_type])
	# slide_proc(patient_id=start_patient - 1, start=replenish[0], end=replenish[1], he=he, masson=masson,
	#            set_hand_drawn=True, server=server, file_type=file_type)
	for i in xrange(start_patient, end_patient):
		task_list.append([i, 0, 6, he, masson, True, server, file_type, slide_type])
	# slide_proc(patient_id=i, start=0, end=6, he=he, masson=masson, set_hand_drawn=True, server=server,
	#            file_type=file_type)
	pool.map(slide_proc, task_list)
	pool.close()
	pool.join()
	pass


def run_parallel_base_proc(start_patient, end_patient, replenish=None, he=True, masson=False, server=False,
                           file_type='.mrxs', slide_type='RCM', threads=18):
	pool = ThreadPool(threads)
	slide_task_list = []
	
	if replenish is not None:
		slide_task_list.append(
			[start_patient - 1, replenish[0], replenish[1], he, masson, True, server, file_type, slide_type])
	# slide_proc(patient_id=start_patient - 1, start=replenish[0], end=replenish[1], he=he, masson=masson,
	#            set_hand_drawn=True, server=server, file_type=file_type)
	for i in xrange(start_patient, end_patient):
		slide_task_list.append([i, 0, 6, he, masson, True, server, file_type, slide_type])
	# slide_proc(patient_id=i, start=0, end=6, he=he, masson=masson, set_hand_drawn=True, server=server,
	#            file_type=file_type)
	
	he_task_list = []
	masson_task_list = []
	for i in slide_task_list:
		patient_id, start, end, he, masson, set_hand_drawn, server, file_type, slide_type = i
		he_slide_path, masson_slide_path = get_patient_image_path(patient_id, file_type=file_type, is_he=he,
		                                                          is_masson=masson,
		                                                          slide_type=slide_type)  # patient's image path
		for slide_no in xrange(start, end):
			if he:
				processed_index_he = 0
				# try:
				for split_path in he_slide_path[1]:
					if int(split_path[-5]) == slide_no + 1:
						processed_index_he = he_slide_path[1].index(split_path)
						he_task_list.append(
							[slide_no, he_slide_path[0][processed_index_he], patient_id, set_hand_drawn,
							 split_path if set_hand_drawn else None, server, slide_type])
				continue
			# except BaseException, e:
			# 	print e.message
			# 	with open('he_error_slide_log.txt', 'a') as f:
			# 		f.writelines(he_slide_path[0][processed_index_he] + '：' + e.message + '\n')
			# 	continue
			if masson:
				processed_index_masson = 0
				# try:
				for split_path in masson_slide_path[1]:
					if int(split_path[-5]) == slide_no + 1:
						processed_index_masson = masson_slide_path[1].index(split_path)
						masson_task_list.append([slide_no, masson_slide_path[0][processed_index_masson], patient_id,
						                         6, set_hand_drawn, split_path if set_hand_drawn else None, slide_type])
	# masson_proc()
	
	# except BaseException, e:
	# 	print e.message
	# 	with open('masson_error_slide_log.txt', 'a') as f:
	# 		f.writelines(masson_slide_path[0][processed_index_masson] + '：' + e.message + '\n')
	# 		continue
	
	# pool.map(slide_proc, slide_task_list)
	if he:
		pool.map(try_he_proc, he_task_list)
	if masson:
		pool.map(try_masson_proc, masson_task_list)
	pool.close()
	pool.join()
	pass


if __name__ == '__main__':
	init_test_proc()
	# masson_test_proc()
	# ============= write test images ================= #
	# MASSON: 41
	# HE : 20
	# for i in xrange(41, 42):  # MASSON RCM
	# for i in xrange(18, 20):  # HE RCM
	# for i in xrange(0, 20):  # HE RCM
	# for i in xrange(0, 4):  # HE RCM
	# for i in xrange(14, 16):  # HE HCM
	# for i in xrange(0, 1):  # MASSON DCM
	# for i in xrange(0, 12):  # MASSON HCM
	# 	# MASSON:
	# 	slide_path = get_patient_image_path(i, return_type="MASSON", file_type='.mrxs',
	# 	                                    for_split=True, is_masson=True, is_he=False, slide_type='DCM')
	# 	write_test_img(slide_path[0], is_masson=True, saved_img_level=6)
	
	# HE
	# 	slide_path = get_patient_image_path(i, return_type="HE", file_type='.mrxs',
	# 	                                    for_split=True, is_masson=False, is_he=True, slide_type='HCM')
	# 	write_test_img(slide_path[0], is_masson=False, saved_img_level=6)
	#
	# ===================================================#
	
	# persist process begin#################
	# for i in xrange(3, 4):
	# 	slide_proc(patient_id=i, start=3, end=6, he=True, masson=False, set_hand_drawn=True)
	
	# ================ RUN ================= #
	# run(15, 20, replenish=(0, 6), server=False, he=True, masson=False, file_type='.mrxs', slide_type='DCM')
	
	# run(27, 27, replenish=(2, 3), server=False, he=False, masson=True, file_type='.mrxs', slide_type='RCM')
	
	# run(4, 13, replenish=(1, 6), server=False, he=False, masson=True, file_type='.mrxs', slide_type='NORMAL')
	# run(9, 10, replenish=(0, 6), server=False, he=False, masson=True, file_type='.mrxs', slide_type='RCM')
	# run(1, 1, replenish=(0, 6), server=False, he=False, masson=True, file_type='.mrxs', slide_type='DCM')
	# run_parallel(26, 27, replenish=(0, 6), server=True, he=False, masson=True, file_type='.mrxs', slide_type='RCM')
	# run_parallel(0, 12, replenish=None, server=True, he=False, masson=True, file_type='.mrxs', slide_type='NORMAL')
	# run_parallel_slide_proc(0, 4, replenish=None, server=True, he=False, masson=True, file_type='.mrxs',
	#                         slide_type='HCM')
	
	# MASSON
	# hcm 12
	# dcm 26
	# normal 12
	# rcm 26
	run_parallel_base_proc(0, 26, replenish=None, server=True, he=False, masson=True, file_type='.mrxs',
	                       slide_type='RCM')
	#  HE
	# run_parallel_base_proc(15, 16, replenish=None, server=True, he=True, masson=False, file_type='.mrxs',
	#                        slide_type='HCM')
	
	# ================ RUN ==================#
	
	# ================ PERSIST ===============#
	# for i in range(0, 26):
	# 	persist(masson_patients[1][i], slide_type="MASSON")  # HCM
	#
	# persist(masson_patients[0][i], slide_type="MASSON") # RCM
	#	persist(masson_patients[3][i], slide_type="MASSON") # DCM
	# persist(masson_patients[i], slide_type="HE")
	# for i in range(0, 4):
		# RCM HCM NORMAL DCM
		# persist(he_patient s[0][i], slide_type="HE")  # RCM
		# persist(he_patients[3][i], slide_type="HE")  # DCM
		# persist(he_patients[1][i], slide_type="HE")  # HCM
		# persist(he_patients[2][i], slide_type="HE")  # HCM
	# ================ PERSIST ===============#/
	
	'''
	deal with hand_drawn pics
	'''
	# image_path = '/home/zhourongchen/lys/rcm_project/fortest/test_code/HE_image/25845/whole/25845_slide0.jpg'
	# image_path = '/home/zhourongchen/lys/rcm_project/fortest/test_images/HE/29708/test_35730-2_LI.jpg'
	# image_path = '/home/zhourongchen/lys/rcm_project/fortest/test_images/HE/29708/test_29708-1_LI2.jpg'
	# for test only
	# he_test_proc()
	# for i in xrange(2, 3):
	# slide_proc(patient_id=i, start=0, end=1, he=True, masson=False, set_hand_drawn=True, hand_drawn_img=image_path)
	# he_slide_path, masson_slide_path = get_image_path(i)
	# write_test_img(he_slide_path, saved_img_level=6)
	
	# persist(he_patients[1], slide_type="HE")
	
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
