import cv2
from aip import AipFace  
import base64
import os
import shutil
import re
from faces_detection_api import detect_image
from face_check import face_check

def search_dir(path):
    return [f for f in os.listdir(path) if f != '.DS_Store']

def get_label(img_numpy,postion,list_all):
    img_to_recognize = img_numpy[postion[1]:postion[3] ,postion[0]:postion[2]]   # position
    cv2.imwrite('tmp/tmp.jpg',img_to_recognize)
    name_all = []
    score_all = list()
    for i in list_all:
        name,score = face_check('tmp/tmp.jpg',i)
        name_all.append(name)
        score_all.append(score)
    score = max(score_all)
    name_all = set(name_all)-set(['unknown'])
    num = len(set(name_all))
    if num == 1:
        name = list(name_all)[0]   # 输出人名
    else:
        name = 'unknown'
    return name,score

if 'tmp' not in os.listdir('./'):
    os.makedirs('tmp') 
images = search_dir('images_to_process')
paths = list()
for image in images:
    paths.append('images_to_process/' + image)

database = ['faces_database/' + file for file in search_dir('faces_database')]
predictions = detect_image(paths, op_or_not = False, path2dir = None)

for i in range(len(images)):
    prediction = predictions[i]
    pattern = re.compile(r'(?P<name>.+?)\.(?P<format>[a-zA-Z]+)$')
    re_result = pattern.fullmatch(images[i])
    image_cv = cv2.imread(paths[i])
    if not prediction:
        cv2.imwrite('results/'+re_result.group('name')+'_processed.'+\
            re_result.group('format'),image_cv)
        continue
    position = prediction['box']
    (x,y,foo) = image_cv.shape
    pt1 = (int(position[1]*y), int(position[0]*x))
    pt2 = (int(position[3]*y), int(position[2]*x))
    cv2.rectangle(image_cv, pt1, pt2, (0, 255, 0), 1)
    name,score_face = get_label(image_cv,[pt1[0],pt1[1],pt2[0],pt2[1]],database)
    score = prediction['score'] * score_face / 100
    font = cv2.FONT_HERSHEY_SIMPLEX
    new_image = cv2.putText(image_cv,f'{name} {round(score,3)}' if score else f'{name} None',\
     pt1, font, 0.5, (0, 255, 255), 1)
    cv2.imwrite('results/'+re_result.group('name')+'_processed.'+\
        re_result.group('format'),new_image)
shutil.rmtree('tmp')