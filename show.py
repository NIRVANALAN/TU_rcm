#coding=utf-8
from geshi import*
from openslide import*
import numpy
from math import *
from PyQt5.QtCore import*
from PyQt5.QtGui import*
from PyQt5.QtWidgets import*
from thumbnail import*
from cv2 import*

class showimage():
    '''
    图片展示类
    '''
    def __init__(self,slide,father):
        self.slide = slide
        self.father = father
        self.PictureMaxLocation = [0,0,0,0]
        self.PictureLocation = []
        self.PictureList = []
        self.labellist = []
        self.LevelNow = 0
        self.thumbnail = None
        QTimer.singleShot(0,self.thumbinit)

    def new(self,geshi,father,restart):
        '''
        原图展示函数,分块加载
        :param geshi: 当前视野参数
        :param father: 父部件
        :param restart: 是否重新加载块
        :return:
        '''
        beilv = geshi.b/geshi.bei[geshi.l]
        w = int(geshi.w*geshi.b)
        h = int(geshi.h*geshi.b)
        self.a = int(geshi.w*beilv)
        self.b = int(geshi.h*beilv)
        if self.LevelNow != geshi.l or restart:
            self.PictureMaxLocation = [0,0,0,0]
            self.PictureLocation = []
            self.PictureList = []
            self.LevelNow = geshi.l
            for i in self.labellist:
                i.hide()
                i.destroy()
                del i
            for i in range(int(geshi.x-(w/2)-(150*geshi.bei[geshi.l])),int(geshi.x+(w/2)+(150*geshi.bei[geshi.l])),int(300*geshi.bei[geshi.l])):
                for j in range(int(geshi.y-(h/2)-100*geshi.bei[geshi.l]),int(geshi.y+(h/2)+100*geshi.bei[geshi.l]),int(200*geshi.bei[geshi.l])):
                    middle = numpy.array(self.slide.read_region((i,j),geshi.l,(300,200)))
                    self.PictureList.append(middle)
                    self.PictureLocation.append((i,j))
        else:
            k=0
            for i in range(0,len(self.PictureLocation)):
                if self.isin(geshi.x-int(w/2),geshi.x+int(w/2),geshi.y-int(h/2),geshi.y+int(h/2),self.PictureLocation[i-k],geshi.bei[geshi.l]):
                    del self.PictureLocation[i-k]
                    del self.PictureList[i-k]
                    k += 1
            self.setMax(geshi.bei[geshi.l])
            blockw = int(300*geshi.bei[geshi.l])
            blockh = int(200*geshi.bei[geshi.l])
            while geshi.x-int(w/2) < self.PictureMaxLocation[0]:
                for j in range(self.PictureMaxLocation[1],self.PictureMaxLocation[3],blockh):
                    middle = numpy.array(self.slide.read_region((self.PictureMaxLocation[0]-blockw,j),geshi.l,(300,200)))
                    self.PictureList.append(middle)
                    self.PictureLocation.append((self.PictureMaxLocation[0]-blockw,j))
                self.PictureMaxLocation[0] -= blockw
            while geshi.x+int(w/2) > self.PictureMaxLocation[2]:
                for j in range(self.PictureMaxLocation[1],self.PictureMaxLocation[3],blockh):
                    middle = numpy.array(self.slide.read_region((self.PictureMaxLocation[2],j),geshi.l,(300,200)))
                    self.PictureList.append(middle)
                    self.PictureLocation.append((self.PictureMaxLocation[2],j))
                self.PictureMaxLocation[2] += blockw
            while geshi.y-int(h/2) < self.PictureMaxLocation[1]:
                for i in range(self.PictureMaxLocation[0],self.PictureMaxLocation[2],blockw):
                    middle = numpy.array(self.slide.read_region((i,self.PictureMaxLocation[1]-blockh),geshi.l,(300,200)))
                    self.PictureList.append(middle)
                    self.PictureLocation.append((i,self.PictureMaxLocation[1]-blockh))
                self.PictureMaxLocation[1] -= blockh
            while geshi.y+int(h/2) > self.PictureMaxLocation[3]:
                for i in range(self.PictureMaxLocation[0],self.PictureMaxLocation[2],blockw):
                    middle = numpy.array(self.slide.read_region((i,self.PictureMaxLocation[3]),geshi.l,(300,200)))
                    self.PictureList.append(middle)
                    self.PictureLocation.append((i,self.PictureMaxLocation[3]))
                self.PictureMaxLocation[3] += blockh
        if self.thumbnail is not None:
            self.thumbnail.set(geshi.x-geshi.w*geshi.b/2,geshi.y-geshi.h*geshi.b/2,geshi.w*geshi.b,geshi.h*geshi.b)
        self.setMax(geshi.bei[geshi.l])

    def prorun(self,geshi,funclist=[],arglist = []):
        '''
        图片处理函数
        :param geshi: 当前视野参数
        :param func: 当前使用处理函数名
        :return:
        '''
        self.father.clear()
        if self.slide is None:
            return
        w = int(geshi.w*geshi.b)
        h = int(geshi.h*geshi.b)
        location = range(0,len(self.PictureLocation))
        e1 = 0
        r1 = 0
        self.region = None
        wn = int(ceil((self.PictureMaxLocation[2]-self.PictureMaxLocation[0])/geshi.bei[geshi.l]/300))
        hn = int(ceil((self.PictureMaxLocation[3]-self.PictureMaxLocation[1])/geshi.bei[geshi.l]/200))
        for i in range(0,len(self.PictureLocation)):
            e = float((self.PictureLocation[i][1]-geshi.y+int(h/2))/geshi.bei[geshi.l])
            r = float((self.PictureLocation[i][0]-geshi.x+int(w/2))/geshi.bei[geshi.l])
            location[int(ceil(e/200)*wn+ceil(r/300))] = i
            if int(ceil(e/200)*wn+ceil(r/300)) == 0:
                e1 = int(-e)
                r1 = int(-r)
        for y in range(0,int(hn)):
            for x in range(0,int(wn)):
                if x == 0:
                    row = self.PictureList[location[y*wn]]
                else:
                    row = numpy.concatenate((row,self.PictureList[location[y*wn+x]]),axis=1)
            if y ==0:
                self.region = row
            else:
                self.region = numpy.concatenate((self.region,row),axis=0)
        self.region = numpy.array(self.region[int(e1):int(self.b+e1),int(r1):int(self.a+r1)])
        for i in self.labellist:
            i.hide()
        self.region = cv2.cvtColor(self.region,cv2.COLOR_RGBA2BGRA)
        number = None
        for i in range(0,len(funclist)):
            result = funclist[i](self.region,arglist[i],geshi)
            self.region = result['image']
            if result.has_key('number'):
                number = result['number']
        self.a = len(self.region[0])
        self.b = len(self.region)
        image = QImage(self.region,int(self.a),int(self.b),QImage.Format_ARGB32)
        self.father.setPixmap(QPixmap.fromImage(image.scaled(self.father.width(),self.father.height())))
        return number

    def isin(self,x1,x2,y1,y2,c,k):
        '''
        当前块是否去除
        '''
        if c[0]+(300*k)<x1 or c[0]>x2 or c[1]+(200*k)<y1 or c[1]>y2:
            return True
        else:
            return False

    def setMax(self,k):
        '''
        计算当前显示最大范围函数
        :param k: 当前倍数
        :return:
        '''
        xi = self.PictureLocation[0][0]
        yi = self.PictureLocation[0][1]
        xa = self.PictureLocation[0][0]+300*k
        ya = self.PictureLocation[0][1]+200*k
        for i in range(0,len(self.PictureLocation)):
            if xi>self.PictureLocation[i][0]:
                xi = self.PictureLocation[i][0]
            if yi>self.PictureLocation[i][1]:
                yi = self.PictureLocation[i][1]
            if xa<self.PictureLocation[i][0]+300*k:
                xa = self.PictureLocation[i][0]+300*k
            if ya<self.PictureLocation[i][1]+200*k:
                ya = self.PictureLocation[i][1]+200*k
        self.PictureMaxLocation = [int(xi),int(yi),int(xa),int(ya)]

    def __del__(self):
        '''
        深删除函数
        :return:
        '''
        for i in self.labellist:
            i.hide()
            del i
        self.thumbnail.hide()
        del self.thumbnail

    def thumbinit(self):
        '''
        略所图函数
        :return:
        '''
        self.thumbnail = ThumbNail(self.slide,self.father)
        self.thumbnail.show()
