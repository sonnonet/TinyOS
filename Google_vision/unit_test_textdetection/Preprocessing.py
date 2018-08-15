import cv2
import numpy as np

import constants

def to_1_channel(image):
    '''
    Returns image in 1 channel with shape(y, x)
    
    - image : 3 channel image matrix with shape (y, x, 3)
    '''

    _ylen = image.shape[0]
    _xlen = image.shape[1]

    image = image.reshape(-1,3)
    image = np.array([int(sum(values) / 3) for values in image]).reshape(_ylen, _xlen)

    return image

def to_grayscale(image, extraction_method):#numpy matrix of image
    '''
    Returns grayscaled image in 2-dim. ndarray

    - image : image (1 or 3 channel both ok) in numpy matrix
    '''
    extraction_method = eval(extraction_method)
    if extraction_method == constants.BY_CONTOUR:
        return image

    if len(image.shape) == 3:
        image = to_1_channel(image)

    thresh = 127
    def to_0(x):
        if x < thresh:
            return 0
        return 255

    try:
        _ylen = image.shape[0]
        _xlen = image.shape[1]
    except AttributeError as e:
        raise e

    image_in_bw = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)[1]
    #image_in_bw = cv2.adaptiveThreshold(image,255, cv2.ADAPTIVE_THRESH_MEAN_C, \
    #                           cv2.THRESH_BINARY_INV, 15,2)

    image_in_bw = np.array(image_in_bw).ravel()
    image_in_bw = np.array(list(map(to_0, image_in_bw)), dtype=np.uint8).reshape(_ylen, _xlen)

    return image_in_bw


def extract_by_contours(image):
    '''
    Returns the extracted image in 2d numpy array

    - image : 2d array of a scene image

    referred to img_cog.py by LKM
    '''
    image = cv2.GaussianBlur(image, (7,7), 0)
    image = cv2.Canny(image, 30, 100)

    cnts, contours, hierarchy =  cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        #print('%s %s %s %s' % (x, y, w, h))
        rect_area = w * h
        aspect_ratio = float(w) / h

        if (aspect_ratio >= 2.4) and (aspect_ratio <= 2.8) and \
            (rect_area >= 40000) and (rect_area <= 285000):

            resized_image = image[y + 60:h + y - 80, x:x + w]
            return resized_image

    return None

def extract_by_template(template_image, scene_image, method='cv2.TM_CCOEFF'):
    '''
    Returns the extracted template image in 2d numpy array 

    - template_image : 2d array of a template image
    - scene_image : 2d array of a scene image
    - method : the extraction method

    '''

    method = eval(method)
    w = template_image.shape[1]
    h = template_image.shape[0]

    res = cv2.matchTemplate(scene_image, template_image, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    ret = scene_image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

    return ret
    

if __name__ == "__main__":
    template_img = cv2.imread('/home/jin/imgt.png',0)
    scene_img = cv2.imread('/home/jin/imgtest.JPG',0)

    ext_img = extract_by_template(template_img, scene_img)
    cv2.imwrite('ext_img.png',ext_img)


