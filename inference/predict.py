
import os
import time
import json
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
    start_time = time.time()

    ret, frame = cap.read()
    if not ret:
        print("RTSP frame read failed")
        continue

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    input_tensor = preprocess(img_pil).unsqueeze(0)

    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.nn.functional.softmax(output[0], dim=0)
        pred_idx = torch.argmax(probs).item()

    label = labels[pred_idx % len(labels)]
    confidence = probs[pred_idx].item()
    top3 = torch.topk(probs, 3)

    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S - %d/%m/%Y")
    hour_stamp = now.strftime("%Y-%m-%d_%H")

    os.makedirs("/shared/history", exist_ok=True)

    with open("/shared/latest.txt", "w") as f:
        f.write(label)
    with open("/shared/timestamp.txt", "w") as f:
        f.write(timestamp)
    with open("/shared/confidence.txt", "w") as f:
        f.write(f"{confidence:.2f}")
    with open("/shared/top3.json", "w") as f:
        json.dump([
            {"label": labels[i % len(labels)], "score": float(top3.values[i])}
            for i in range(3)
        ], f)
    with open("/shared/latency.txt", "w") as f:
        latency = time.time() - start_time
        f.write(f"{latency:.2f}")

    cv2.imwrite("/shared/last.jpg", frame)
    cv2.imwrite(f"/shared/history/{hour_stamp}.jpg", frame)
    with open(f"/shared/history/{hour_stamp}.txt", "w") as f:
        f.write(label)

    print(f"[{timestamp}] {label} ({confidence*100:.1f}%) - latency: {latency:.2f}s")
    time.sleep(10)
