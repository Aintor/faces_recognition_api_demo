from aip import AipFace
import base64


def face_check(path_verifyee,path_verifyer):
    with open('keys.json','r') as file:
        f = file.read()
    lines = f.split('\n')
    APP_ID = lines[0]
    API_KEY = lines[1]
    SECRET_KEY = lines[2]
    print(APP_ID, API_KEY, SECRET_KEY)

    client = AipFace(APP_ID,API_KEY,SECRET_KEY)
    
    

    f1 = open(path_verifyee,'rb')
    f2 = open(path_verifyer,'rb')
   
    img1 = base64.b64encode(f1.read())
    img2 = base64.b64encode(f2.read())
    
    image_1 = str(img1,'utf-8')
    image_2 = str(img2,'utf-8')
    
    images = [{'image':image_1,'image_type':'BASE64'},
              {'image':image_2,'image_type':'BASE64'}]
    
    ptr = client.match(images)
    if ptr['result'] and ptr['result']['score']>60:
        name = path_verifyer.split('\\')[-1].split('.')[0]
        score = ptr['result']['score']
    else:
        score = 0
        name = 'unknown'
    return name,score