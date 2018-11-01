# coding=utf-8
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from geshi import *
from math import *
from lxml import etree
from namefile import *
import time


class Annotations():
	'''
	文件的标记群
	'''
	
	def __init__(self, father):
		self.list = []
		self.father = father
		self.group = {}
		self.t = time.time()
		self.gap = 0.2
	
	def openAnnotation(self, fname, geshi):
		'''
		打开标记文件函数
		:param fname: 图片文件名
		:return:
		'''
		afname = fname[:-4] + ".xml"
		if not os.path.exists(afname):
			self.annoshowToolBar()
			return
		afile = etree.parse(afname)
		root = afile.getroot()
		for annos in root:
			if annos.tag == "Annotations":
				for anno in annos:
					self.list.append(
						Annotation(self.father, geshi, str(anno.get('PartOfGroup')) + ':' + anno.get('Name'),
						           anno.get('Type'), self))
					self.list[len(self.list) - 1].setColor(anno.get('Color'))
					for coors in anno:
						for coor in coors:
							self.list[len(self.list) - 1].list.append((float(coor.get('X')), float(coor.get('Y'))))
						self.list[len(self.list) - 1].list.append(
							(self.list[len(self.list) - 1].list[0][0], self.list[len(self.list) - 1].list[0][1]))
						self.list[len(self.list) - 1].ending()
		for i in self.list:
			i.update()
	
	def messageline(self, x, y, geshi):
		'''
		鼠标是否在标记线上函数
		:param x: 鼠标横坐标
		:param y: 鼠标纵坐标
		:param geshi: 当前图片视野参数
		:return: 选中标记们
		'''
		list = []
		for i in range(0, len(self.list)):
			ison = False
			if self.list[i].type == "Polygon" or self.list[i].type == "Rectangle":
				for j in range(0, len(self.list[i].list) - 1):
					x1 = (self.list[i].list[j][0] - geshi.x) / geshi.b + geshi.w / 2
					x2 = (self.list[i].list[j + 1][0] - geshi.x) / geshi.b + geshi.w / 2
					y1 = (self.list[i].list[j][1] - geshi.y) / geshi.b + geshi.h / 2
					y2 = (self.list[i].list[j + 1][1] - geshi.y) / geshi.b + geshi.h / 2
					if x1 != x2 or y1 != y2:
						if (x - x1) * (x - x2) <= 25 and (y - y1) * (y - y2) <= 25:
							if abs((y1 - y2) * x + (x2 - x1) * y + (x1 * y2 - x2 * y1)) / sqrt(
									(x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)) < 4:
								ison = True
			if self.list[i].type == "Ellipse" and len(self.list[i].list) > 0:
				ox = (self.list[i].list[0][0] + self.list[i].list[4][0]) / 2
				oy = (self.list[i].list[0][1] + self.list[i].list[4][1]) / 2
				a = abs(self.list[i].list[0][0] - self.list[i].list[4][0]) / 2
				b = abs(self.list[i].list[0][1] - self.list[i].list[4][1]) / 2
				xop = (ox - geshi.x) / geshi.b + geshi.w / 2
				yop = (oy - geshi.y) / geshi.b + geshi.h / 2
				aop = a / geshi.b
				bop = b / geshi.b
				if (aop > 0 and bop > 0 and (x - xop) * (x - xop) / aop / aop + (y - yop) * (
						y - yop) / bop / bop < 1.1 and (x - xop) * (x - xop) / aop / aop + (y - yop) * (
						    y - yop) / bop / bop > 0.9) or ((a == 0 or b == 0) and (x - xop == 0 and y - yop == 0)):
					ison = True
			if ison == True:
				self.list[i].ison(x, y + 20 + 10 * len(list))
				list.append(i)
			else:
				self.list[i].unon()
		return list
	
	def messagepoint(self, x, y, geshi, canchange):
		'''
		鼠标是否在点上函数
		:param x: 鼠标横坐标
		:param y: 鼠标纵坐标
		:param geshi: 当前视野参数
		:param canchange: 已选定标记们
		:return: 选中点,无返还(-1,-1)
		'''
		for i in canchange:
			for j in range(0, len(self.list[i].list)):
				xx = (self.list[i].list[j][0] - geshi.x) / geshi.b + geshi.w / 2
				yy = (self.list[i].list[j][1] - geshi.y) / geshi.b + geshi.h / 2
				if (x - xx) * (x - xx) + (y - yy) * (y - yy) < 49:
					return (i, j)
		return (-1, -1)
	
	def saveAnnotation(self, fname):
		'''
		标记保存函数
		:param fname:图片文件名
		:return:
		'''
		root = etree.Element("Image_Annotations")
		annos = etree.SubElement(root, "Annotations")
		annoslist = []
		for i in range(0, len(self.list)):
			if self.list[i].end:
				annoslist.append(etree.SubElement(annos, "Annotation"))
				if len(self.list[i].name.split(':')) == 2:
					annoslist[i].set("PartOfGroup", self.list[i].name.split(':')[0])
					annoslist[i].set("Name", self.list[i].name.split(':')[1])
				else:
					annoslist[i].set("Name", self.list[i].name)
					annoslist[i].set("PartOfGroup", "")
				annoslist[i].set("Type", self.list[i].type)
				annoslist[i].set("Color", self.list[i].opColor())
				coors = etree.SubElement(annoslist[i], "Coordinates")
				coorslist = []
				for j in range(0, len(self.list[i].list)):
					if j == 0 or self.list[i].list[j][0] != self.list[i].list[0][0] or self.list[i].list[j][1] != \
							self.list[i].list[0][1]:
						coorslist.append(etree.SubElement(coors, "Coordinate"))
						coorslist[j].set("Order", unicode(j))
						coorslist[j].set("X", unicode(self.list[i].list[j][0]))
						coorslist[j].set("Y", unicode(self.list[i].list[j][1]))
		annosgroup = etree.SubElement(root, "AnnotationGroups")
		for i, j in self.group.items():
			if j.text() != str(""):
				onegroup = etree.SubElement(annosgroup, "Group")
				onegroup.set("Name", j.text())
		tree = etree.ElementTree(root)
		afname = '%s.xml' % fname[:-4]
		afilename = QFileDialog.getSaveFileName(self.father, "选择路径", afname, "xml files(*.xml)")
		if len(afilename[0]) > 0:
			tree.write(afilename[0], encoding="utf-8", method="xml", pretty_print=True, xml_declaration=True)
			QMessageBox.warning(self.father, "Notice", "Saved!", QMessageBox.Cancel)
	
	def remove(self):
		'''
		删除最后标记函数
		:return:
		'''
		if len(self.list) > 0:
			self.list[len(self.list) - 1].hide()
			self.list[len(self.list) - 1].deleting()
			del self.list[len(self.list) - 1]
	
	def addAnnotation(self, geshi, x, y, type):
		'''
		增加标记函数
		:return:
		'''
		self.list.append(Annotation(self.father, geshi, "Annotation %d" % len(self.list), type, self))
		self.list[len(self.list) - 1].initpoint(x, y)
		self.list[len(self.list) - 1].show()
	
	def addPoint(self, geshi, x, y, type):
		'''
		增加标记点函数
		:param x: 总横坐标
		:param y: 总纵坐标
		:param k: 当前倍率(提供误差范围
		:return: 是否当前标记终点
		'''
		if type == "Polygon":
			if time.time() - self.t > self.gap:
				i = len(self.list) - 1
				while i > -1 and self.list[i].type != "Polygon":
					i -= 1
				if i == -1 or self.list[i].end:
					self.t = time.time()
					self.addAnnotation(geshi, x, y, type)
				else:
					self.t = time.time()
					if self.list[i].PaddPoint(x, y):
						self.t += 1
		if type == "Rectangle" or type == "Ellipse":
			self.addAnnotation(geshi, x, y, type)
	
	def set(self, geshi):
		'''
		刷新新视野后标记们函数
		:param geshi: 当前视野参数
		:return:
		'''
		for i in self.list:
			i.set(geshi)
	
	def __del__(self):
		'''
		深度删除
		:return:
		'''
		for i in self.list:
			i.hide()
			del i
	
	def hiding(self, group):
		'''
		标记隐藏函数(未使用)
		:return:
		'''
		for i in self.list:
			if i.group == group:
				i.hide()
	
	def showing(self, group):
		'''
		标记显示函数(未使用)
		:return:
		'''
		for i in self.list:
			if i.group == group:
				i.show()
	
	def annoshowToolBar(self):
		self.father.parent().annoshowToolbar.clear()
		annos = self.father.parent().annoshowToolbar.addAction("标注群:")
		annos.setDisabled(True)
		for i, j in self.group.items():
			self.father.parent().annoshowToolbar.addAction(j)


class Annotation(QWidget):
	'''
	一个标记
	'''
	
	def __init__(self, father, geshi, name, type, mother):
		super(Annotation, self).__init__(father)
		self.list = []
		self.mother = mother
		self.geshi = geshi
		self.setGeometry(QRect(0, 0, father.width(), father.height()))
		self.color = QColor(255, 0, 0)
		self.colorn = QColor(self.color)
		self.name = name
		if len(self.name.split(":")) == 2:
			self.group = self.name.split(":")[0]
		else:
			self.group = str("")
		self.type = type
		self.end = False
		self.show()
		self.ql = QLabel(self)
		self.setMouseTracking(True)
		self.ql.setMouseTracking(True)
		self.ql.setStyleSheet("background-color:yellow")
		self.ql.setText(self.name)
		self.ql.adjustSize()
		self.pcolor = QColor(0, 0, 255)
	
	def initpoint(self, x, y):
		if self.type == "Polygon":
			self.PaddPoint(x, y)
		if self.type == "Rectangle" or self.type == "Ellipse":
			self.REadd(x, y)
	
	def PaddPoint(self, x, y):
		'''
		增加标记点
		:param x:总横坐标
		:param y: 总纵坐标
		:return:
		'''
		if self.type == "Polygon" and not self.end:
			if len(self.list) > 0 and abs(x - self.list[0][0]) < 20 * self.geshi.b and abs(
					y - self.list[0][1]) < 20 * self.geshi.b:
				self.list.append(self.list[0])
				self.ending()
				return True
			else:
				self.list.append((x, y))
		return False
	
	def REadd(self, x, y):
		if self.type == "Rectangle" or self.type == "Ellipse":
			for i in range(0, 9):
				self.list.append((x, y))
			self.ending()
	
	def paintEvent(self, QPaintEvent):
		'''
		标记绘图函数
		:param QPaintEvent:绘图事件
		:return:
		'''
		if len(self.list) > 0:
			qp = QPainter()
			qp.begin(self)
			j = None
			for i in self.list:
				qp.setPen(QPen(self.pcolor, 10))
				qp.drawPoint((i[0] - self.geshi.x) / self.geshi.b + self.geshi.w / 2,
				             (i[1] - self.geshi.y) / self.geshi.b + self.geshi.h / 2)
				if self.type == "Polygon" or self.type == "Rectangle":
					if j is not None:
						qp.setPen(QPen(self.colorn, 5))
						qp.drawLine((j[0] - self.geshi.x) / self.geshi.b + self.geshi.w / 2,
						            (j[1] - self.geshi.y) / self.geshi.b + self.geshi.h / 2,
						            (i[0] - self.geshi.x) / self.geshi.b + self.geshi.w / 2,
						            (i[1] - self.geshi.y) / self.geshi.b + self.geshi.h / 2)
					j = i
			if self.type == "Ellipse":
				qp.setPen(QPen(self.colorn, 5))
				qp.drawEllipse((self.list[0][0] - self.geshi.x) / self.geshi.b + self.geshi.w / 2,
				               (self.list[0][1] - self.geshi.y) / self.geshi.b + self.geshi.h / 2,
				               (self.list[4][0] - self.list[0][0]) / self.geshi.b,
				               (self.list[4][1] - self.list[0][1]) / self.geshi.b)
			qp.end()
			self.raise_()
	
	def setPoint(self, j, x, y):
		'''
		重设点函数
		:param j: 序号
		:param x: 总横坐标
		:param y: 总纵坐标
		:return:
		'''
		if self.type == "Polygon":
			self.list[j] = (x, y)
			if j == 0 or j == 8:
				self.list[len(self.list) - 1] = self.list[0]
		if self.type == "Rectangle" or self.type == "Ellipse":
			if j == 0:
				self.list[0] = (x, y)
			elif j == 1:
				self.list[0] = (self.list[0][0], y)
			elif j == 2:
				self.list[0] = (self.list[0][0], y)
				self.list[4] = (x, self.list[4][1])
			elif j == 3:
				self.list[4] = (x, self.list[4][1])
			elif j == 4:
				self.list[4] = (x, y)
			elif j == 5:
				self.list[4] = (self.list[4][0], y)
			elif j == 6:
				self.list[0] = (x, self.list[0][1])
				self.list[4] = (self.list[4][0], y)
			elif j == 7:
				self.list[0] = (x, self.list[0][1])
			self.REresize()
		self.update()
	
	def REresize(self):
		if self.type == "Rectangle" or self.type == "Ellipse":
			x1, y1 = self.list[0]
			x2, y2 = self.list[4]
			self.list[1] = ((x1 + x2) / 2, y1)
			self.list[2] = (x2, y1)
			self.list[3] = (x2, (y1 + y2) / 2)
			self.list[5] = ((x1 + x2) / 2, y2)
			self.list[6] = (x1, y2)
			self.list[7] = (x1, (y1 + y2) / 2)
			self.list[8] = self.list[0]
	
	def set(self, geshi):
		'''
		刷新新视野后标记函数
		:param geshi:
		:return:
		'''
		self.geshi = geshi
		self.setGeometry(QRect(0, 0, self.geshi.w, self.geshi.h))
		self.update()
	
	def setColor(self, color):
		'''
		修改颜色函数
		:param color: 颜色(16进制#FFFFFF)
		:return:
		'''
		self.color.setNamedColor(color)
		self.colorn = QColor(self.color)
		self.update()
	
	def opColor(self):
		'''
		输出当前颜色函数
		:return: 颜色(16进制#FFFFFF)
		'''
		return self.color.name()
	
	def setName(self, name):
		'''
		修改标记名函数
		:param name:标记新名
		:return:
		'''
		if self.end:
			self.deleting()
		self.name = name
		if len(self.name.split(":")) == 2:
			self.group = self.name.split(":")[0]
		else:
			self.group = str("")
		if self.end:
			self.ending()
		self.ql.setText(self.name)
		self.ql.adjustSize()
	
	def chosed(self):
		'''
		被选中函数
		:return:
		'''
		self.pcolor = QColor(20, 20, 20)
		self.colorn.setRed(self.color.red() * 0.8)
		self.colorn.setGreen(self.color.green() * 0.8)
		self.colorn.setBlue(self.color.blue() * 0.8)
		self.update()
	
	def unchosed(self):
		'''
		取消选中函数
		:return:
		'''
		self.pcolor = QColor(0, 0, 255)
		self.colorn.setRed(self.color.red())
		self.colorn.setGreen(self.color.green())
		self.colorn.setBlue(self.color.blue())
		self.update()
	
	def ison(self, x, y):
		self.ql.setGeometry(x, y, 30, 10)
		self.ql.adjustSize()
		self.ql.show()
	
	def unon(self):
		self.ql.hide()
	
	def deleting(self):
		if self.mother.group.has_key(self.group):
			self.mother.group[self.group].num -= 1
			if self.mother.group[self.group].num == 0:
				del self.mother.group[self.group]
		self.mother.annoshowToolBar()
	
	def ending(self):
		self.end = True
		if self.mother.group.has_key(self.group):
			self.mother.group[self.group].num += 1
		else:
			self.mother.group[self.group] = Group(self.mother, self.group, self.parent().parent())
		self.mother.annoshowToolBar()


class Group(QAction):
	def __init__(self, father, name, mainWindow):
		super(Group, self).__init__(name, mainWindow)
		self.father = father
		self.setToolTip(name)
		self.triggered.connect(self.showorclose)
		self.setCheckable(True)
		self.setChecked(True)
		self.num = 1
	
	def showorclose(self):
		if not self.isChecked():
			self.father.hiding(self.text())
			self.setChecked(False)
		else:
			self.father.showing(self.text())
			self.setChecked(True)
