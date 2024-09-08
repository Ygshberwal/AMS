import numpy as np
import cv2
import torch
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords, xyxy2xywh
from utils.torch_utils import select_device

def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border

    return img, ratio, (dw, dh)

class Head_Detector:
    def __init__(self, imgsz=640, weights="yolov5s.pt", device="0", half=False):
        self.device = select_device(device)
        self.half = half
        self.model = attempt_load(weights, map_location=self.device)  # load FP32 model
        self.stride = int(self.model.stride.max())  # model stride
        self.imgsz = check_img_size(imgsz, s=self.stride)  # check img_size
        if half:
            self.model.half()
            
        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once  
            
    def detect(self, image, conf_thres=0.4, iou_thres=0.5, class_filter=1):
        img, _, _ = letterbox(image, new_shape=self.imgsz, stride=self.stride)
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x640x640
        img = np.ascontiguousarray(img)
        
        img = torch.from_numpy(img).to(self.device)  
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0

        if len(img.shape) == 3:
            img = img[None]
        
        pred = self.model(img)[0]
        
        # Apply NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes=class_filter)[0]
        
        # Scale those coords back to original size
        pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], image.shape[:2]).round()
        
        # Return only the coords, as filtered on the class level
        pred = pred[:, :4].tolist()
        # pred = [int(value) for sublist in pred for value in sublist]

        return pred
    
    def draw_pred(self, image, preds):
        for x1, y1, x2, y2 in preds:
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), 4)
        return image

if __name__ == "__main__":
    detector = Head_Detector(weights="best.pt")
    cap = cv2.VideoCapture(0)
    while True:
        _, frame = cap.read()
        pred = detector.detect(frame)
        drawn_image = detector.draw_pred(frame, pred)
        drawn_image = cv2.resize(drawn_image, (1280, 720))
        
        cv2.imshow("a", drawn_image)
        
        if cv2.waitKey(1) == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()
    