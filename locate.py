# -*- coding: UTF-8 -*-
'''
python 2.6
raspberry pi with 2014-01-07-wheezy-raspbian

定位 algorithm

1. 定位原理: thesis 第二節
2. 訊號的 input 檔案格式必須為 pathX.Xm.S3_data 
3. 分為[random選擇]跟[依據plane來選擇]兩種方法來計算位置

'''

import os
import re
from operator import itemgetter, attrgetter
import matplotlib.pyplot as plt
from pylab import *
import numpy
from matplotlib.pyplot import *
import math
import time
import random

phone_loc = [ 50, 37 ]

class Point:
    def __init__(self, trk_len, max_rssi, mean_rssi, x, y, max_dist, mean_dist):
        self.trk_len = float(trk_len) # 從起點走所經過的距離
        self.x = float(x)
        self.y = float(y)
        self.max_rssi = int(max_rssi)
        self.max_dist = float(max_dist)
        self.mean_rssi = float(mean_rssi)
        self.maen_dist = float(mean_dist)

def parseData(filename):
    signals = []
    with open(filename) as file:
        for line in file:
            signals.append(int(line))
    return signals

def getFile():
    coeffs = [-0.03574875, -0.99455495]  # from RSSI v.s. distance expirement
    path = []
    path.append([])
    path.append([])
    path.append([])
    directory = os.listdir('.')
    for filename in directory:
        if filename[-9:] == 'm.S3_data':
			# 紀錄的檔案格式: pathX.Xm.S3_data
            match = re.search('^path(\d+).(\d+)m.S3(.*)$', filename)
            if match:
                path_no = int(match.group(1)) # path 編號
                trk_len = int(match.group(2)) # 從起點走所經過的距離
                signals = parseData(filename)
                max_rssi = max(signals)
                threshold = int(len(signals)/10)
                mean_rssi = numpy.mean(sorted(signals)[threshold:-threshold])
                max_dist = 10**(coeffs[0]*max_rssi+coeffs[1])
                mean_dist = 10**(coeffs[0]*mean_rssi+coeffs[1])
                x = 80
                y = 7
                if path_no == 1:
                    x = trk_len
                else:
                    y = trk_len
                point = Point(trk_len, max_rssi, mean_rssi, x, y, max_dist, mean_dist)
                path[path_no].append(point)
    path[1] = sorted(path[1],key=attrgetter('trk_len'))
    path[2] = sorted(path[2],key=attrgetter('trk_len'))
    return path[1], path[2]
    
def getDist(x1,x2,y1,y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)
    
def getPoint(p1,p2):
    r1 = p1.max_dist
    r2 = p2.max_dist
    d12 = getDist( p1.x, p2.x, p1.y, p2.y)
    v12 = [ p2.x-p1.x, p2.y-p1.y ]
    #if r1 > 0 and d12 > 0:
    cos_theta = float(d12**2+r1**2-r2**2)/(2*r1*d12)
    cal_x = 0
    cal_y = 0
    if cos_theta < 1 and cos_theta > -1:
        sin_theta = math.sqrt(1-cos_theta**2)
        cal_x = p1.x + float(r1/d12)*(v12[0]*cos_theta-v12[1]*sin_theta)
        cal_y = p1.y + float(r1/d12)*(v12[0]*sin_theta+v12[1]*cos_theta)        
    return [cal_x, cal_y]

def method1(path1, path2):
    cal_loc1 = []
    cal_loc2 = []
    # method 1 : random
    points = path1+path2
    random.shuffle(points)
    count = 0
    while count < 100:
        random.shuffle(points)
        p1 = points[len(points)/4]
        p2 = points[len(points)/2]
        p3 = points[len(points)*3/4]
        result1 = getPoint(p1,p2)
        result2 = getPoint(p2,p3)
        result3 = getPoint(p3,p1)
        if not result1 == [0,0]:
            if not result2 == [0,0]:
                if not result3 == [0,0]:
                    count += 1
                    x = (result1[0]+result2[0]+result3[0])/3.0
                    y = (result1[1]+result2[1]+result3[1])/3.0
                    err = getDist(x, phone_loc[0], y, phone_loc[1])
                    cal_loc1.append([x,y,err])
    
    # method 2 : plan selection
    points1 = path1[:len(path1)/2]
    points2 = path1[len(path1)/2:]+path2[:len(path1)/2]
    points3 = path2[len(path1)/2:]
    
    count = 0
    while count < 100:
        p1 = points1[random.randint(0,len(points1)-1)]
        p2 = points2[random.randint(0,len(points2)-1)]
        p3 = points3[random.randint(0,len(points3)-1)]
        
        result1 = getPoint(p1,p2)
        result2 = getPoint(p2,p3)
        result3 = getPoint(p3,p1)
        
        if not result1 == [0,0]:
            if not result2 == [0,0]:
                if not result3 == [0,0]:
                    count += 1
                    x = (result1[0]+result2[0]+result3[0])/3.0
                    y = (result1[1]+result2[1]+result3[1])/3.0
                    err = getDist(x, phone_loc[0], y, phone_loc[1])
                    cal_loc2.append([x,y,err])
    return cal_loc1, cal_loc2


def triangulation(path1, path2):
    points1 = path1[:len(path1)/2]
    points2 = path1[len(path1)/2:]+path2[:len(path1)/2]
    points3 = path2[len(path1)/2:]
    cal_loc = []
    count = 0
    threshold = 200
    while count < 100:
        p1 = points1[random.randint(0,len(points1)-1)]
        p2 = points2[random.randint(0,len(points2)-1)]
        p3 = points3[random.randint(0,len(points3)-1)]
        a = getDist(p2.x, p3.x, p2.y, p3.y)
        b = getDist(p1.x, p3.x, p1.y, p3.y)
        c = getDist(p1.x, p2.x, p1.y, p2.y)
        p = (a+b+c)/2.0
        S = math.sqrt(p*(p-a)*(p-b)*(p-c))
        r = 2.0*S/(a+b+c)
        pc = [(a*p1.x+b*p2.x+c*p3.x)/(a+b+c), (a*p1.y+b*p2.y+c*p3.y)/(a+b+c)]
        min_shift = threshold
        cal_x = 0
        cal_y = 0
        cal_err = 0
        x_range = numpy.arange(pc[0]-r,pc[0]+r,0.5)
        y_range = numpy.arange(pc[1]-r,pc[1]+r,0.5)
        for x in x_range:
            for y in y_range:
                shift  = (getDist(x, p1.x, y, p1.y)-p1.max_dist)**2
                shift += (getDist(x, p2.x, y, p2.y)-p2.max_dist)**2
                shift += (getDist(x, p3.x, y, p3.y)-p3.max_dist)**2
                if shift < min_shift:
                    min_shift = shift
                    cal_err = getDist(x, phone_loc[0], y, phone_loc[1])
                    cal_x = x
                    cal_y = y
        if not cal_x == 0 and not cal_y == 0:
            count += 1
            cal_loc.append([cal_x, cal_y, cal_err])
    return cal_loc            
    
    
    
if __name__ == '__main__':
    
    path1, path2 = getFile()
    
    path1_x = [item.x for item in path1]
    path1_y = [item.y for item in path1]
    
    path2_x = [item.x for item in path2]
    path2_y = [item.y for item in path2]
    
    
    cal_result1, cal_result2 = method1(path1, path2)
    
    cal1_x = [item[0] for item in cal_result1]
    cal1_y = [item[1] for item in cal_result1]
    cal1_err = sorted([item[2] for item in cal_result1])
    print 'cal1: ', numpy.mean(cal1_err), numpy.std(cal1_err)
    
    cal2_x = [item[0] for item in cal_result2]
    cal2_y = [item[1] for item in cal_result2]
    cal2_err = sorted([item[2] for item in cal_result2])
    print 'cal2: ', numpy.mean(cal2_err), numpy.std(cal2_err)
    
    
    cal_result3 = triangulation(path1, path2)
    
    cal3_x = [item[0] for item in cal_result3]
    cal3_y = [item[1] for item in cal_result3]
    cal3_err = sorted([item[2] for item in cal_result3])
    print cal3_err
    
    plt.clf()
    plt.xlabel('x-axis')
    plt.ylabel('y-axis')
    plt.plot(path1_x,path1_y, label='path1', linewidth=3)
    plt.plot(path2_x,path2_y, label='path2', linewidth=3)
    
    plt.plot(cal1_x,cal1_y, '^', label='random')
    plt.plot(cal2_x,cal2_y, 's', label='based on plane')
    
    plt.plot([phone_loc[0]],[phone_loc[1]], 'o', label='phone')
    plt.legend(loc=2)
    grid(True)
    plt.savefig('locate.with.planes.png',dpi=300,format="png")
	
    plt.clf()
    plt.xlabel('Location Error ( m )')
    plt.ylabel('Probability ( % )')
    plt.plot(cal1_err, [ float(i)*100/float(len(cal1_err)) for i in xrange(0,len(cal1_err))], label='random')
    plt.plot(cal2_err, [ float(i)*100/float(len(cal2_err)) for i in xrange(0,len(cal2_err))], label='based on plane', linewidth=3)
    plt.legend(loc=4)
    grid(True)
    plt.savefig('CDF.png',dpi=300,format="png")
    