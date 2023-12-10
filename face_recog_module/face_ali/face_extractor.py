import dlib
import cv2 as cv
import numpy as np
from imutils import face_utils
#from IPython.display import display
#import PIL.Image as PILImage
from typing import *

from time import time

class Face_Extractor():
    
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector() 
        self.predictor = dlib.shape_predictor("face_recog_module/face_ali/shape_predictor_5_face_landmarks.dat")


    def mksquare(self, img: np.ndarray,
                pad_color: Tuple[float, float, float] = (114, 114, 114),
                size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        h, w, *_ = img.shape
        vpad, hpad = [max(0, w - h) // 2] * 2, [max(0, h - w) // 2] * 2
        img = cv.copyMakeBorder(img, *vpad, *hpad, cv.BORDER_CONSTANT, value=pad_color)
        img = cv.resize(img, size) if size is not None else img
        return img
    
    
    def T_rotate(self, rad):
        return np.array([
            [np.cos(rad), np.sin(rad)],
            [-np.sin(rad), np.cos(rad)],
        ])


    def face_extract(self, img):

        faces = self.detector(img)
        
        if len(faces):
            for face in faces:
                landmarks = self.predictor(img, face)
                shape = face_utils.shape_to_np(landmarks)
                v_i2i = np.array(shape[0]) - np.array(shape[2])
                v_i2i = v_i2i / np.linalg.norm(v_i2i)
                
                rotation_direction = np.sign(np.cross([*v_i2i, 0], [1, 0, 0]))[-1]
                theta = np.arccos(np.dot(v_i2i, [1, 0])) * rotation_direction

                x_lt = shape[2][0]
                y_lt = landmarks.rect.top()
                x_rb = shape[0][0]
                y_rb = landmarks.rect.bottom()

                p_lt = (landmarks.rect.left(), y_lt)
                p_rb = (landmarks.rect.right(), y_rb)
                rectang = [p_lt, p_rb]
                
                pt_lt = np.array([x_lt, y_lt])
                pt_lb = np.array([x_lt, y_rb])
                pt_rt = np.array([x_rb, y_lt])
                pt_rb = np.array([x_rb, y_rb])
                pt_rose = shape[4]

                x_candidates = []
                y_candidates = []
                for pt in [pt_lt, pt_lb, pt_rt, pt_rb]:
                    x, y = self.T_rotate(theta) @ (pt - pt_rose)
                    x_candidates.append(x)
                    y_candidates.append(y)

                new_pt_lt = np.array([min(x_candidates), min(y_candidates)], dtype=int) + pt_rose
                new_pt_rb = np.array([max(x_candidates), max(y_candidates)], dtype=int) + pt_rose

                transform = cv.getRotationMatrix2D((pt_rose).astype(float), -theta * 180 / np.pi, 1.)
                img_partial = cv.warpAffine(img, transform, dsize=img.shape[:2][::-1])
                img_partial = img_partial[new_pt_lt[1]:new_pt_rb[1], new_pt_lt[0]:new_pt_rb[0], :]
                img_partial = self.mksquare(img_partial, (0,0,0), (224, 224))
                
            return img_partial, len(faces), rectang
        else:
            return None, False, None
                #img_partial = cv.resize(img_partial, dsize=(112, 112))
