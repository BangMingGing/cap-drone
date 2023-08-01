import requests
import cv2 as cv
import numpy as np
import time

from face_recog_system.face_recog import Face_Recognizer

class Face_Inferer():
    
    def __init__():
        
        self.face_recognizer = Face_Recognizer()


    async def face_recognition_video(self, pre_inference_model, receiver_info):
        # CAM open
        cap = cv.VideoCapture(0)
        t = time.time() % 100
        
        # Generate video_writer
        output_file = f'{t}_face_video.mp4'
        fourcc = cv.VideoWriter_fourcc(*'MP4V')
        fps = cap.get(cv.CAP_PROP_FPS)
        frame_size = (224, 224)
        video_writer = cv.VideoWriter(output_file, fourcc, fps, frame_size)
        
        total_output_file = f'{t}_total_face_video.mp4'
        total_frame_size = (int(cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)))
        total_video_writer = cv.VideoWriter(total_output_file, fourcc, fps, total_frame_size)

        # find face in CAM for 5 seconds
        end_time = time.time() + 6
        
        while True:
            if time.time() > end_time:
                break
            if not cap.isOpened():
                print("Failed to open the camera")
                break
            
            ret, frame = cap.read()
            
            if ret:
                img, is_face, rectang = self.face_recognizer.face_detector(frame)
                total_video_writer.write(frame)
                video_writer.write(img)
                
        video_writer.release()
        total_video_writer.release()
        
        video_file = open(output_file, 'rb')
        payload = {'drone_name': self.drone_name, 'receiver_info': receiver_info}
        files = {'video_file': video_file}

        response = requests.post(self.url, files=files ,data=payload)
        if response.status_code != 200:
            print('face_video request failed')

        
        return

    