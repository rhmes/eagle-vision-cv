# engine/yolo_handler.py
import torch

class yoloHandler:
    def __init__(self):
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)
        # Set confidence threshold and class (person class)
        self.model.conf = 0.4
        self.model.classes = [0]  # Only detect person class
        
        ### Automatically choose device: GPU if available, otherwise CPU
        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        ### Move the model to the selected device (GPU/CPU)
        # self.model.to(self.device).eval()
    
        ### If using GPU and TensorRT is available, convert the model to TensorRT
        # if self.device.type == 'cuda' and TRT_AVAILABLE:
        #     print("Converting YOLOv5 model to TensorRT...")
        #     # Use a dummy input tensor to define the input shape for TensorRT
        #     example_input = torch.randn((1, 3, 640, 640)).to(self.device)  # YOLOv5 expects (1, 3, 640, 640) shape
        #     self.model = torch_tensorrt.compile(
        #         self.model,
        #         inputs=[torch_tensorrt.Input(example_input.shape)],
        #         enabled_precisions={torch.float},  # Can use torch.half or torch.int8 as well
        #         device={'device_type': torch_tensorrt.DeviceType.GPU}
        #     )
        #     print("TensorRT model ready.")
        # else:
        #     print(f"Using model on {self.device}")
        
    def process_frame(self, frame):
        return self.model(frame)
