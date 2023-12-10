import numpy as np
import onnxruntime

class onnx_client_model:
    def __init__(self, provider):           
        self.dsize = (224, 224)
        
        self.model = onnxruntime.InferenceSession(
            "face_recog_module/resnet_pi.onnx",
            providers=['{}ExecutionProvider'.format(provider)])


    def preprocess(self, x):
        x = x.transpose((2, 0, 1))
        x = np.expand_dims(x, 0)
        x = x.astype(np.float32)
        return x

    # 추론 load_block_name 함수가 선행되고 진행해야함
    async def inference_tensor(self, out):
        return await self.model.run(None, {'input': out[0]})[0]

    async def inference_image(self, face_img):
        return await self.inference_tensor([self.preprocess(face_img)])
