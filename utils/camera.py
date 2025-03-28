from ultralytics import YOLO
import cv2
import torch
from utils.common import random_string
import time
from rpi_api.models import Logs

model = YOLO("yolo11m.pt")

def capture_and_detect_humans():
    unique_id = random_string()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        log = Logs(severity='ERROR', message='Camera not found')
        log.save()
        return {
            'status': 'error',
            'message': 'Camera not found',
            'data': ''
        }

    ret, image = cap.read()
    cap.release()

    if not ret:
        log = Logs(severity='ERROR', message='Failed to capture image')
        log.save()
        return {
            'status': 'error',
            'message': 'Failed to capture image',
            'data': ''
        }

    start_time = time.time()

    human_detections = []
    results = model(image)
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if cls_id == 0:
                human_detections.append({
                    "confidence": conf,
                    "box": [x1, y1, x2, y2]
                })
                # Draw the bounding box and confidence on the image
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, f'{conf:.2f}', (x1 + 5, y1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    end_time = time.time()
    processing_time = end_time - start_time

    image_name = f"static/captured_images/{unique_id}.jpg"
    cv2.imwrite(image_name, image)
    log = Logs(severity='SUCCESS', message=f'Image captured and processed in {processing_time:.2f} seconds')
    log.save()
    return {
        'status': 'success',
        'message': 'Image processed',
        'data': {
            'image_name': image_name,
            'human_detections': human_detections,
            'human_count': len(human_detections),
            'processing_time': processing_time,
            'unique_id': unique_id
        }
    }