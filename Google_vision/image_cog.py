# -*- coding:utf-8 -*-

import cv2
from google.cloud import vision
import io
import datetime
import time
import requests
import json



'''
1. 이미지 불러오기 
2. 이미지 가공
    - 색 보정
    - 잡티 제거
    - 윤곽선 뜨기
    
3. 이미지에서 원하는 부분만 추출
4. 추출된 이미지 숫자 인식
5. OpenTsdb 저장
'''


class Image_cog:

    def __init__(self, Start_, End_):
        # Start_ means First image's day , End_ means last image's day

        self.image = []
        self.image_format = []
        self.image_final = []
        self.image_dict = []
        self.dict_list=[]

        self.len = None
        self.Start_ = Start_
        self.End_ = End_

    def Open_image(self):
        # 1. 이미지 불러오기
        first_name = 'IMG_00'

        for i in range(self.Start_, self.End_+1):
            path = first_name + str(i) + '.JPG'
            img = cv2.imread(path, cv2.IMREAD_COLOR)  # numpy 값으로 변경
            self.image.append(img) # list로 저장
        self.len = len(self.image)


    def Format_image(self, _list, _list_2):
        # 2. 이미지 가공
        # 전처리 할 이미지의 list와 전처리를 한 후 변경된 이미지를 저장할 list입력

        for i in range(len(_list)):
            img = _list[i].copy()
            img_ver2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 색 제거
            img_ver3 = cv2.GaussianBlur(img_ver2, (7, 7), 0)  # 잡티 제거
            img_ver4 = cv2.Canny(img_ver3, 30, 100)  # 윤곽선
            # cv2.imwrite('format_image_'+str(i)+'.jpg', img_ver4) #이미지 확인

            _list_2.append(img_ver4)


    def Contours_image(self):
        # 3. 이미지에서 원하는 부분만 추출

        for j in range(self.len):
            # 전처리한 사진의 contours를 저장
            cnts, contours, hierarchy = cv2.findContours(self.image_format[j], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for i in range(len(contours)):
                # 에너지가 같은 점을 잇는 사각형을 보여주고, 그 중 우리가 원하는 검량계부분만 보여준다.

                cnt = contours[i]
                x, y, w, h = cv2.boundingRect(cnt)
                rect_area = w * h  # 넓이
                aspect_ratio = float(w) / h  # 비율 = width/height

                # 검량계 부분이라 생각하는 곳의 비율 범위와 넓이 범위 조건식
                if (aspect_ratio >= 2.4) and (aspect_ratio <= 2.8) and (rect_area >= 40000) and (rect_area <= 285000):

                    #사각형의 위치 확인
                    #check_image = cv2.rectangle(self.image[j], (x, y), (x + w, y + h), (0, 255, 0), 1)
                    #cv2.imwrite('contour_check' + str(j) + '.jpg', check_image)

                    resize_image = self.image[j].copy()[y + 60:h + y - 80, x:x + w]  # 모양에 맞게 자른다.
                    self.image_dict.append({ 'x_position' : x, 'y_position' : y}) # 좌표 저장
                    self.image_final.append(resize_image) #저장
                    cv2.imwrite('contour_' + str(j+1)  + '.jpg', resize_image) # 사진 저장
                    break # 1개만 추출하기


    def Cog_number(self):
        # 4. 추출된 이미지 숫자 인식
        client = vision.ImageAnnotatorClient()
        for i in range(self.len):

            path = 'contour_' + str(i+1)  + '.jpg' # 저장된 파일 불러오기
            with io.open(path, 'rb') as image_file:
                content = image_file.read()

            image = vision.types.Image(content=content)
            response = client.text_detection(image=image)
            text =response.text_annotations[0].description.replace(" ","").replace('\n','').replace('O','0') # 인식된 숫자 추출

            print(str(i+1) + u'번째 사진의 숫자 : ' + text)
            self.image_dict[i]['Watt']=int(text)
            

    def Put_tsdb(self):
        #5. OpenTsdb 저장

        '''
        putdict = {
        'metric' : Watthour_00
        'timestamp' : 현재 시간(저장시간으로 바꿔야함)
        'value' : 값
        'tags' : {
                    Feature: 검량값, x좌표, y좌표
                 }
        }
        '''

        headers = {'content-type': 'application/json'}
        metric = 'Watthour_00'
        g_w_url = "http://125.140.110.217:44242/api/put?details"

        for i in range(self.len):

            for key,value in (self.image_dict[i].items()):

                putdict = {}
                tags={}
                putdict['metric'] = metric
                # 사진 저장 시간으로 수정해야 합니다!
                putdict['timestamp'] = time.mktime(datetime.datetime.now().timetuple())
                putdict['value'] = value
                tags['Feature'] = key
                putdict['tags'] = tags
                self.dict_list.append(putdict)


        decode_data = json.dumps(self.dict_list, indent=2)

        try:
            # put 하는걸 요청한다.
            _r = requests.post(g_w_url, decode_data, headers=headers)
            while _r.status_code > 204:
                print (" Write error!")
                res = json.loads(_r.content)
                #print (_r.content)
                print(res)
                print(res['errors'])
                
            print('tsdb 저장 완료')

        except requests.exceptions.ReadTimeout as e:
            print ("\n [Exception]", e)

        except requests.exceptions.ConnectionError as e:
            print ("\n [Exception]", e)
            time.sleep(10)



    def run(self):

        self.Open_image() # image 불러오기
        self.Format_image(self.image, self.image_format) # image 추출을 위한 전처리
        self.Contours_image() # image 추출
        self.Cog_number() # 추출된 이미지에서 숫자 인식

        # Opentsdb에 저장, 저장을 원치 않으면 이 부분만 주석처리 하시면 됩니다.
        # self.Put_tsdb()


if __name__ == '__main__':

    #[IMG_00XX] 에서 XX에 해당하는 번호를 입력한다.
    app = Image_cog(86,89)
    app.run()
