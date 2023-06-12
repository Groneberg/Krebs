from ultralytics import YOLO
import cv2
from os import path
from matplotlib import pyplot as plot

model = YOLO(path.join('weights', 'best_11062023.pt'))

# from ndarray
im2 = cv2.imread(path.join("image", "roter-amerik-sumpfkrebs2.jpg"))
results = model.predict(source=im2, save=True, save_txt=True)  # save predictions as labels

for result in results:
    for box in result.boxes:
        xyxy = box.xyxy.flatten()
        x1, y1, x2, y2 = xyxy[0].item(), xyxy[1].item(), xyxy[2].item(), xyxy[3].item()
        cv2.rectangle(im2, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 2)

plot.imshow(im2)
plot.show()

