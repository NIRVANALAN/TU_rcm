#coding=utf-8
import openslide

class geshi():
    '''
    当前视野参数
    '''
    def __init__(self,slide,iw,ih):
        self.wa , self.ha = slide.dimensions    #原图宽和高
        self.w = iw #屏幕宽
        self.h = ih #屏幕高
        self.x = int(iw*slide.level_downsamples[slide.level_count-1]/2) #视野中心总横坐标
        self.y = int(ih*slide.level_downsamples[slide.level_count-1]/2) #视野中心总纵坐标
        self.la = slide.level_count-1   #最大层数
        self.l = self.la    #当前层数
        self.bei = []   #当前倍数
        for i in range(0,self.la+1):    #层数对应倍数
            self.bei.append(slide.level_downsamples[i])
        self.b = self.bei[self.l]

    def setx(self,x):
        '''
        设置视野中心横坐标函数
        :param x: 总横坐标
        :return:
        '''
        if x>self.wa-(self.w/2):
            self.x = self.wa-(self.w/2)
        elif x<int(self.w/2):
            self.x = int(self.w/2)
        else:
            self.x = x

    def sety(self,y):
        '''
        设置视野中心纵坐标函数
        :param y: 总纵坐标
        :return:
        '''
        if y>self.ha-(self.h/2):
            self.y = self.ha-(self.h/2)
        elif y<int(self.h/2):
            self.y = int(self.h/2)
        else:
            self.y = y

    def setw(self,w):
        '''
        设置屏幕宽度函数
        :param w: 屏幕宽度
        :return:
        '''
        self.w = w
        self.setx(self.x)

    def seth(self,h):
        '''
        设置屏幕高度函数
        :param h: 屏幕高度
        :return:
        '''
        self.h = h
        self.sety(self.y)

    def setl(self,level):
        '''
        设置层数函数
        :param level: 新层数
        :return:
        '''
        if level>self.la:
            self.l = self.la
        elif level<0:
            self.l = 0
        else:
            self.l = level
        self.b = self.bei[self.l]

    def setb(self,beishu):
        '''
        设置倍数函数
        :param beishu: 新倍数
        :return:
        '''
        if beishu<1:
            self.b = 1
        else:
            self.b = beishu
        self.l = self.getbest(self.b)

    def getbest(self,beishu):
        '''
        得到当前最好层数函数
        :param beishu: 倍数
        :return: 对应最好层数
        '''
        for i in range(0,self.la+1):
            if beishu>self.bei[self.la-i]:
                return self.la-i
        return 0






