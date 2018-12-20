# coding=utf-8
import sys
import os
from scipy.stats import iqr

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from module import *

# img_dir = 'G:\Junior\Tsinghua research\rcm_images\\'


# beilv = dimension[0] / mason['dimensions'][0]
countbodyMax = 0
meanmax = 0
detectmax = 0
avermax = 0
numbermax = 0

slide_he = []

# cv2.imshow('hsv', hsv)
# body = cv2.inRange(hsv, (0, 40, 0), (180, 255, 255))
# cv2.imshow('body', body)
# countbody = cv2.countNonZero(body)
# cv2.imshow("body", body)

# N, W = detectprocess(region, hsv)
slide_masson = []
max_level = 0
working_level = 0
dimension = ()
working_dimension = ()
he_result_iter = [[], [], [], ]
he_whole_res = []
he_path = []
masson_path = []

img_dir = './../../rcm_images/'
patients = ['/25845', '/28330', '/29708', '/30638', '/31398', '/35485']
patient_id = 1


def init():
    # kk = 1
    # name = '25845-' + str(kk)
    # he_img_name = name + '.ndpi'
    patient = patients[0]
    global he_path
    global masson_path
    for i in xrange(1, 7):
        img_name = patient + '-' + str(i) + '.ndpi'
        he_path_iter = img_dir + 'HE' + patient + img_name
        masson_path_iter = img_dir + 'MASSON' + patient + img_name
        he_path.append(he_path_iter)
        masson_path.append(masson_path_iter)
    global slide_he
    global slide_masson
    slide_he = openslide.open_slide(he_path[0])
    slide_masson = openslide.open_slide(masson_path[0])
    global dimension
    global max_level
    dimension = slide_he.dimensions
    '''
    dimension (81920L, 65536L)
    (1280L, 1024L)
    '''
    # print "dimension", dimension
    max_level = slide_he.level_count - 1
    n = 21
    global working_level
    working_level = max_level - 4
    global working_dimension
    working_dimension = slide_he.level_dimensions[max_level]
    # print workingDimensions
    print "init finished, working dimension: ", working_dimension, "working level:", max_level


masson_erosion_iteration_time_list = [10, 10, 15, 15, 15, 13]
he_erosion_iteration_time_list = [3, 3, 8, 3, 13, 9]  # for specifications


def he_test_proc():
    # print dimension
    # whole_level = 6
    # print "he_test_proc_dimension:", max_level
    slide_no = 5
    global slide_he
    global slide_masson
    slide_he = openslide.open_slide(he_path[slide_no])
    # slide_masson = openslide.open_slide(masson_path[slide_no])
    firstmask, secondmask, thirdmask, othermask, rcm_thickening = edit_area(6, slide_he, he_erosion_iteration_time_list,
                                                            masson_erosion_iteration_time_list, slide_no,
                                                            is_masson=False)

    def write_test_img(is_masson=False):
        if is_masson is False:
            path = he_path
            img_dir_path = './../test_images/HE/'
        else:
            path = masson_path
            img_dir_path = './../test_images/MASSON/'
        for i in path:
            slide_iter = openslide.open_slide(i)
            whole_dimension = slide_iter.level_dimensions[working_level]
            region = np.array((slide_iter.read_region((0, 0), working_level, whole_dimension)))
            region = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
            # cv2.imshow(i, region)
            img_path_iter = img_dir_path + i.split('/')[-2]
            if not os.path.exists(img_path_iter):
                os.mkdir(img_path_iter)
            cv2.imwrite(img_path_iter + '/' + i.split('/')[-1] + '.jpg', region)

    # write_test_img(is_masson=True)
    # region = np.array(slide_he.read_region((30000, 30000), 0, (1000, 1000)))
    # region = np.array(slide.read_region((0, 0), 0, (1000, 1000)))
    # region = cv2.cvtColor(region, cv2.COLOR_RGBA2BGR)
    # cv2.imshow("region", region)
    # hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

    # cv2.imshow("origin", hsv)
    # h, s, v = cv2.split(hsv)
    # res, s = cv2.threshold(s, 20, 255, cv2.THRESH_BINARY)

    # lower = np.array([0, 20, 100])
    # upper = np.array([255, 180, 255])
    # mask = cv2.inRange(hsv, lower, upper)
    # res = cv2.bitwise_and(hsv, hsv, mask)
    # cv2.imshow("res", res)

    # detect = detectprocess(region, hsv)

    # def getpos(event, x, y, flags, param):
    #     if event == cv2.EVENT_LBUTTONDOWN:
    #         print(hsv[y, x])

    # cv2.imshow('HSV', hsv)
    # cv2.setMouseCallback('HSV', getpos)
    # print detect
    # return detect
    pass


# whole_img = slide.read_region((0, 0), 0, dimension)

# print firstmask
he_mask_name = ['firstmask', 'secondmask', 'secondmask', 'secondmask', 'whole']


def he_proc():
    global he_result_iter
    he_slide_no = 0
    firstmask, secondmask, thirdmask, othermask = edit_area(max_level, slide_he, he_erosion_iteration_time_list,
                                                            masson_erosion_iteration_time_list, he_slide_no)
    global he_mask_name
    areas = [firstmask, secondmask, thirdmask, othermask]
    magnify = pow(2, max_level)
    area_length = 500
    i = 0
    for area in areas:
        for y in range(0, dimension[1] - 1000, 1000):
            for x in range(0, dimension[0] - 1000, 1000):
                # if whole_img[x * magnify + 500][y * magnify + 500] != 0:
                if firstmask[int((y + area_length) / magnify)][int((x + area_length) / magnify)] != 0:
                    print x, y
                    region = np.array(slide_he.read_region((x, y), 0, (1000, 1000)))
                    region = cv2.cvtColor(region, cv2.COLOR_RGBA2BGR)
                    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
                    detect = detectprocess(region, hsv)
                    he_result_iter[0] += (detect[0])
                    he_result_iter[1] += (detect[1])
                    he_result_iter[2] += (detect[2])
                    he_result_iter[3] += (detect[3])
                    he_result_iter[4].append(detect[4])
        print (he_mask_name[i], ' : ', sum(he_result_iter[0]), sum(he_result_iter[1]), sum(he_result_iter[2]),
               sum(he_result_iter[3]))
        i += 1
        he_whole_res.append(he_result_iter)
        he_result_iter = [[], [], [], ]


def he_statics_persistence(res):
    global he_mask_name
    index = 0
    print len(res)
    for i in xrange(len(res)):
        cardiac_cells_num = res[index][1]
        non_cardiac_cells_num = res[index][2]
        vacuole_num = res[index][0]
        region_area = res[index][3]
        cardiac_cells_nucleus_area = [i[0] for i in res[index][4]]
        cardiac_cells_nucleus_perimeter = [i[1] for i in res[index][4]]

        cardiac_cells_ratio = non_cardiac_cells_num / float(cardiac_cells_num)
        cardiac_area_num_ratio = region_area / float(cardiac_cells_num)

        #  cardiac cell nucleus statics
        # mean
        cardiac_cells_nucleus_area_mean = np.mean(cardiac_cells_nucleus_area)
        # median
        cardiac_cells_nucleus_area_median = np.median(cardiac_cells_nucleus_area)
        # SD
        cardiac_cells_nucleus_area_sd = np.std(cardiac_cells_nucleus_area, ddof=1)
        # IQR
        cardiac_cells_nucleus_area_iqr = iqr(cardiac_cells_nucleus_area, rng=(25, 75), interpolation='midpoint')

        # perimeter calculation
        cardiac_cells_nucleus_perimeter_mean = np.mean(cardiac_cells_nucleus_perimeter)
        cardiac_cells_nucleus_perimeter_median = np.median(cardiac_cells_nucleus_perimeter)
        cardiac_cells_nucleus_perimeter_sd = np.std(cardiac_cells_nucleus_perimeter, ddof=1)
        cardiac_cells_nucleus_perimeter_iqr = iqr(cardiac_cells_nucleus_perimeter, rng=(25, 75),
                                                  interpolation='midpoint')

        # nucleus / whole_area 细胞核总数量/切片总面积
        # intensity = cardiac_cells_num/float(region_area)

        # area ratio  心肌细胞核面积占心肌细胞的面积比例
        cardiac_cells_nucleus_area_region_ratio = float(sum(cardiac_cells_nucleus_area)) / region_area

        # vacuole calculation
        cardiac_cells_vacuole_area_mean = np.mean(vacuole_num)
        cardiac_cells_vacuole_area_median = np.median(vacuole_num)
        cardiac_cells_vacuole_area_sd = np.std(vacuole_num, ddof=1)

        print 'region: ' + he_mask_name[index]
        print 'Cardiac cells num: ' + str(res[index][1])
        print 'vacuole cells num: ' + str(res[index][0])
        print 'Non-cardiac cells num: ' + str(res[index][2])
        print 'region area: ' + he_mask_name[index] + str(res[index][3])

    # print
    pass


# for masson proc later
cardiac_threshold = (155, 140, 50), (175, 230, 255)  # cardiac
fibrosis_threshold = (90, 20, 20), (140, 255, 255)  # fibrosis

masson_result_iter = [[], [], []]
masson_whole_result = []
masson_mask_name = ['firstmask', 'secondmask', 'secondmask', 'secondmask', 'whole']


def masson_proc(slide=slide_masson, working_level=6):  # need debug and fix
    global masson_result_iter
    # i = 5
    print working_level
    working_dimensions = slide.level_dimensions[working_level]
    firstmask, secondmask, thirdmask, othermask, grey_img, hsv, fibrosis_img = edit_area(working_level, slide,
                                                                                        masson_erosion_iteration_time_list=masson_erosion_iteration_time_list,
                                                                                        is_masson=True)
    areas = [firstmask, secondmask, thirdmask, othermask]
    magnify = pow(2, max_level)
    area_length = 250
    for area in areas:
        for y in range(0, working_dimensions[1] - 500, 500):
            for x in range(0, working_dimensions[0] - 500, 500):
                if firstmask[int((y + area_length) / magnify)][int((x + area_length) / magnify)] != 0:
                    print x, y
                    _, cardiac_area = masson_region_slide(slide, working_level, cardiac_threshold, (x, y),
                                                          is_debug=False,
                                                          dimension=(500, 500))
                    _, fibrosis_area = masson_region_slide(slide, working_level, fibrosis_threshold, (x, y),
                                                           is_debug=False, dimension=(500, 500))
                    # fat area here
                    masson_result_iter[0] += cardiac_area
                    masson_result_iter[1] += fibrosis_area
        masson_whole_result.append(masson_result_iter)
        masson_result_iter = [[], [], []]
        print masson_mask_name[i] + " finished"
        i += 1
    # fibrosis area
    # fat area
    # cardiac cell area
    pass


def masson_test_proc(working_level=6):
    global slide_he
    global slide_masson
    print 'working level', working_level
    working_dimension = slide_masson.level_dimensions[working_level]
    # cardiac_threshold = (155, 140, 50), (175, 230, 255)  # cardiac
    # fibrosis_threshold = (90, 20, 20), (140, 255, 255)  # fibrosis

    # hsv = []
    # rgb_img = []

    def pure_test():
        # global hsv
        # global rgb_img
        # region = np.array(slide_masson.read_region((30000, 30000), 0, (1000, 1000)))
        region = np.array(slide_masson.read_region((40000, 50000), 0, (1000, 1000)))
        r, g, b, a = cv2.split(region)
        bgr_img = cv2.merge((b, g, r))
        hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
        res_fibrosis_hsv = cv2.inRange(hsv, fibrosis_threshold[0], fibrosis_threshold[1])  # s 50-255 in paper fibrosis
        res_cardiac_hsv = cv2.inRange(hsv, cardiac_threshold[0], cardiac_threshold[1])  # cardiac threshold

        cv2.imshow('HSV', hsv)
        cv2.imshow('res_cardiac_HSV', res_cardiac_hsv)
        cv2.imshow('res_fibrosis_hsv', res_fibrosis_hsv)
        cv2.imshow('rgb_masson', bgr_img)

        def getpos(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                print(hsv[y, x])

        cv2.setMouseCallback('HSV', getpos)

    # pure_test()
    slide_no = 0
    # slide_he = openslide.open_slide(he_path[slide_no])
    slide_masson = openslide.open_slide(masson_path[slide_no])
    firstmask, secondmask, thirdmask, othermask, greyimg, hsv, fibrosis_img, rcm_thickening = edit_area(working_level, slide_masson,
                                                                                        masson_erosion_iteration_time_list=masson_erosion_iteration_time_list,
                                                                                        slide_no=slide_no,
                                                                                        is_masson=True)


# hsv = cardiac_cell_slide(slide_masson, 0, start_pos=(40000, 40000), is_debug=True, dimension=(1000, 1000))


# cv2.imshow('masson_region', bgr_img)


# cv2.imshow('origin', region)
# fibrosis_hsv = fibrosis_slide(slide_masson, working_level, (30000, 30000), is_debug=True)
# cv2.imshow('masson_fibrosis_hsv', fibrosis_hsv)


# fibrosis_slide()


# working_dimensions = slide2.level_dimensions[working_level]
# print working_dimensions
# img = np.array(slide2.read_region((0, 0), working_level, working_dimensions))
# cv2.imshow('masson_img', img)
# print areaaveragedensity(fibrosis_img, greyimg, firstmask)
# pass

if __name__ == '__main__':
    init()

    # masson_proc()
    masson_test_proc()
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # he test_images
    # he_test_proc()
    # he_whole_res.append(he_test_proc())
    # he_statics_persistence(he_whole_res)
    # 空泡 心肌细胞核 非心肌细胞核 区域总面积 列表[编号，细胞核面积，细胞核周长]
    cv2.waitKey(0)
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
