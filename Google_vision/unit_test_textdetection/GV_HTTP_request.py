import base64
import json
import requests

import cv2
def detect_texts(extension, image_matrix, key, session=None):
    '''
    Returns the response(descriptions of texts) of a request(image)
    
    - extension : 확장자명 (ex. '.png', '.jpg',...)
    - image_matrix : ndarray of an image
    - session : requests session 
    - key : API Key of Google Vision
    '''
    _img = cv2.imencode(extension, image_matrix)[1].tostring() #byte string
    content = str(base64.b64encode(_img))
    content = content[2:-1]
    _url = 'https://vision.googleapis.com/v1/images:annotate?key='+key
    _item = {
      "requests":[
        {
          "image":{
            "content":content
          },
          "features":[
            {
              "type":"TEXT_DETECTION",
              "maxResults":1
            }
          ]
        }
      ]
    }
    if session is None:
        ret = requests.post(_url, json.dumps(_item))
    else:
        ret = session.post(_url, json.dumps(_item))
        
    ret = json.loads(ret.content)
    return ret



if __name__ == "__main__":
    img = cv2.imread('./imgt.png',0)
    ret = GV_get_description('.png',img)

    #print json
    print(ret)
