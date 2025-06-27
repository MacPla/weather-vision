import os
import time
import cv2
import torch
from torchvision import transforms
from PIL import Image
from datetime import datetime

labels = ["cloudy", "foggy", "rainy", "snowy", "sunny"]

model = torch.hub.load('pytorch/vision:v0.10.0', 'mobilenet_v2', pretrained=True)
model.eval()

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

rtsp_url = os.getenv("RTSP_URL", "")
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Failed to open RTSP stream")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("RTSP frame read failed")
        continue

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img)
    input_tensor = preprocess(img_pil).unsqueeze(0)

    with torch.no_grad():
        output = model(input_tensor)
        pred = output.argmax(1).item()

    label = labels[pred % len(labels)]
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S - %d/%m/%Y")

    print(f"[{timestamp}] Detected weather: {label}")

    os.makedirs("/shared/history", exist_ok=True)

    # Save current status and image
    with open("/shared/latest.txt", "w") as f:
        f.write(label)
    with open("/shared/timestamp.txt", "w") as f:
        f.write(timestamp)

    # Save hourly snapshot
    hour_stamp = now.strftime("%Y-%m-%d_%H")
    cv2.imwrite(f"/shared/history/{hour_stamp}.jpg", frame)
    with open(f"/shared/history/{hour_stamp}.txt", "w") as f:
        f.write(label)

    # Save current image too
    cv2.imwrite("/shared/last.jpg", frame)

    time.sleep(10)
