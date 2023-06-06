from ultralytics import YOLO
import cv2
from os import path

model = YOLO(path.join('model', 'best.pt'))

# from ndarray
im2 = cv2.imread("test_fish.jpg")
results = model.predict(source=im2, save=True, save_txt=True)  # save predictions as labels
