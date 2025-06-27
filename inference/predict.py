
import os
import time
import cv2
import torch
from torchvision import transforms
from PIL import Image

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

    print(f"Detected weather: {label}")

    with open("/shared/latest.txt", "w") as f:
        f.write(label)

    time.sleep(10)
