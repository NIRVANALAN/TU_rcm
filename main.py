# coding=utf-8
import os
import sys
import numpy
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import openslide
import resources
import cv2
from geshi import *
from show import *
from segway import *
from namefile import *
from annotation import *
import namefile
from adjust import *
from operator import itemgetter

_version_ = "1.0.0"


class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		
		# 基本变量
		self.filename = None
		self.slide = None
		self.slide2 = None
		self.picture = None
		self.before = None
		self.annotation = None
		self.ismouse = False
		self.ifleftbuttom = False
		self.ifseg = False
		self.ifabjust = False
		self.ifdetect = False
		self.ifaver = False
		
		self.haha = True
		self.ifpointanno = False
		self.ifrectanno = False
		self.ifellianno = False
		
		self.qpox = 0
		self.qpoy = 0
		self.point = (-1, -1)
		self.pro = []
		self.arg = []
		self.canchange = []
		self.statusBar()
		
		# 图片显示子部件
		self.imageLabel = QLabel()
		self.imageLabel.setAlignment(Qt.AlignCenter)
		self.imageLabel.setMouseTracking(True)
		self.imageLabel.setMinimumHeight(200)
		self.imageLabel.setMinimumWidth(200)
		self.imageLabel.show()
		# 主窗口中心只显示图片
		self.setCentralWidget(self.imageLabel)
		# 设置状态栏
		self.sizeLabel = QLabel()
		self.sizeLabel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
		status = self.statusBar()
		status.setSizeGripEnabled(False)
		status.addPermanentWidget(self.sizeLabel)
		status.showMessage("Ready", 5000)
		
		# 按钮群(标题,事件,快捷键,图标,提示信息)
		# 文件操作按纽群
		fileOpenAction = self.createAction("&打开图片", self.fileOpen, QKeySequence.Open, "fileopen", "打开图片")
		fileQuitAction = self.createAction("&退出", self.close, QKeySequence.Quit, "filequit", "退出")
		fileSaveAction = self.createAction("&保存标注", self.fileSave, QKeySequence.Save, "save", "保存标注")
		# 图片操作按钮群
		self.editSegAction = self.createAction(segway, self.editSeg, None, "blank5", segway, True)
		self.editDetectAction = self.createAction(detect, self.editDetect, None, "blank1", detect, True)
		self.editAbjustAction = self.createAction(adjust, self.editabjust, None, "blank2", adjust, True)
		self.editAreaAction = self.createAction(area, self.editarea, None, "blank3", area, False)
		self.editAreaActionHE = self.createAction(area, self.editareaHE, None, "blank3", area, False)
		self.editAverAction = self.createAction(aver, self.editAver, None, "blank4", aver, True)
		self.editPointAnnoAction = self.createAction(pointanno, self.editPointAnno, QKeySequence.Paste, "polygon",
		                                             pointanno, True)
		self.editRectAnnoAction = self.createAction(rectanno, self.editRectAnno, "Ctrl+R", "rectangle", rectanno, True)
		self.editElliAnnoAction = self.createAction(ellianno, self.editElliAnno, "Ctrl+E", "ellipse", ellianno, True)
		self.editAnnoCNAction = self.createAction(annoCN, self.editAnnoCN)
		self.editAnnoCCAction = self.createAction(annoCC, self.editAnnoCC)
		self.editAnnoDelAction = self.createAction(annoDel, self.editAnnoDel)
		# 图片缩放按钮群
		editZoominAction = self.createAction("&放大", self.editZoomin, QKeySequence.ZoomIn, "editzoomin", "放大")
		editZoomoutAction = self.createAction("&缩小", self.editZoomout, QKeySequence.ZoomOut, "editzoomout", "缩小")
		# 帮助按钮群
		helpAboutAction = self.createAction("&帮助", self.helpabout, "Ctrl+A", "helpabout", "帮助")
		
		# 菜单群
		# 文件菜单
		self.fileMenu = self.menuBar().addMenu("&文件")
		# 固定文件菜单项,文件菜单打开时实时更新
		self.fileMenuActions = (fileOpenAction, fileSaveAction, fileQuitAction)
		self.fileMenu.aboutToShow.connect(self.updateFileMenu)
		# 编辑菜单
		editMenu = self.menuBar().addMenu("&编辑")
		self.addActions(editMenu, (editZoominAction, editZoomoutAction))
		editAnno = editMenu.addMenu("&标注")
		editMason = editMenu.addMenu("&Mason染色处理")
		editHe = editMenu.addMenu("&HE染色处理")
		editAnno.setIcon(QIcon(":/anno.png"))
		self.addActions(editAnno, (self.editPointAnnoAction, self.editRectAnnoAction, self.editElliAnnoAction))
		self.addActions(editMason, (self.editSegAction, self.editAreaAction))
		self.addActions(editHe,
		                (self.editAbjustAction, self.editDetectAction, self.editAverAction, self.editAreaActionHE))
		# 帮助菜单
		helpMenu = self.menuBar().addMenu("&帮助")
		helpMenu.addAction(helpAboutAction)
		
		# 文件工具条
		fileToolbar = self.addToolBar("File")
		fileToolbar.setObjectName("FileToolBar")
		self.addActions(fileToolbar, (fileOpenAction, fileQuitAction))
		# 标记工具条
		annoToolbar = self.addToolBar("Annotation")
		annoToolbar.setObjectName("AnnotationToolBar")
		self.addActions(annoToolbar,
		                (self.editPointAnnoAction, self.editRectAnnoAction, self.editElliAnnoAction, fileSaveAction))
		# 放大工具条
		zoomToolbar = self.addToolBar("Zoom")
		zoomToolbar.setObjectName("ZoomToolBar")
		self.addActions(zoomToolbar, (editZoominAction, editZoomoutAction))
		# 编辑工具条
		editToolbar = self.addToolBar("Edit")
		editToolbar.setObjectName("EditToolBar")
		self.addActions(editToolbar, (
			self.editSegAction, self.editAreaAction, None, self.editAbjustAction, self.editDetectAction,
			self.editAverAction, None))
		# 标注显示工具条
		self.annoshowToolbar = self.addToolBar('Annos')
		self.annoshowToolbar.setObjectName("annoshowToolbar")
		self.annoshowToolbar.show()
		
		# 右键菜单
		self.imageLabelMenu = QMenu(self.imageLabel)
		self.annoMenu = QMenu("&标注")
		self.annoMenu.setIcon(QIcon(":/anno.png"))
		self.masonMenu = QMenu("&Mason染色处理")
		self.heMenu = QMenu("&HE染色处理")
		self.changeGroup = (self.annoMenu, None, self.masonMenu, self.heMenu)
		self.addActions(self.annoMenu, (self.editPointAnnoAction, self.editRectAnnoAction, self.editElliAnnoAction))
		self.addActions(self.masonMenu, (self.editSegAction, self.editAreaAction))
		self.addActions(self.heMenu,
		                (self.editAbjustAction, self.editDetectAction, self.editAverAction, self.editAreaActionHE))
		self.addActions(self.imageLabelMenu, self.changeGroup)
		self.imageLabelMenu.aboutToHide.connect(self.mouserelease)
		
		# 放大层数子部件
		self.zoomSpinBox = QSpinBox()
		self.zoomSpinBox.setRange(0, 10)
		self.zoomSpinBox.setSuffix("层")
		self.zoomSpinBox.setValue(0)
		self.zoomSpinBox.setToolTip("Zoom")
		self.zoomSpinBox.setStatusTip(self.zoomSpinBox.toolTip())
		self.zoomSpinBox.setFocusPolicy(Qt.NoFocus)
		self.zoomSpinBox.valueChanged.connect(self.vchange)
		zoomToolbar.addWidget(self.zoomSpinBox)
		# 放大倍数子部件
		self.beilvLabel = QLabel()
		self.beilvLabel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
		self.beilvLabel.setText("0")
		zoomToolbar.addWidget(self.beilvLabel)
		
		# 主窗口初始化加载历史
		self.setMouseTracking(True)
		settings = QSettings()
		if settings.value("RecentFiles") is not None:
			self.recentFiles = settings.value("RecentFiles")
		else:
			self.recentFiles = []
		size = settings.value("MainWindow/Size", QVariant(QSize(600, 500)))
		self.resize(size)
		position = settings.value("MainWindow/Position", QVariant(QPoint(0, 0)))
		self.move(position)
		if settings.value("MainWindow/State") is not None:
			self.restoreState(QByteArray(settings.value("MainWindow/State")))
		self.setWindowTitle(title)
		self.updateFileMenu()
		QTimer.singleShot(0, self.loadInitialFile)  # firstshowup mainwindow then load
	
	def resizeEvent(self, event):
		'''
		窗口重调函数
		:param event: 窗口大小改变事件
		:return:
		'''
		if self.slide is None:
			return
		self.geshi.setw(self.imageLabel.width())
		self.geshi.seth(self.imageLabel.height())
		self.showImage()
	
	def vchange(self):
		'''
		放大层数改变函数
		:return:
		'''
		if self.slide is None:
			return
		if self.haha:
			self.geshi.setl(self.zoomSpinBox.value())
			self.showImage()
	
	def keyPressEvent(self, event):
		'''
		键盘响应函数
		:param event: 键盘事件
		:return:
		'''
		if self.slide is None:
			return
		if event.key() == Qt.Key_Left:
			self.geshi.setx(int(self.geshi.x - (self.geshi.w * self.geshi.b / 5)))
		elif event.key() == Qt.Key_Right:
			self.geshi.setx(int(self.geshi.x + (self.geshi.w * self.geshi.b / 5)))
		elif event.key() == Qt.Key_Down:
			self.geshi.sety(int(self.geshi.y + (self.geshi.h * self.geshi.b / 5)))
		elif event.key() == Qt.Key_Up:
			self.geshi.sety(int(self.geshi.y - (self.geshi.h * self.geshi.b / 5)))
		elif event.key() == Qt.Key_Z:
			if self.annotation is not None:
				self.annotation.remove()
		self.showImage()
	
	def loadInitialFile(self):
		'''
		加载初始图片函数
		:return:
		'''
		settings = QSettings()
		fname = unicode(settings.value("LastFile"))
		# fname = (settings.value("LastFile"))
		if fname and QFile.exists(fname):
			self.loadFile(fname)
	
	def closeEvent(self, event):
		'''
		窗口关闭前操作函数
		:param event: 窗口关闭事件
		:return:
		'''
		if self.okToContinue():
			settings = QSettings()
			filename = QVariant(unicode(self.filename)) if self.filename is not None else QVariant()
			settings.setValue("LastFile", filename)
			recentFiles = QVariant(self.recentFiles) \
				if self.recentFiles else QVariant()
			settings.setValue("RecentFiles", recentFiles)
			settings.setValue("MainWindow/Size", QVariant(self.size()))
			settings.setValue("MainWindow/Position", QVariant(self.pos()))
			settings.setValue("MainWindow/State", self.saveState())
		else:
			event.ignore()
	
	def okToContinue(self):
		'''
		保存提示函数
		:return: 是否保存
		'''
		if self.annotation is None or len(self.annotation.list) == 0 or (
				len(self.annotation.list) == 1 and len(self.annotation.list[0].list) == 0):
			return True
		reply = QMessageBox.question(self, "Finish Notice", "save the annotation?",
		                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
		if reply == QMessageBox.Cancel:
			return False
		if reply == QMessageBox.Yes and self.annotation is not None:
			self.annotation.saveAnnotation(self.filename)
		return True
	
	def updateFileMenu(self):
		'''
		刷新文件菜单函数
		:return:
		'''
		self.fileMenu.clear()
		self.addActions(self.fileMenu, self.fileMenuActions[:-1])
		current = unicode(self.filename) \
			if self.filename is not None else None
		recentFiles = []
		for fname in self.recentFiles:
			if fname != current and QFile.exists(fname):
				recentFiles.append(fname)
		if recentFiles:
			self.fileMenu.addSeparator()
			for i, fname in enumerate(recentFiles):
				action = QAction(QIcon(":/image"), "&%d %s" % (i + 1, QFileInfo(fname).fileName()), self)
				action.setData(QVariant(fname))
				action.triggered.connect(self.loadrecentfile)
				self.fileMenu.addAction(action)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.fileMenuActions[-1])
	
	def loadrecentfile(self):
		'''
		加载最近文件函数
		:return:
		'''
		self.loadFile()
	
	def addRecentFile(self, fname):
		'''
		记录最近文件函数
		:param fname: 现文件
		:return:
		'''
		if fname is None:
			return
		if fname not in self.recentFiles:
			self.recentFiles.insert(0, fname)
			while len(self.recentFiles) > 5:
				self.recentFiles.pop()
	
	def updateStatus(self, message):
		'''
		状态刷新函数
		:param message:提示信息
		:return:
		'''
		self.statusBar().showMessage(message, 5000)
		wt = title + " - " + str(self.filename)
		if self.filename is not None:
			self.setWindowTitle(wt)
		else:
			self.setWindowTitle(title)
	
	def fileOpen(self):
		'''
		文件打开函数
		:return:
		'''
		dir = os.path.dirname(self.filename) \
			if self.filename is not None else "."
		fname, ftype = QFileDialog.getOpenFileName(self, "选择图片", dir,
		                                           "tif files(*.tif);;svs files(*.svs);;ndpi files(*.ndpi)")
		if fname:
			self.updateStatus(fname)
			self.loadFile(fname)
	
	def loadFile(self, fname=None):
		'''
		文件加载函数
		:param fname: 文件名
		:return:
		'''
		if fname is None:
			action = self.sender()
			if isinstance(action, QAction):
				fname = unicode(action.data())
				if not self.okToContinue():
					return
			else:
				return
		if fname:
			self.filename = None
			# open slide
			self.slide = openslide.open_slide(fname)
			if self.slide is None:
				message = "Failed to read %s" % fname
			else:
				self.addRecentFile(fname)
				self.filename = fname
				self.geshi = geshi(self.slide, self.imageLabel.width(), self.imageLabel.height())
				if self.picture is not None:
					del self.picture
					self.picture = None
				if self.annotation is not None:
					for i in self.annotation.list:
						i.hide()
					del self.annotation
					self.annotation = None
				self.picture = showimage(self.slide, self.imageLabel)
				self.annotation = Annotations(self.imageLabel)
				self.annotation.openAnnotation(self.filename, self.geshi)
				self.haha = False
				self.zoomSpinBox.setRange(0, self.geshi.la)
				self.zoomSpinBox.setValue(self.geshi.la)
				self.haha = True
				self.showImage()
				self.sizeLabel.setText("%d x %d" % self.slide.dimensions)
			message = "Loaded %s" % os.path.basename(fname)
			self.updateStatus(message)
	
	def fileSave(self):
		'''
		标记保存函数
		:return:
		'''
		if self.slide is None:
			return
		self.annotation.saveAnnotation(self.filename)
	
	def editZoomout(self):
		'''
		缩小函数
		:return:
		'''
		if self.slide is None:
			return
		if self.zoomSpinBox.value() <= self.geshi.la - 1:
			self.geshi.setl(self.geshi.l + 1)
			self.zoomSpinBox.setValue(self.geshi.l)
			self.showImage()
	
	def editZoomin(self):
		'''
		放大函数
		:return:
		'''
		if self.slide is None:
			return
		if self.zoomSpinBox.value() > 1:
			self.geshi.setl(self.geshi.l - 1)
			self.zoomSpinBox.setValue(self.geshi.l)
			self.showImage()
	
	def wheelEvent(self, event):
		'''
		鼠标滚动函数
		:param event: 鼠标滚动事件
		:return:
		'''
		if self.slide is None:
			return
		if self.picture is not None and self.picture.thumbnail.geometry().contains(event.pos() - self.imageLabel.pos()):
			return
		pox = event.pos().x() - self.imageLabel.pos().x()
		poy = event.pos().y() - self.imageLabel.pos().y()
		if event.angleDelta().y() > 0 and self.geshi.b > 1:
			self.geshi.setb(self.geshi.b / 1.1)
			self.geshi.setx(int(self.geshi.x + (pox - self.imageLabel.width() / 2) * self.geshi.b * 0.1))
			self.geshi.sety(int(self.geshi.y + (poy - self.imageLabel.height() / 2) * self.geshi.b * 0.1))
		elif event.angleDelta().y() < 0:
			self.geshi.setb(self.geshi.b * 1.1)
			self.geshi.setx(int(self.geshi.x - (pox - self.imageLabel.width() / 2) * self.geshi.b * 0.09))
			self.geshi.sety(int(self.geshi.y - (poy - self.imageLabel.height() / 2) * self.geshi.b * 0.09))
		self.showImage()
	
	def mousePressEvent(self, event):
		'''
		鼠标单击事件
		:param event: 鼠标单击函数
		:return:
		'''
		if not self.imageLabel.geometry().contains(event.pos()):
			return
		if self.slide is None:
			return
		# 点击缩略图,移动视野
		if self.picture.thumbnail.geometry().contains(
				event.pos() - self.imageLabel.pos()) and event.button() == Qt.LeftButton:
			x = (
					    event.pos().x() - self.imageLabel.pos().x() - self.picture.thumbnail.geometry().x()) * self.geshi.wa / self.picture.thumbnail.geometry().width()
			y = (
					    event.pos().y() - self.imageLabel.pos().y() - self.picture.thumbnail.geometry().y()) * self.geshi.ha / self.picture.thumbnail.geometry().height()
			self.geshi.setx(x)
			self.geshi.sety(y)
			self.showImage(True)
			return
		# 登记鼠标位置
		pox = event.pos().x() - self.imageLabel.x()
		poy = event.pos().y() - self.imageLabel.y()
		self.point = (-1, -1)
		self.ismouse = True
		if event.button() == Qt.LeftButton:
			self.ifleftbuttom = True
		else:
			self.ifleftbuttom = False
		# 是否正在标记
		if self.ifpointanno and self.ifleftbuttom:
			# 增加新标记点
			x = self.geshi.x + (pox - self.imageLabel.width() / 2) * self.geshi.b
			y = self.geshi.y + (poy - self.imageLabel.height() / 2) * self.geshi.b
			self.annotation.addPoint(self.geshi, x, y, "Polygon")
			self.showImage()
			return
		if self.ifrectanno and self.ifleftbuttom:
			# 增加新的矩形
			x = self.geshi.x + (pox - self.imageLabel.width() / 2) * self.geshi.b
			y = self.geshi.y + (poy - self.imageLabel.height() / 2) * self.geshi.b
			self.annotation.addPoint(self.geshi, x, y, "Rectangle")
			self.point = (len(self.annotation.list) - 1, 4)
		if self.ifellianno and self.ifleftbuttom:
			# 增加新的圆形
			x = self.geshi.x + (pox - self.imageLabel.width() / 2) * self.geshi.b
			y = self.geshi.y + (poy - self.imageLabel.height() / 2) * self.geshi.b
			self.annotation.addPoint(self.geshi, x, y, "Ellipse")
			self.point = (len(self.annotation.list) - 1, 4)
		# 是否单击到已选中标记内的点
		if self.annotation is not None and len(
				self.annotation.list) > 0 and not self.ifrectanno and self.ifleftbuttom and not self.ifellianno:
			self.point = self.annotation.messagepoint(pox, poy, self.geshi, self.canchange)
		# 当前鼠标位置
		self.qx = pox
		self.qy = poy
		if self.point[0] >= 0:
			# 当前点位置
			self.bx = self.annotation.list[self.point[0]].list[self.point[1]][0]
			self.by = self.annotation.list[self.point[0]].list[self.point[1]][1]
			return
		else:
			# 当前视野位置
			self.bx = self.geshi.x
			self.by = self.geshi.y
		# 是否选中标记
		if self.annotation is not None and len(self.annotation.list) > 0 and self.ifleftbuttom:
			self.canchange = self.annotation.messageline(pox, poy, self.geshi)
			for i in self.annotation.list:
				i.unchosed()
			if len(self.canchange) > 0:
				for i in self.canchange:
					self.annotation.list[i].chosed()
				for i in self.imageLabelMenu.actions():
					self.imageLabelMenu.removeAction(i)
				self.imageLabelMenu.addAction(self.editAnnoCNAction)
				self.imageLabelMenu.addAction(self.editAnnoCCAction)
				self.imageLabelMenu.addAction(self.editAnnoDelAction)
			else:
				for i in self.imageLabelMenu.actions():
					self.imageLabelMenu.removeAction(i)
				self.addActions(self.imageLabelMenu, self.changeGroup)
		if self.point[0] < 0 and event.button() == Qt.RightButton:
			self.imageLabelMenu.exec_(QCursor.pos())
	
	def mouseReleaseEvent(self, event):
		'''
		鼠标释放函数
		:param event:鼠标释放事件
		:return:
		'''
		self.mouserelease()
	
	def mouserelease(self):
		self.ismouse = False
		self.ifleftbuttom = False
	
	def mouseMoveEvent(self, event):
		'''
		鼠标移动函数
		:param event: 鼠标移动事件
		:return:
		'''
		if not self.imageLabel.geometry().contains(event.pos()):
			return
		if self.slide is None:
			return
		pox = event.pos().x() - self.imageLabel.pos().x()
		poy = event.pos().y() - self.imageLabel.pos().y()
		if self.ismouse is True:
			if self.ifleftbuttom:
				if not self.ifpointanno or self.ifrectanno:
					if self.point[0] >= 0:
						# 移动点
						self.annotation.list[self.point[0]].setPoint(self.point[1],
						                                             self.bx + (pox - self.qx) * self.geshi.b,
						                                             self.by + (poy - self.qy) * self.geshi.b)
					else:
						# 移动视野
						self.geshi.setx(int(self.bx - (pox - self.qx) * self.geshi.b))
						self.geshi.sety(int(self.by - (poy - self.qy) * self.geshi.b))
				else:
					# 增加标记点
					x = self.geshi.x + (pox - self.imageLabel.width() / 2) * self.geshi.b
					y = self.geshi.y + (poy - self.imageLabel.height() / 2) * self.geshi.b
					self.annotation.addPoint(self.geshi, x, y, "Polygon")
			else:
				# 移动视野
				self.geshi.setx(int(self.bx - (pox - self.qx) * self.geshi.b))
				self.geshi.sety(int(self.by - (poy - self.qy) * self.geshi.b))
			self.showImage()
		# 显示标记名
		if self.annotation is not None and len(self.annotation.list) > 0 and (
				abs(pox - self.qpox) > 4 or abs(poy - self.qpoy) > 4):
			self.annotation.messageline(pox, poy, self.geshi)
			self.qpox = pox
			self.qpoy = poy
	
	def editAnnoCN(self):
		'''
		标记名字修改函数
		:return:
		'''
		for i in self.canchange:
			text, ok = QInputDialog.getText(self.imageLabel, "重命名", "请输入新名（组名：标注名）：", QLineEdit.Normal,
			                                self.annotation.list[i].name)
			if ok:
				self.annotation.list[i].setName(text)
	
	def editAnnoCC(self):
		'''
		标记颜色修改函数
		:return:
		'''
		for i in self.canchange:
			color = QColor()
			color.setNamedColor(self.annotation.list[i].opColor())
			color = QColorDialog.getColor(color)
			if color.isValid():
				self.annotation.list[i].setColor(color.name())
	
	def editAnnoDel(self):
		'''
		删除标记函数
		:return:
		'''
		if self.annotation is not None and len(self.annotation.list) > self.canchange[0]:
			self.annotation.list[self.canchange[0]].hide()
			self.annotation.list[self.canchange[0]].deleting()
			del self.annotation.list[self.canchange[0]]
		self.canchange = []
	
	def showImage(self, restart=False):
		'''
		图片显示函数
		:param restart: 重新加载视野
		:return:
		'''
		if self.slide is None:
			return
		global number
		number = None
		self.haha = False
		self.zoomSpinBox.setValue(self.geshi.l)
		self.haha = True
		self.annotation.set(self.geshi)
		self.picture.new(self.geshi, self.imageLabel, restart)
		number = self.picture.prorun(self.geshi, self.pro, self.arg)
		if number is not None:
			self.updateStatus(number)
		self.beilvLabel.setText("1:%f" % self.geshi.b)
	
	def helpabout(self):
		'''
		帮助对话框函数
		:return:
		'''
		QMessageBox.about(self, "About %s" % title, "<b>%s</b> v %s" % (title, _version_))
	
	def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False):
		'''
		按钮集成函数
		:param text:标题
		:param slot: 事件
		:param shortcut: 快捷键
		:param icon: 图标
		:param tip:提示信息
		:param checkable:是否标记
		:return:
		'''
		action = QAction(text, self)
		if icon is not None:
			action.setIcon(QIcon(":/%s.png" % icon))
		if shortcut is not None:
			action.setShortcut(shortcut)
		if tip is not None:
			action.setToolTip(tip)
			action.setStatusTip(tip)
		if slot is not None:
			action.triggered.connect(slot)
		if checkable:
			action.setCheckable(True)
			action.setChecked(False)
		return action
	
	def addActions(self, target, actions):
		'''
		按钮加载函数
		:param target: 加载父部件
		:param actions: 加载按钮
		:return:
		'''
		for action in actions:
			if action is None:
				target.addSeparator()
			else:
				if type(action) == type(QMenu()):
					target.addMenu(action)
				else:
					target.addAction(action)
	
	def checkableaction(self, ifbuttom, pro, action=None, arg=None):
		if self.slide is None:
			return
		if ifbuttom == True:
			ifbuttom = False
			if pro is not None:
				j = self.pro.index(pro)
				del self.pro[j]
				del self.arg[j]
			if action is not None:
				action.setChecked(False)
		else:
			ifbuttom = True
			if pro is not None:
				self.pro.append(pro)
				if arg is not None:
					self.arg.append(arg)
				else:
					self.arg.append(0)
			if action is not None:
				action.setChecked(True)
		self.showImage()
		return ifbuttom
	
	def editDetect(self):
		self.ifdetect = self.checkableaction(self.ifdetect, detectprocess, self.editDetectAction)
	
	def editAver(self):
		self.ifaver = self.checkableaction(self.ifaver, averprocess, self.editAverAction)
	
	def editSeg(self):
		if self.ifseg == False and self.slide is not None:
			if not self.before == self.filename:
				self.totalimage = totaldensity(self.slide)
				global arg
				arg = self.totalimage
				self.before = self.filename
		self.ifseg = self.checkableaction(self.ifseg, density, self.editSegAction, arg)
	
	def editabjust(self):
		if self.ifabjust == False and self.slide is not None:
			dir = os.path.dirname(self.filename) if self.filename is not None else "."
			if self.slide2 is not None:
				reply = QMessageBox.question(self, "Mason Picture", "Change picture?", QMessageBox.Yes | QMessageBox.No)
			if self.slide2 is None or reply == QMessageBox.Yes:
				fname, ftype = QFileDialog.getOpenFileName(self, "选择Mason染色图片", dir,
				                                           "tif files(*.tif);;svs files(*.svs);;ndpi files(*.ndpi)")
				self.slide2 = openslide.open_slide(fname)
			threshold, ok = QInputDialog.getInt(self.imageLabel, "Threshold", "Input Integer in [0,255]:", 20, 0, 255)
			if self.geshi.la > 4:
				level = self.geshi.la - 4
			else:
				level = self.geshi.la - 1
			he = densityprocess(self.slide, level)
			mason = densityprocess(self.slide2, level)
			
			bf = cv2.BFMatcher()
			matches = bf.knnMatch(mason['des'], he['des'], k=2)
			
			MIN_MATCH_COUNT = 10
			good = []
			for m, n in matches:
				if m.distance < 0.75 * n.distance:
					good.append(m)
			
			if len(good) > MIN_MATCH_COUNT:
				src_pts = np.float32([mason['key'][m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
				dst_pts = np.float32([he['key'][m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
				
				M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
				matchesMask = mask.ravel().tolist()
			
			else:
				QMessageBox.question(self, "Notice", "Can't match", QMessageBox.Yes)
				return
			
			if self.geshi.la > 6:
				fibrosislevel = self.geshi.la - 6
			else:
				fibrosislevel = self.geshi.la - 1
			masonimg = fibrosis(self.slide2, mason['dimensions'], fibrosislevel, threshold)
			masonimg = cv2.warpPerspective(masonimg, M, he['dimensions'])
			global arg
			arg = {'masonimg': masonimg, 'dimensions': he['dimensions']}
			beilv = self.geshi.wa / he['dimensions'][0]
			image, cnts, hierarchy = cv2.findContours(masonimg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			for i in self.annotation.list:
				if i.name.split(":")[0] == 'fibrosis':
					i.hide()
					i.deleting()
					del i
			self.canchange = []
			for i in range(0, len(cnts)):
				if cv2.contourArea(cnts[i]) > 100:
					self.annotation.list.append(
						Annotation(self.imageLabel, self.geshi, 'fibrosis:' + str(i), "Polygon", self.annotation))
					for j in cnts[i]:
						self.annotation.list[len(self.annotation.list) - 1].list.append(
							(j[0][0] * beilv, j[0][1] * beilv))
					self.annotation.list[len(self.annotation.list) - 1].list.append(
						(cnts[i][0][0][0] * beilv, cnts[i][0][0][1] * beilv))
					self.annotation.list[len(self.annotation.list) - 1].ending()
					if hierarchy[0][i][3] < 0:
						self.annotation.list[len(self.annotation.list) - 1].setColor('#FFFF00')
					else:
						self.annotation.list[len(self.annotation.list) - 1].setColor('#238E23')
		self.ifabjust = self.checkableaction(self.ifabjust, abjust, self.editAbjustAction, arg)
	
	# 分区密度处理
	def editarea(self):
		print "called"
		for i in self.annotation.list:
			if i.name.split(":")[0] == 'density':
				i.hide()
				i.deleting()
				del i
		self.canchange = []
		n = 21
		if self.geshi.la > 4:
			level = self.geshi.la - 4
		else:
			level = self.geshi.la - 1
		workingDimensions = self.slide.level_dimensions[level]
		img = np.array(self.slide.read_region((0, 0), level, workingDimensions))
		
		b, g, r, a = cv2.split(img)
		rgbimg = cv2.merge((r, g, b))
		hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
		greyimg = cv2.inRange(hsv, (0, 20, 0), (180, 255, 180))
		fibrosis = cv2.inRange(hsv, (90, 20, 0), (150, 255, 255))
		
		averagegreyimg = cv2.blur(greyimg, (30, 30))
		cv2.imshow("average grey img", averagegreyimg)
		
		ret, erode = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
		erode = cv2.erode(erode, kernel, iterations=15)
		
		ret, averimage = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
		averimage, avercnts, averhierarchy = cv2.findContours(averimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		
		image, cnts, hierarchy = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cv2.imshow("contour after erosion", image)
		
		object = []
		maxarea = 0
		max = None
		
		for cnt in cnts:
			area = cv2.contourArea(cnt)
			if area > 100:
				points = []
				for i in cnt:
					x = i[0][0]
					y = i[0][1]
					points.append([x, y])
				i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
				cv2.fillPoly(i, np.array([points], np.int32), 255)
				object.append(i)
				if area > maxarea:
					maxarea = area
					max = len(object) - 1
		wall = object[max]
		
		other = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
		for i in range(0, len(object)):
			if i != max:
				other = cv2.add(other, object[i])
		
		# 通过矩moments计算重心
		M1 = cv2.moments(wall)
		cx1 = int(M1["m10"] / M1["m00"])
		cy1 = int(M1["m01"] / M1["m00"])
		
		M0 = cv2.moments(other)
		cx0 = int((M0["m10"]) / (M0["m00"]))
		cy0 = int((M0["m01"]) / (M0["m00"]))
		
		if cx0 - cx1 == 0:
			if cy0 - cy1 > 0:
				baseangle = 90
			else:
				baseangle = -90
		else:
			if cx0 - cx1 > 0:
				baseangle = 180 * math.atan(-(cy0 - cy1) / (cx0 - cx1)) / math.pi
			else:
				baseangle = 180 + 180 * math.atan(-(cy0 - cy1) / (cx0 - cx1)) / math.pi
		
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
		wall = cv2.dilate(wall, kernel, iterations=15)
		cv2.imshow("wall", wall)
		
		other = cv2.dilate(other, kernel, iterations=15)
		cv2.imshow("other", other)
		
		image, contours, hierarchy = cv2.findContours(wall, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		image1, contours1, hierarchy1 = cv2.findContours(other, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		points = cv2.approxPolyDP(contours[0], 15, True)
		points1 = []
		for i in contours1:
			for j in i:
				points1.append(j)
		points1 = np.array(points1)
		rect = cv2.minAreaRect(points)
		rect1 = cv2.minAreaRect(points1)
		
		rect = (rect[0], rect[1], -rect[2])
		if (math.fabs(rect[2] - baseangle) % 360) < 45 or (math.fabs(rect[2] - baseangle) % 360) > 135:
			angle = 90 - rect[2]
			width = rect[1][1]
			height = rect[1][0]
		else:
			angle = rect[2]
			width = rect[1][0]
			height = rect[1][1]
		points = rotatePoints(points, rect[0], -angle)
		
		for i in avercnts:
			averpoints = rotatePoints(i, rect[0], -angle)
		
		notheightPoints = [[], []]
		for i in range(0, len(points)):
			if points[i][0][1] - rect[0][1] > height / 5:
				notheightPoints[0].append(points[i])
			else:
				if points[i][0][1] - rect[0][1] < -height / 5:
					notheightPoints[1].append(points[i])
		
		avery0 = 0
		for i in range(0, len(notheightPoints[0])):
			avery0 = avery0 + notheightPoints[0][i][0][1]
		avery0 = avery0 / len(notheightPoints[0])
		avery1 = 0
		for i in range(0, len(notheightPoints[1])):
			avery1 = avery1 + notheightPoints[1][i][0][1]
		avery1 = avery1 / len(notheightPoints[1])
		
		if (baseangle % 360) < 180:
			if avery1 < avery0:
				abc = notheightPoints[0]
				notheightPoints[0] = notheightPoints[1]
				notheightPoints[1] = abc
		else:
			if avery1 > avery0:
				abc = notheightPoints[0]
				notheightPoints[0] = notheightPoints[1]
				notheightPoints[1] = abc
		
		nothei1 = []
		for i in avercnts:
			for j in i:
				distance0 = 100000
				for k in notheightPoints[0]:
					distance = math.sqrt(
						(j[0][0] - k[0][0]) * (j[0][0] - k[0][0]) + (j[0][1] - k[0][1]) * (j[0][1] - k[0][1]))
					if distance < distance0:
						distance0 = distance
				distance1 = 100000
				for k in notheightPoints[1]:
					distance = math.sqrt(
						(j[0][0] - k[0][0]) * (j[0][0] - k[0][0]) + (j[0][1] - k[0][1]) * (j[0][1] - k[0][1]))
					if distance < distance1:
						distance1 = distance
				if distance1 < distance0 / 2:
					nothei1.append(j)
		
		notheightPoints[1] = nothei1
		
		for i in range(0, len(notheightPoints[0])):
			notheightPoints[0][i] = [notheightPoints[0][i][0][0], notheightPoints[0][i][0][1]]
		for i in range(0, len(notheightPoints[1])):
			notheightPoints[1][i] = [notheightPoints[1][i][0][0], notheightPoints[1][i][0][1]]
		notheightPoints[0].sort()
		notheightPoints[1].sort()
		for i in range(0, len(notheightPoints[0])):
			notheightPoints[0][i] = [[notheightPoints[0][i][0], notheightPoints[0][i][1]]]
		for i in range(0, len(notheightPoints[1])):
			notheightPoints[1][i] = [[notheightPoints[1][i][0], notheightPoints[1][i][1]]]
		
		xlist = []
		for i in notheightPoints[0]:
			xlist.append((i[0][0], i[0][1], 0))
		for i in notheightPoints[1]:
			xlist.append((i[0][0], i[0][1], 1))
		xlist.sort(key=itemgetter(0))
		
		addPoints = [[], []]
		for i in range(0, len(xlist)):
			pl = i - 1
			pr = i + 1
			if xlist[i][2] == 0:
				n = 0
				m = 1
			else:
				n = 1
				m = 0
			while pl >= 0 and xlist[pl][2] == xlist[i][2]:
				pl = pl - 1
			while pr < len(xlist) and xlist[pr][2] == xlist[i][2]:
				pr = pr + 1
			if pl >= 0 and pr < len(xlist):
				y = (xlist[pl][1]) * (xlist[pr][0] - xlist[i][0]) / (xlist[pr][0] - xlist[pl][0]) + (xlist[pr][1]) * (
						xlist[i][0] - xlist[pl][0]) / (xlist[pr][0] - xlist[pl][0])
				addPoints[n].append([[int(xlist[i][0]), int((xlist[i][1] - y) / 3 + y)]])
				addPoints[m].append([[int(xlist[i][0]), int((xlist[i][1] - y) * 2 / 3 + y)]])
			elif pl < 0:
				addPoints[n].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pr][1]) / 3 + xlist[pr][1])]])
				addPoints[m].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pr][1]) * 2 / 3 + xlist[pr][1])]])
			else:
				addPoints[n].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pl][1]) / 3 + xlist[pl][1])]])
				addPoints[m].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pl][1]) * 2 / 3 + xlist[pl][1])]])
		
		notheightPoints[0] = rotatePoints(notheightPoints[0], rect[0], angle)
		notheightPoints[1] = rotatePoints(notheightPoints[1], rect[0], angle)
		addPoints[0] = rotatePoints(addPoints[0], rect[0], angle)
		addPoints[1] = rotatePoints(addPoints[1], rect[0], angle)
		
		m = cv2.moments(numpy.array(notheightPoints[1]))
		cx1 = int(m["m10"] / m["m00"])
		cy1 = int(m["m01"] / m["m00"])
		
		addPoints[1].reverse()
		notheightPoints[1].reverse()
		first = notheightPoints[0] + addPoints[1]
		second = addPoints[0] + addPoints[1]
		third = addPoints[0] + notheightPoints[1]
		
		i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
		firstmask = cv2.fillPoly(i, np.array([first], np.int32), 255)
		
		i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
		secondmask = cv2.fillPoly(i, np.array([second], np.int32), 255)
		
		i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
		thirdmask = cv2.fillPoly(i, np.array([third], np.int32), 255)
		
		firstdensity = areaaveragedensity(fibrosis, greyimg, firstmask)
		seconddensity = areaaveragedensity(fibrosis, greyimg, secondmask)
		thirddensity = areaaveragedensity(fibrosis, greyimg, thirdmask)
		
		box1 = cv2.boxPoints(rect1)
		box1 = np.array(box1)
		for i in range(0, 2):
			max = sqrt((box1[i][0] - cx1) * (box1[i][0] - cx1) + (box1[i][1] - cy1) * (box1[i][1] - cy1))
			n = i
			for j in range(i, 4):
				if sqrt((box1[j][0] - cx1) * (box1[j][0] - cx1) + (box1[j][1] - cy1) * (box1[j][1] - cy1)) > max:
					max = sqrt((box1[j][0] - cx1) * (box1[j][0] - cx1) + (box1[j][1] - cy1) * (box1[j][1] - cy1))
					n = j
			k = (box1[i][0], box1[i][1])
			box1[i] = box1[n]
			box1[n] = [k[0], k[1]]
		
		firstarea = 'Endocardium'
		thirdarea = 'Epicardium'
		otherline = notheightPoints[0]
		
		if sqrt((box1[0][0] - otherline[0][0][0]) * (box1[0][0] - otherline[0][0][0]) + (
				box1[0][1] - otherline[0][0][1]) * (box1[0][1] - otherline[0][0][1])) > sqrt(
			(box1[1][0] - otherline[0][0][0]) * (box1[1][0] - otherline[0][0][0]) + (
					box1[1][1] - otherline[0][0][1]) * (box1[1][1] - otherline[0][0][1])):
			otherline.append([[box1[0][0], box1[0][1]]])
			otherline.append([[box1[1][0], box1[1][1]]])
		else:
			otherline.append([[box1[1][0], box1[1][1]]])
			otherline.append([[box1[0][0], box1[0][1]]])
		
		i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
		othermask = cv2.fillPoly(i, np.array([otherline], np.int32), 255)
		otherdensity = areaaveragedensity(fibrosis, greyimg, othermask)
		
		self.annotation.list.append(
			Annotation(self.imageLabel, self.geshi, firstarea + ':' + str(firstdensity * 100)[0:4] + '%', "Polygon",
			           self.annotation))
		for i in first:
			self.annotation.list[len(self.annotation.list) - 1].list.append(
				(i[0][0] * self.geshi.bei[level], i[0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].list.append(
			(first[0][0][0] * self.geshi.bei[level], first[0][0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].ending()
		self.annotation.list[len(self.annotation.list) - 1].setColor('#FFC0CB')
		self.annotation.list.append(
			Annotation(self.imageLabel, self.geshi, 'Midwall:' + str(seconddensity * 100)[0:4] + '%', "Polygon",
			           self.annotation))
		for i in second:
			self.annotation.list[len(self.annotation.list) - 1].list.append(
				(i[0][0] * self.geshi.bei[level], i[0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].list.append(
			(second[0][0][0] * self.geshi.bei[level], second[0][0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].ending()
		self.annotation.list[len(self.annotation.list) - 1].setColor('#000000')
		self.annotation.list.append(
			Annotation(self.imageLabel, self.geshi, thirdarea + ':' + str(thirddensity * 100)[0:4] + '%', "Polygon",
			           self.annotation))
		for i in third:
			self.annotation.list[len(self.annotation.list) - 1].list.append(
				(i[0][0] * self.geshi.bei[level], i[0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].list.append(
			(third[0][0][0] * self.geshi.bei[level], third[0][0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].ending()
		self.annotation.list[len(self.annotation.list) - 1].setColor('#32CD32')
		self.annotation.list.append(
			Annotation(self.imageLabel, self.geshi, 'Trabecular:' + str(otherdensity * 100)[0:4] + '%', "Polygon",
			           self.annotation))
		for i in otherline:
			self.annotation.list[len(self.annotation.list) - 1].list.append(
				(i[0][0] * self.geshi.bei[level], i[0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].list.append(
			(otherline[0][0][0] * self.geshi.bei[level], otherline[0][0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].ending()
		self.annotation.list[len(self.annotation.list) - 1].setColor('#6495ED')
	
	def editPointAnno(self):
		'''
		正在点群标记函数
		:return:
		'''
		self.ifpointanno = self.checkableaction(self.ifpointanno, None, self.editPointAnnoAction)
		if self.ifpointanno:
			self.ifrectanno = False
			self.ifellianno = False
			self.editRectAnnoAction.setChecked(False)
			self.editElliAnnoAction.setChecked(False)
	
	def editRectAnno(self):
		'''
		正在矩形标记函数
		:return:
		'''
		self.ifrectanno = self.checkableaction(self.ifrectanno, None, self.editRectAnnoAction)
		if self.ifrectanno:
			self.ifpointanno = False
			self.ifellianno = False
			self.editPointAnnoAction.setChecked(False)
			self.editElliAnnoAction.setChecked(False)
	
	def editElliAnno(self):
		'''
		正在圆形标记函数
		:return:
		'''
		self.ifellianno = self.checkableaction(self.ifellianno, None, self.editElliAnnoAction)
		if self.ifellianno:
			self.ifpointanno = False
			self.ifrectanno = False
			self.editPointAnnoAction.setChecked(False)
			self.editRectAnnoAction.setChecked(False)
	
	def editareaHE(self):
		print "called editHE"
		for i in self.annotation.list:
			if i.name.split(":")[0] == 'density':
				i.hide()
				i.deleting()
				del i
		self.canchange = []
		n = 21
		if self.geshi.la > 4:
			level = self.geshi.la - 4
		else:
			level = self.geshi.la - 1
		workingDimensions = self.slide.level_dimensions[level]
		img = np.array(self.slide.read_region((0, 0), level, workingDimensions))
		
		b, g, r, a = cv2.split(img)
		rgbimg = cv2.merge((r, g, b))
		hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
		# greyimg = cv2.inRange(hsv, (0, 20, 0), (180, 255, 180))
		greyimg = cv2.inRange(hsv, (0, 20, 0), (180, 255, 220))
		fibrosis = cv2.inRange(hsv, (90, 20, 0), (150, 255, 255))
		# cv2.imshow("fibrosis",fibrosis)
		averagegreyimg = cv2.blur(greyimg, (30, 30))
		# cv2.imshow('average grey img', averagegreyimg)
		# cv2.imwrite("test/HE/average_grey_img.jpg", averagegreyimg)
		
		ret, erode = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
		erode = cv2.erode(erode, kernel, iterations=3)
		# cv2.imshow("after erosion", erode)
		# cv2.imwrite("test/HE/after_erosion.jpg", erode)
		
		# cv2.imshow("")
		#  多次腐蚀，除去小梁
		
		ret, averimage = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
		averimage, avercnts, averhierarchy = cv2.findContours(averimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		# cv2.imshow("aver image", averimage)
		
		# 得到整体的边界
		
		image, cnts, hierarchy = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		# cv2.imshow("contour after erosion", erode)
		# 腐蚀后的边界
		
		object = []
		maxarea = 0
		max = None
		
		for cnt in cnts:
			area = cv2.contourArea(cnt)
			if area > 100:
				points = []
				for i in cnt:
					x = i[0][0]
					y = i[0][1]
					points.append([x, y])
				i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
				cv2.fillPoly(i, np.array([points], np.int32), 255)
				object.append(i)
				if area > maxarea:
					maxarea = area
					max = len(object) - 1
		wall = object[max]
		# 把每一个区域都分割出来，最大的心肌壁
		
		other = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
		for i in range(0, len(object)):
			if i != max:
				other = cv2.add(other, object[i])
		
		# 通过矩moments计算重心
		M1 = cv2.moments(wall)
		cx1 = int(M1["m10"] / M1["m00"])
		cy1 = int(M1["m01"] / M1["m00"])
		
		M0 = cv2.moments(other)
		cx0 = int((M0["m10"]) / (M0["m00"]))
		cy0 = int((M0["m01"]) / (M0["m00"]))
		
		if cx0 - cx1 == 0:
			if cy0 - cy1 > 0:
				baseangle = 90
			else:
				baseangle = -90
		else:
			if cx0 - cx1 > 0:
				baseangle = 180 * math.atan(-(cy0 - cy1) / (cx0 - cx1)) / math.pi
			else:
				baseangle = 180 + 180 * math.atan(-(cy0 - cy1) / (cx0 - cx1)) / math.pi
		
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
		wall = cv2.dilate(wall, kernel, iterations=15)
		# cv2.imshow("wall", wall)
		other = cv2.dilate(other, kernel, iterations=15)
		# cv2.imshow("other", other)
		
		image, contours, hierarchy = cv2.findContours(wall, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		image1, contours1, hierarchy1 = cv2.findContours(other, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		points = cv2.approxPolyDP(contours[0], 15, True)  # 主要功能是把一个连续光滑曲线折线化，对图像轮廓点进行多边形拟合。
		points1 = []
		for i in contours1:  # contours1 : other
			for j in i:
				points1.append(j)
		points1 = np.array(points1)
		
		rect = cv2.minAreaRect(points)
		rect1 = cv2.minAreaRect(points1)
		# 最小外切矩形
		
		rect = (rect[0], rect[1], -rect[2])  # ?
		if (math.fabs(rect[2] - baseangle) % 360) < 45 or (math.fabs(rect[2] - baseangle) % 360) > 135:
			angle = 90 - rect[2]
			width = rect[1][1]
			height = rect[1][0]
		else:
			angle = rect[2]
			width = rect[1][0]
			height = rect[1][1]
		points = rotatePoints(points, rect[0], -angle)
		
		for i in avercnts:
			averpoints = rotatePoints(i, rect[0], -angle)
		
		notheightPoints = [[], []]
		for i in range(0, len(points)):
			if points[i][0][1] - rect[0][1] > height / 5:
				notheightPoints[0].append(points[i])
			else:
				if points[i][0][1] - rect[0][1] < -height / 5:
					notheightPoints[1].append(points[i])
		
		avery0 = 0
		for i in range(0, len(notheightPoints[0])):
			avery0 = avery0 + notheightPoints[0][i][0][1]
		avery0 = avery0 / len(notheightPoints[0])
		avery1 = 0
		for i in range(0, len(notheightPoints[1])):
			avery1 = avery1 + notheightPoints[1][i][0][1]
		avery1 = avery1 / len(notheightPoints[1])
		
		if (baseangle % 360) < 180:
			if avery1 < avery0:
				abc = notheightPoints[0]
				notheightPoints[0] = notheightPoints[1]
				notheightPoints[1] = abc
		else:
			if avery1 > avery0:
				abc = notheightPoints[0]
				notheightPoints[0] = notheightPoints[1]
				notheightPoints[1] = abc
		
		nothei1 = []
		for i in avercnts:
			for j in i:
				distance0 = 100000
				for k in notheightPoints[0]:
					distance = math.sqrt(
						(j[0][0] - k[0][0]) * (j[0][0] - k[0][0]) + (j[0][1] - k[0][1]) * (j[0][1] - k[0][1]))
					if distance < distance0:
						distance0 = distance
				distance1 = 100000
				for k in notheightPoints[1]:
					distance = math.sqrt(
						(j[0][0] - k[0][0]) * (j[0][0] - k[0][0]) + (j[0][1] - k[0][1]) * (j[0][1] - k[0][1]))
					if distance < distance1:
						distance1 = distance
				if distance1 < distance0 / 2:
					nothei1.append(j)
		
		notheightPoints[1] = nothei1
		
		for i in range(0, len(notheightPoints[0])):
			notheightPoints[0][i] = [notheightPoints[0][i][0][0], notheightPoints[0][i][0][1]]
		for i in range(0, len(notheightPoints[1])):
			notheightPoints[1][i] = [notheightPoints[1][i][0][0], notheightPoints[1][i][0][1]]
		notheightPoints[0].sort()
		notheightPoints[1].sort()
		for i in range(0, len(notheightPoints[0])):
			notheightPoints[0][i] = [[notheightPoints[0][i][0], notheightPoints[0][i][1]]]
		for i in range(0, len(notheightPoints[1])):
			notheightPoints[1][i] = [[notheightPoints[1][i][0], notheightPoints[1][i][1]]]
		
		xlist = []
		for i in notheightPoints[0]:
			xlist.append((i[0][0], i[0][1], 0))
		for i in notheightPoints[1]:
			xlist.append((i[0][0], i[0][1], 1))
		xlist.sort(key=itemgetter(0))
		
		addPoints = [[], []]
		for i in range(0, len(xlist)):
			pl = i - 1
			pr = i + 1
			if xlist[i][2] == 0:
				n = 0
				m = 1
			else:
				n = 1
				m = 0
			while pl >= 0 and xlist[pl][2] == xlist[i][2]:
				pl = pl - 1
			while pr < len(xlist) and xlist[pr][2] == xlist[i][2]:
				pr = pr + 1
			if pl >= 0 and pr < len(xlist):
				y = (xlist[pl][1]) * (xlist[pr][0] - xlist[i][0]) / (xlist[pr][0] - xlist[pl][0]) + (xlist[pr][1]) * (
						xlist[i][0] - xlist[pl][0]) / (xlist[pr][0] - xlist[pl][0])
				addPoints[n].append([[int(xlist[i][0]), int((xlist[i][1] - y) / 3 + y)]])
				addPoints[m].append([[int(xlist[i][0]), int((xlist[i][1] - y) * 2 / 3 + y)]])
			elif pl < 0:
				addPoints[n].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pr][1]) / 3 + xlist[pr][1])]])
				addPoints[m].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pr][1]) * 2 / 3 + xlist[pr][1])]])
			else:
				addPoints[n].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pl][1]) / 3 + xlist[pl][1])]])
				addPoints[m].append([[int(xlist[i][0]), int((xlist[i][1] - xlist[pl][1]) * 2 / 3 + xlist[pl][1])]])
		
		notheightPoints[0] = rotatePoints(notheightPoints[0], rect[0], angle)
		notheightPoints[1] = rotatePoints(notheightPoints[1], rect[0], angle)
		addPoints[0] = rotatePoints(addPoints[0], rect[0], angle)
		addPoints[1] = rotatePoints(addPoints[1], rect[0], angle)
		
		m = cv2.moments(numpy.array(notheightPoints[1]))
		cx1 = int(m["m10"] / m["m00"])
		cy1 = int(m["m01"] / m["m00"])
		
		addPoints[1].reverse()
		notheightPoints[1].reverse()
		first = notheightPoints[0] + addPoints[1]
		second = addPoints[0] + addPoints[1]
		third = addPoints[0] + notheightPoints[1]
		
		i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
		firstmask = cv2.fillPoly(i, np.array([first], np.int32), 255)
		
		i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
		secondmask = cv2.fillPoly(i, np.array([second], np.int32), 255)
		
		i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
		thirdmask = cv2.fillPoly(i, np.array([third], np.int32), 255)
		
		firstdensity = areaaveragedensity(fibrosis, greyimg, firstmask)
		seconddensity = areaaveragedensity(fibrosis, greyimg, secondmask)
		thirddensity = areaaveragedensity(fibrosis, greyimg, thirdmask)
		
		box1 = cv2.boxPoints(rect1)
		box1 = np.array(box1)
		for i in range(0, 2):
			max = sqrt((box1[i][0] - cx1) * (box1[i][0] - cx1) + (box1[i][1] - cy1) * (box1[i][1] - cy1))
			n = i
			for j in range(i, 4):
				if sqrt((box1[j][0] - cx1) * (box1[j][0] - cx1) + (box1[j][1] - cy1) * (box1[j][1] - cy1)) > max:
					max = sqrt((box1[j][0] - cx1) * (box1[j][0] - cx1) + (box1[j][1] - cy1) * (box1[j][1] - cy1))
					n = j
			k = (box1[i][0], box1[i][1])
			box1[i] = box1[n]
			box1[n] = [k[0], k[1]]
		
		firstarea = 'Endocardium'
		thirdarea = 'Epicardium'
		otherline = notheightPoints[0]
		
		if sqrt((box1[0][0] - otherline[0][0][0]) * (box1[0][0] - otherline[0][0][0]) + (
				box1[0][1] - otherline[0][0][1]) * (box1[0][1] - otherline[0][0][1])) > sqrt(
			(box1[1][0] - otherline[0][0][0]) * (box1[1][0] - otherline[0][0][0]) + (
					box1[1][1] - otherline[0][0][1]) * (box1[1][1] - otherline[0][0][1])):
			otherline.append([[box1[0][0], box1[0][1]]])
			otherline.append([[box1[1][0], box1[1][1]]])
		else:
			otherline.append([[box1[1][0], box1[1][1]]])
			otherline.append([[box1[0][0], box1[0][1]]])
		
		i = np.zeros((workingDimensions[1], workingDimensions[0]), np.uint8)
		othermask = cv2.fillPoly(i, np.array([otherline], np.int32), 255)
		otherdensity = areaaveragedensity(fibrosis, greyimg, othermask)
		
		self.annotation.list.append(
			Annotation(self.imageLabel, self.geshi, firstarea + ':' + str(firstdensity * 100)[0:4] + '%', "Polygon",
			           self.annotation))
		for i in first:
			self.annotation.list[len(self.annotation.list) - 1].list.append(
				(i[0][0] * self.geshi.bei[level], i[0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].list.append(
			(first[0][0][0] * self.geshi.bei[level], first[0][0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].ending()
		self.annotation.list[len(self.annotation.list) - 1].setColor('#FFC0CB')
		self.annotation.list.append(
			Annotation(self.imageLabel, self.geshi, 'Midwall:' + str(seconddensity * 100)[0:4] + '%', "Polygon",
			           self.annotation))
		for i in second:
			self.annotation.list[len(self.annotation.list) - 1].list.append(
				(i[0][0] * self.geshi.bei[level], i[0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].list.append(
			(second[0][0][0] * self.geshi.bei[level], second[0][0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].ending()
		self.annotation.list[len(self.annotation.list) - 1].setColor('#000000')
		self.annotation.list.append(
			Annotation(self.imageLabel, self.geshi, thirdarea + ':' + str(thirddensity * 100)[0:4] + '%', "Polygon",
			           self.annotation))
		for i in third:
			self.annotation.list[len(self.annotation.list) - 1].list.append(
				(i[0][0] * self.geshi.bei[level], i[0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].list.append(
			(third[0][0][0] * self.geshi.bei[level], third[0][0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].ending()
		self.annotation.list[len(self.annotation.list) - 1].setColor('#32CD32')
		self.annotation.list.append(
			Annotation(self.imageLabel, self.geshi, 'Trabecular:' + str(otherdensity * 100)[0:4] + '%', "Polygon",
			           self.annotation))
		for i in otherline:
			self.annotation.list[len(self.annotation.list) - 1].list.append(
				(i[0][0] * self.geshi.bei[level], i[0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].list.append(
			(otherline[0][0][0] * self.geshi.bei[level], otherline[0][0][1] * self.geshi.bei[level]))
		self.annotation.list[len(self.annotation.list) - 1].ending()
		self.annotation.list[len(self.annotation.list) - 1].setColor('#6495ED')


app = QApplication(sys.argv)
app.setOrganizationName("Qtrac Ltd")
app.setOrganizationDomain("qtrac.edu")
app.setApplicationName(title)
app.setWindowIcon(QIcon(":/icon.png"))
form = MainWindow()
form.show()
app.exec_()
cv2.destroyAllWindows()
