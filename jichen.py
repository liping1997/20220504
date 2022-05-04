import cv2
import os
import numpy as np
from crop import *
from merge import *
import math



def generatetestpicture(test_folder,save_folder,num=25):         #将test_file文件夹下的图片分成num份，拼接之后保存在save_file中，save_file通常是datasets/test
    dir_num=len(os.listdir(test_folder))
    for k in range(dir_num):
        img = cv2.imread('{}/{}.jpg'.format(test_folder,k))
        a, b, c, d = cutimg(img,num)       #核心代码--切块

        for i in range(int(math.sqrt(num))):
            for j in range(int(math.sqrt(num))):
                img1 = np.hstack((a[i][j], b[i][j], c[i][j], d[i][j]))
                cv2.imwrite('{}/{}_{}_{}.jpg'.format(save_folder,k,i,j), img1,[int(cv2.IMWRITE_JPEG_QUALITY), 100])

def finalpicture(test_folder,input_folder,num,save_folder):      #test_folder和上面一致，input_folder是results中images文件夹，save_folder一般是savewjj
    dat_list1 = []
    dat_list2 = []
    dat_list3 = []
    dir_num=len(os.listdir(test_folder))
    for k in range(dir_num):
        for i in range(num):
            for j in range(num):
                img1 = cv2.imread('{}/{}_{}_{}_{}.png'.format(input_folder,k,i, j, 'fake_B0'))

                img2 = cv2.imread('{}/{}_{}_{}_{}.png'.format(input_folder,k,i, j, 'fake_B1'))
                img3 = cv2.imread('{}/{}_{}_{}_{}.png'.format(input_folder,k,i, j, 'fake_B2'))
                dat_list1.append(img1)
                dat_list2.append(img2)
                dat_list3.append(img3)
    for i in range(dir_num):
######################################################################################################
        # h1 = imgFusion(dat_list1[0+9*i:3+9*i])
        # h2 = imgFusion(dat_list1[3+9*i:6+9*i])
        # h3 = imgFusion(dat_list1[6+9*i:9+9*i])
        #
        # hh1=[h1,h2,h3]
        # dat1=imgFusion(hh1,128,False)
        # h4 = imgFusion(dat_list2[0 + 9 * i:3 + 9 * i])
        # h5 = imgFusion(dat_list2[3 + 9 * i:6 + 9 * i])
        # h6 = imgFusion(dat_list2[6 + 9 * i:9 + 9 * i])
        #
        # hh2 = [h4,h5,h6]
        # dat2 = imgFusion(hh2, 128, False)
        # h7 = imgFusion(dat_list3[0 + 9 * i:3 + 9 * i])
        # h8 = imgFusion(dat_list3[3 + 9 * i:6 + 9 * i])
        # h9 = imgFusion(dat_list3[6 + 9 * i:9 + 9 * i])
        #
        # hh3 = [h7,h8,h9]
        # dat3 = imgFusion(hh3, 128, False)
        #
        # dat4=np.zeros((512,512,3))
        # dat4=np.uint8(dat4)
        # dat=np.hstack((dat4,dat1,dat2,dat3))
###########################################################################
        print(1)
        h1 = imgFusion(dat_list1[0 + 25 * i:5 + 25 * i])
        h2 = imgFusion(dat_list1[5+25*i:10+25*i])
        h3 = imgFusion(dat_list1[10+25*i:15+25*i])

        h4 = imgFusion(dat_list1[15+25*i:20+25*i])
        h5 = imgFusion(dat_list1[20+25*i:25+25*i])
        hh1=[h1,h2,h3,h4,h5]
        dat1=imgFusion(hh1,128,False)
        print(2)
        h11 = imgFusion(dat_list2[0 + 25 * i:5 + 25 * i])
        h21 = imgFusion(dat_list2[5+25*i:10+25*i])
        h31 = imgFusion(dat_list2[10+25*i:15+25*i])
        h41 = imgFusion(dat_list2[15+25*i:20+25*i])
        h51 = imgFusion(dat_list2[20+25*i:25+25*i])
        hh11=[h11,h21,h31,h41,h51]
        dat11=imgFusion(hh11,128,False)
        print(3)
        h12 = imgFusion(dat_list3[0 + 25 * i:5 + 25 * i])
        h22 = imgFusion(dat_list3[5+25*i:10+25*i])
        h32 = imgFusion(dat_list3[10+25*i:15+25*i])
        h42 = imgFusion(dat_list3[15+25*i:20+25*i])
        h52 = imgFusion(dat_list3[20+25*i:25+25*i])
        hh12=[h12,h22,h32,h42,h52]
        dat12=imgFusion(hh12,128,False)





        print(4)
        dat4=np.zeros((768,768,3))
        dat4=np.uint8(dat4)
        dat=np.hstack((dat4,dat1,dat11,dat12))











        img4=cv2.imread('./{}/{}.jpg'.format(test_folder,i))

        dat=np.vstack((img4,dat))


        cv2.imwrite('{}/{}.jpg'.format(save_folder,i), dat,[int(cv2.IMWRITE_JPEG_QUALITY), 100])
        print("第{}张图片已经保存".format(i))

# generatetestpicture('./test','dataset/test',num=25)
finalpicture('./test','./results/FA_sequenc/test_latest/images',5,'save')