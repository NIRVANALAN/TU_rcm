import cv2
import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn import preprocessing
from itertools import cycle
from mpl_toolkits.mplot3d import Axes3D


patients = ['25845','28330','29708','30638','31398','35485']

inputFile = open('./data/maxresult.txt','r')
max = {}
for line in inputFile:
    line = line.strip('\n')
    maxs = line.split(',')
    print maxs
    max[maxs[0]] = {}
    max[maxs[0]]['pixelMax'] = int(maxs[1])
    max[maxs[0]]['fibrosisMax'] = float(maxs[2])
    max[maxs[0]]['holeMax'] = int(maxs[3])
    max[maxs[0]]['nuclearMax'] = int(maxs[4])
    max[maxs[0]]['blockNumberMax'] = int(maxs[5])
    max[maxs[0]]['blockAreaMax'] = int(maxs[6])
inputFile.close()
print max

result = []
count = 0
totalmax = [0]*7
totalsmall = [int(maxs[1]),float(maxs[2]),int(maxs[3]),int(maxs[4]),int(maxs[5]),int(maxs[6]),4]
for nu in range(0,len(patients)):
    patient = patients[nu]
    print patient
    for kk in range(1,7):
        if (patient == '29708' and kk ==2) or (patient == '30638' and kk == 5) or (patient == '31398' and kk == 6):# or not(kk==6)  :
            continue
        print kk
        picture = patient + '-' + str(kk)
        path = ['./data/' + picture + '0.png','./data/' + picture + '1.png']
        image = [cv2.imread(path[0],-1),cv2.imread(path[1])]
        s,a,b,c = cv2.split(image[0])
        d,e,f = cv2.split(image[1])
        s = s * max[picture]['pixelMax']
        s = s / 255
        a = a * max[picture]['fibrosisMax']
        a = a / 255
        b = np.array(b,np.uint16)
        b = b * max[picture]['holeMax']
        b = b / 255
        c = np.array(c,np.uint16)
        c = c * max[picture]['nuclearMax']
        c = c / 255
        d = np.array(d,np.uint32)
        d = d * max[picture]['blockNumberMax']
        d = d / 255
        e = np.array(e,np.uint64)
        e = e * max[picture]['blockAreaMax']
        e = e / 255
        f = f / 51
        for j in range(0,len(s)):
            for i in range(0,len(s[0])):
                if s[j][i] != 0 and b[j][i] < c[j][i] and c[j][i]*float(1000000)/float(s[j][i])<100 and f[j][i] == 2:
                    if a[j][i]>1:
                        a[j][i] = 1
                    if f[j][i] == 0:
                        f[j][i] = 2
                    beilv = float(s[j][i])/float(1000000)
                    if d[j][i] !=0:
                        e[j][i] = s[j][i]*a[j][i]/d[j][i]
                    else:
                        e[j][i] = 0
                    if f[j][i] == 1:
                        result.append([a[j][i],b[j][i]/beilv,c[j][i]/beilv,d[j][i]/beilv,e[j][i],100,0,0,i,j])
                    elif f[j][i] == 2:
                        result.append([a[j][i],b[j][i]/beilv,c[j][i]/beilv,d[j][i]/beilv,e[j][i],0,100,0,i,j])
                    elif f[j][i] == 3:
                        result.append([a[j][i],b[j][i]/beilv,c[j][i]/beilv,d[j][i]/beilv,e[j][i],0,0,100,i,j])
                    else:
                        result.append([a[j][i],b[j][i]/beilv,c[j][i]/beilv,d[j][i]/beilv,e[j][i],0,0,0,i,j])
                    '''
                    if s[j][i] > totalmax[0]:
                        totalmax[0] = s[j][i]
                    if a[j][i] > totalmax[1]:
                        totalmax[1] = a[j][i]
                    if b[j][i] > totalmax[2]:
                        totalmax[2] = b[j][i]
                    if c[j][i] > totalmax[3]:
                        totalmax[3] = c[j][i]
                    if d[j][i] > totalmax[4]:
                        totalmax[4] = d[j][i]
                    if e[j][i] > totalmax[5]:
                        totalmax[5] = e[j][i]
                    if f[j][i] > totalmax[6]:
                        totalmax[6] = f[j][i]

                    if s[j][i] < totalsmall[0]:
                        totalsmall[0] = s[j][i]
                    if a[j][i] < totalsmall[1]:
                        totalsmall[1] = a[j][i]
                    if b[j][i] < totalsmall[2]:
                        totalsmall[2] = b[j][i]
                    if c[j][i] < totalsmall[3]:
                        totalsmall[3] = c[j][i]
                    if d[j][i] < totalsmall[4]:
                        totalsmall[4] = d[j][i]
                    if e[j][i] < totalsmall[5]:
                        totalsmall[5] = e[j][i]
                    if f[j][i] < totalsmall[6]:
                        totalsmall[6] = f[j][i]
                '''

print len(result)
result = np.array(result)
resultStd = result[:,2:5]
for haha in range(0,3):
    x = resultStd[:,haha]
    print np.mean(x), np.std(x)
print
min_max_scaler = preprocessing.MinMaxScaler()
resultStd = min_max_scaler.fit_transform(resultStd)
for haha in range(0,3):
    x = resultStd[:,haha]
    print np.mean(x), np.std(x)

'''
scaler = preprocessing.StandardScaler().fit(result)
print scaler.mean_ , scaler.std_
resultStd = scaler.transform(result)
print len(result)
'''
'''
result = np.array(result)
x = result[:,4]
print np.mean(x)
print np.std(x)
plt.hist(x,range(0,2000))
plt.show()
'''
'''
result = np.array(result)
print result
print count
x = result[:,3]
y = result[:,6]
plt.scatter(x,y)
plt.show()
'''
'''
print totalmax
print totalsmall
for i in range(0,len(result)):
    for j in range(0,7):
        result[i][j] = (result[i][j]-totalsmall[j])*100/(totalmax[j]-totalsmall[j])
'''
'''
for i in range(6,7,1):
    clf = KMeans(n_clusters=i,n_init=20)
    clf.fit(result)
    print i, clf.inertia_,clf.cluster_centers_
'''

resultStd = np.array(resultStd)

bandwidth = estimate_bandwidth(resultStd, quantile = 0.1, n_samples = 5000)

ms = MeanShift(bandwidth = bandwidth, bin_seeding = True)
ms.fit(resultStd)
labels = ms.labels_
cluster_centers = ms.cluster_centers_

labels_unique = np.unique(labels)
n_clusters_ = len(labels_unique)

labels = labels
print n_clusters_

la = labels.tolist()
for haha in range(0,n_clusters_):
    if la.count(haha)>0:
        print cluster_centers[haha],la.count(haha)

'''
colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
for k, col in zip(range(n_clusters_), colors):
    my_members = labels == k
    qwer = []
    wert = 10
    for nkx in range(0,wert):
        for nky in range(0,wert):
            x0 = (resultStd[my_members, 0].max()-resultStd[my_members, 0].min())*nkx/wert + resultStd[my_members, 0].min()
            gex = (resultStd[my_members, 0].max()-resultStd[my_members, 0].min())/wert
            y0 = (resultStd[my_members, 1].max()-resultStd[my_members, 1].min())*nky/wert + resultStd[my_members, 1].min()
            gey = (resultStd[my_members, 1].max()-resultStd[my_members, 1].min())/wert
            numbercount = 0
            for we in resultStd[my_members]:
                if we[0]>=x0 and we[0]<x0+gex and we[1]>=y0 and we[1]<y0+gey:
                    numbercount =  numbercount + 1
            if  numbercount>len(resultStd[my_members])/500+30:
                qwer.append([x0+gex/2,y0+gey/2])
    cluster_center = cluster_centers[k]
    if len(qwer)>0 and len(resultStd[my_members])>200:
        qwer = np.array(qwer)
        plt.plot(qwer[:,0], qwer[:,1], col + '.')
    plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)
plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()
'''
colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
ax = plt.subplot(111,projection='3d')
for k, col in zip(range(n_clusters_), colors):
    my_members = labels == k
    cluster_center = cluster_centers[k]
    ax.scatter(resultStd[my_members, 0], resultStd[my_members, 1],resultStd[my_members, 2],c=col,alpha=0.3,s=10)
plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()
'''
labels = labels + 1
n = 0
for nu in range(0,6):
    for ci in range(0,6):
        nj = 0
        ni = 0
        picture = patients[nu] + '-' + str(ci+1)
        path = './data/' + picture + '1.png'
        image = cv2.imread(path)
        image = np.zeros((len(image),len(image[0])),np.uint8)
        while nj< result[n][9]or (nj== result[n][9] and ni<=result[n][8]):
            print result[n][9],result[n][8],labels[n]
            image[result[n][9]][result[n][8]] = int(labels[n])
            ni = result[n][8]
            nj = result[n][9]
            n = n+1
        plt.imshow(image)
        plt.show()
'''
