import cv2
import numpy as np
from openvino.runtime import Core
from openvino_detector_2022_3.model_api.performance_metrics import PerformanceMetrics
from time import perf_counter
core = Core() # Initialize OpenVINO API
detection_model_xml = "openvino_detector_2022_3/model_2022_3/face-detection-retail-0005.xml"
detection_model = core.read_model(model=detection_model_xml)
device = "CPU" # if you have NCS2 use "MYRIAD"
compiled_model = core.compile_model(model=detection_model, device_name=device)
input_layer = compiled_model.input(0) # Get input layer
output_layer = compiled_model.output(0) # get outputs layer
source = 0 #'videos/wonder_woman.mp4' # Load the video
cap = cv2.VideoCapture(source)
N, C, H, W = input_layer.shape
metrics = PerformanceMetrics()
while True: # Main loop
    start_time = perf_counter()
    ret, frame = cap.read()
    resized_image = cv2.resize(src=frame, dsize=(W, H))
    input_data = np.expand_dims(np.transpose(resized_image, (2, 0, 1)), 0).astype(np.float32)
    request = compiled_model.create_infer_request()
    request. infer(inputs={input_layer.any_name: input_data}) # Infer
    result = request.get_output_tensor(output_layer.index) .data
    bboxes = [] # Post-process the outputs
    frame_height, frame_width = frame.shape[:2]
    
    for detection in result[0][0]:
        label = int (detection[1])
        conf = float (detection[2])
        if conf > 0.76:
            xmin = int(detection[3] * frame_width)
            ymin = int(detection[4] * frame_height)
            xmax = int(detection[5] * frame_width)
            ymax = int(detection[6] * frame_height)
            bboxes.append([xmin, ymin, xmax, ymax])
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 255), 3)
            cv2.putText (frame, "face", (xmin, ymin-5) , cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2 )
    metrics.update(start_time, frame)
    cv2.imshow('person detection demo', frame)
    key = cv2.waitKey(1)
    if key in {ord('q'), ord('Q'), 27}:
        cap.release()
        cv2.destroyAllWindows ()
        break