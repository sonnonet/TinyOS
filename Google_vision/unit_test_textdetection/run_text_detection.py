'''
    2가지 방식 중에 하나를 선택하여 숫자열이 포함된 부분을 얻어오는 기능을 수행한다
        - 템플릿 매칭 방식 
        - 등고선 추출 방식

    문제점 : 
            [템플릿 매칭 방식]
            템플릿 매칭을 사용하는 경우, 이미지에서 음영이 균일하지 않으면, 특정 숫자는 
            인식이 되지 않는다

            '적응 임계처리' 방식(adaptiveThreshold)을 사용해본 결과 이미지 추출은 사용자가
            알아볼 수 있으나, 구글 비전에 쿼리하면 빈 response를 받는다
            
            [등고선 추출 방식]
            등고선 추출 방식을 사용하는 경우, 이미지가 정방향으로 찍히지 않고 회전되거나 기울어지면,
            숫자열이 포함된 등고선을 필터링하는 부분을 재조정해야 할 필요가 있다


'''


import numpy as np
import requests
import cv2

import Preprocessing
import GV_HTTP_request
import constants

def run(sess, name_scene_image, API_KEY, extraction_method='constants.BY_CONTOUR'):
    '''
    Receives an extracted texts from scene image using Google Vision API 

    - name_scene_image : name of the scene image
    - API_KEY = Google Vision API Key

    '''
    #name_scene_image = './test.png'
    extension = '.png'
    name_template_image = './template_image.png'

    scene_image = cv2.imread(name_scene_image,0)
    template_image = cv2.imread(name_template_image, 0)

    #grayscale the image
    scene_image = Preprocessing.to_grayscale(scene_image, extraction_method)
    template_image = Preprocessing.to_grayscale(template_image, extraction_method)

    #extract the template(target numbers) image from the scene image
    #extracted_image = Preprocessing.extract_by_template(template_image, scene_image)
    extracted_image = Preprocessing.extract_by_contours(scene_image)
    cv2.imwrite('./' + name_scene_image, extracted_image)

    #send the extracted image, and receive text
    ret = GV_HTTP_request.detect_texts(extension, extracted_image, API_KEY, sess)
    
    #extracted text
    #extracted_text = ret['responses'][0]['fullTextAnnotation']['text']
    extracted_text = ret['responses'][0]['textAnnotations'][0]['description']
    
    ret = ''
    for ch in extracted_text:
        try:
            ret += str(int(ch))
        except ValueError as e:
            pass

    return int(ret)


if __name__ == '__main__':
    names_image = ['./test1.png']
    values = []
    API_KEY = 'AIzaSyDdPiRW0lXGtY_s188gr6tIZ8WY_ZqAglM'

    with requests.Session() as sess:
        for name in names_image:
            values.append(run(sess, name, API_KEY))
    
    print(values)

    
    
    
    

    
    
    
    

