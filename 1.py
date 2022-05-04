import numpy as np
import cv2
import os
a=0
for i in os.listdir('test'):
    path=os.path.join('test',i)
    img=cv2.imread(path)[:,2304:3072,:]
    cv2.imwrite('{}.jpg'.format(a),img)
    a+=1


