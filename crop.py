import cv2
import os
import torch
import numpy as np




def cutimg(img, num=9,overlap_factor=192):

    print(img.shape)
    """a,b,c,d,分别存储A,B1,B2,B3的256*256块"""
    factor = int(np.sqrt(num))
    x=4
    a=[]
    a1=[]
    b1=[]
    c1=[]
    d1=[]
    e1=[]
    b=[]
    c=[]
    d=[]
    e=[]
    for i in range(factor):
        a1 = []
        b1 = []
        c1 = []
        d1 = []
        e1=[]
        for ii in range(factor):
            img_temp1 = img[i * overlap_factor:(i + 2) * overlap_factor, ii * overlap_factor:(ii + 2) * overlap_factor]
            img_temp2 = img[i * overlap_factor:(i + 2) * overlap_factor, (ii+x) * overlap_factor:(ii +x+2) * overlap_factor]
            img_temp3 = img[i * overlap_factor:(i + 2) * overlap_factor, (ii+2*x) * overlap_factor:(ii + 2*x+2) * overlap_factor]
            img_temp4 = img[i * overlap_factor:(i + 2) * overlap_factor, (ii+3*x) * overlap_factor:(ii + 3*x+2) * overlap_factor]
            img_temp5 = img[i * overlap_factor:(i + 2) * overlap_factor, (ii+4*x) * overlap_factor:(ii + 4*x+2) * overlap_factor]
            print(i)
            print(img_temp1.shape,img_temp2.shape,img_temp3.shape,img_temp4.shape,img_temp5.shape)
            a1.append(img_temp1)
            b1.append(img_temp2)
            c1.append(img_temp3)
            d1.append(img_temp4)
            e1.append(img_temp5)
        a.append(a1)
        b.append(b1)
        c.append(c1)
        d.append(d1)
        e.append(e1)
    return a,b,c,d,e

# img=cv2.imread('./data_test/173.jpg')
# a,b,c,d=cutimg(img,9)
# for i in range(9):
#     img=np.hstack((a[i],b[i],c[i],d[i]))
#     cv2.imwrite('./save/{}.jpg'.format(i),img)

# img=cv2.imread('./0.jpg')
# a,b,c,d=cutimg(img,25)
# cv2.imshow('1',a[2])
# cv2.waitKey(0)