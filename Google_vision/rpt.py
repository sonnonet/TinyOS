
'''
	target image를 scene image에서 찾는 기능을 수행한다 (RPT)
	target image의 중심점이 scene image에서 어느 좌표에 있는지 찾는 기능 수행
	여기서 scene image는 target image를 포함한 회전/이동된 이미지이다

	작업 상황 : 진행중
	문제점 : 
		- 시간 소요가 크다
		- 올바른 결과치 출력 x
	
'''

import cv2
import numpy as np
import sys
from PIL import Image
import scipy.integrate as integrate
import multiprocessing as mp



class RPT():
    def __init__(self, template, scene):
        print('INITIALIZATION COMPLETE')
        self.template = template
        self.scene = scene

        self.w = (template.shape[1], scene.shape[1]) # 0: template's, 1:scene's
        self.h = (template.shape[0], scene.shape[0])


        print('template shape : '+str(self.template.shape))
        print(str(self.h[0])+ ' ' +str(self.w[0]))
        print('scene shape : '+str(self.scene.shape))
        print(str(self.h[1])+ ' ' +str(self.w[1]))
        
    def _pixel_at(self, theta, x, y, r, which):
        #print(theta)
        w = self.w[which]
        h = self.h[which]
            
        #print('x y r which')
        #print(str(x)+' '+str(y)+' '+str(r)+' '+str(which))
            
        #print('w h')
        #print(str(w)+' '+str(h))
       
            
        x = int(x + h/2 + r*np.sin(theta))
        y = int(y + w/2 + r*np.cos(theta))
            
            
        #print('x y')
        #print(str(x)+' '+str(y))
            

        if x >= h:
            x = h-1
        if y >= w:
            y = w-1
            
        if which == 1:
            return self.scene[x][y]
        else:
            return self.template[x][y]


    def sigma(self, _from, _to, x, y, r, which):
        s = 0
        for i in range(0,361):
            s += self._pixel_at(i,x,y,r, which)
        return s
        
    def S_xy_r(self, x,y,r):
        SCENE = 1
        #integrated_val = integrate.quad(self._pixel_at, 0,360, args=(x, y, r, SCENE))
        integrated_val = self.sigma(0, 360, x, y, r, SCENE)
        S_xy_r = integrated_val / (2*np.pi*r)
        
        return S_xy_r
        
    def T_r(self, r):
        TEMPLATE = 0
        #integrated_val = integrate.quad(self._pixel_at, 0, 360, args=(0,0,r,TEMPLATE))
        integrated_val = self.sigma(0, 360, 0, 0, r, TEMPLATE)
        T_r = integrated_val / (2*np.pi*r)
        
        return T_r
        
    def NCC(self, pix_v1, pix_v2): # T, S : array
        #print(pix_v1)
        #print(pix_v2)
        pix_vs = np.array([pix_v1, pix_v2])
            
        _cov = np.cov(pix_v1, pix_v2)
        _cov = _cov[0][1]
        _std_T = np.std(pix_v1)
        _std_S = np.std(pix_v2)
            
        ret = _cov / (_std_T * _std_S)
        #print(_cov)
        #print(_std_T * _std_S)
        #print(_std_T)
        #print(_std_S)

          
        return ret
        


    def similarity(self, x,y,r): #x,y : point, r : 1 ~ r\n",
        '''
        returns the similarity of point A(x,y) and point B(x,y)
        - x : x coordinate
        - y : y coordinate
        - r : range of radius from 1
        '''
        S = []; T = []
        for _r in range(1,r+1): #sum of values of surrounding points when the radius is _r
            S.append(self.S_xy_r(x, y, _r))
            T.append(self.T_r(_r))

        #normalized correlation value\n",
        _ncc = self.NCC(T,S)

        print(_ncc)
        return _ncc #scala
    
    def multi_get_max(self, radius, xfrom, xto, yfrom, yto):
        print('MULTI PROCESSING')
        _max_x = 0
        _max_y = 0
        _max_v = 0
        for _x in range(xfrom, xto+1):
            for _y in range(yfrom, yto+1):
                _v = self.similarity(_x, _y, radius)
                if _v > _max_v:
                    _max_v = _v
                    _max_x = _x
                    _max_y = _y

        return (_max_x, _max_y, _max_v)


    def get_max_center(self, radius):
        xlen_scene = self.h[1]
        ylen_scene = self.w[1]
        print(str(xlen_scene)+' '+str(ylen_scene))
        _max = 0
        _max_x = 0
        _max_y = 0

        N=4
        x_div = int(xlen_scene / N)
        y_div = int(ylen_scene / N)
        async_rsts = []
        pool = mp.Pool(N)
        try:
            for i in range(N):
                xfrom = i * x_div
                xto = xfrom + x_div
                yfrom = i * y_div
                yto = yfrom + y_div

                async_rsts.append(pool.apply_async(self.multi_get_max,\
                                  args=(radius, xfrom, xto, yfrom, yto)))
        except Exception as e:
            raise e
        finally:
            pool.close()
            pool.join()

        mxvs = []
        for rst in async_rsts:
            mxvs.append(rst.get())

        mx = 0
        for tup_val in mxvs:
            v = tup_val[2]
            if v > _max:
                _max = v
                _max_x = tup_val[0]
                _max_y = tup_val[1]

        

        return (_max_x, _max_y)



if __name__ == "__main__":


    scene = np.array(cv2.imread('./imgtest.JPG',0))
    print(np.array(scene).shape)
    sys.exit()
    template = np.array(cv2.imread('./imgt.png',0))

    radius = 3
    rpt_obj = RPT(template, scene)
    max_x, max_y = rpt_obj.get_max_center(radius)


    print(max_x)
    print(max_y)
