import cv2 as cv

from face_recog_module.onnx_inference_client import onnx_client_model
from face_recog_module.face_ali.face_extractor import Face_Extractor


class Client_Inferer():

    def __init__(self):
        self.provider = 'CPU'  # CPU or CUDA
        self.model = onnx_client_model(self.provider)
        self.face_extractor = Face_Extractor()


    def faceDetectAndCrop(self, img):
        return self.face_extractor.face_extract(img)

    
    def inference_video(self, video_route, target_route):
        cap = cv.VideoCapture(video_route)

        avg_mse = []

        while (cap.isOpened()):
            ret, img = cap.read()

            if ret:
                img = cv.resize(img, dsize = (360, 360))
                face_img, is_face, rectang = self.faceDetectAndCrop(img)
                
                if is_face:
                    tensor = self.model.inference_image(face_img)
                    result = self.request2server(tensor)
                    mse = self.get_mse(result, target_route)

                    avg_mse.append(mse)
            
            else:
                break

        ret_val = sum(avg_mse) / len(avg_mse)

        return ret_val


    async def inference_img(self, img):
        img = cv.resize(img, dsize = (360, 360))
        face_img, is_face, rectang = self.faceDetectAndCrop(img)
        print('is_face : ', is_face)
        if is_face:
            tensor = await self.model.inference_image(face_img)
            return is_face, tensor

        return is_face, None

    
if __name__ == '__main__':
    
    video_route = './data/total_face_video.mp4'
    target_route = './face_targets/sunjae_face'
    img_route = './data/face_img.jpg'

    client_inferer = Client_Inferer()

    result = client_inferer.inference_img(img_route, target_route)
    print(result)
    
