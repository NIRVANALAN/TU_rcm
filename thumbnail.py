#coding=utf-8
import numpy
from PyQt5.QtCore import*
from PyQt5.QtGui import*
from PyQt5.QtWidgets import*
from openslide import*

class ThumbNail(QLabel):
    '''
    略缩图类
    '''
    def __init__(self,slide,father):
        super(ThumbNail,self).__init__(father)
        self.wa,self.ha = slide.dimensions
        self.thumbnail = numpy.array(slide.get_thumbnail((200,200*self.ha/self.wa)))
        self.pictureheight = len(self.thumbnail)
        self.picturewidth = len(self.thumbnail[0])
        self.father = father
        if father.width()-self.picturewidth>20 and father.height()-self.pictureheight>20:
            self.setGeometry(QRect(father.width()-self.picturewidth-20,father.height()-self.pictureheight-20,self.picturewidth,self.pictureheight))
        else:
            self.setGeometry(QRect(0,0,self.picturewidth,self.pictureheight))
        image = QImage(self.thumbnail,self.picturewidth,self.pictureheight,QImage.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(image.scaled(self.picturewidth,self.pictureheight)))
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    def paintEvent(self,QPaintEvent):
        '''
        绘画函数
        :param QPaintEvent:绘画事件
        :return:
        '''
        super(ThumbNail,self).paintEvent(QPaintEvent)
        if self.father.width()-self.picturewidth>20 and self.father.height()-self.pictureheight>20:
            self.setGeometry(QRect(self.father.width()-self.picturewidth-20,self.father.height()-self.pictureheight-20,self.picturewidth,self.pictureheight))
        else:
            self.setGeometry(QRect(0,0,self.picturewidth,self.pictureheight))
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QPen(QColor(255,0,0),4))
        painter.drawRect(self.x,self.y,self.w,self.h)
        painter.setPen(QPen(QColor(0,0,0),2))
        painter.drawRect(0,0,self.picturewidth,self.pictureheight)
        self.raise_()
        painter.end()

    def set(self,x,y,w,h):
        '''
        设置当前红框位置函数
        :param x: 中心横坐标
        :param y: 中心纵坐标
        :param w: 宽度
        :param h: 高度
        :return:
        '''
        self.x = x*self.picturewidth/self.wa
        self.y = y*self.pictureheight/self.ha
        self.w = w*self.picturewidth/self.wa
        self.h = h*self.pictureheight/self.ha
        self.raise_()
        self.update()
