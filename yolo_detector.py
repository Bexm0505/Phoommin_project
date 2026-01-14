from ultralytics import YOLO
from collections import deque
import cv2
import numpy as np

# โค้ดสำหรับ Internship Exam 
# Phoommin 

def main():
    # โหลดโมเดลตัวเล็กสุด เร็วดี
    print("Loading model...")
    model = YOLO("yolov8n.pt") 

    # เปิดไฟล์ video
    cap = cv2.VideoCapture("CatZoomies.mp4")
    
    # กันเหนียว ถ้าเปิดไม่ได้
    if not cap.isOpened():
        print("Error: หาไฟล์วิดีโอไม่เจอ") 
        return

    # จุดเก็บตำแหน่งหางแมว (30 เฟรมย้อนหลัง)
    points = deque(maxlen=30)
    
    # print("Start loop")

    while True:
        ret, frame = cap.read()
        
        # ถ้าจบวิดีโอ หรือ error
        if not ret:
            break

        # detect แมว = class 15
        results = model(frame, classes=[15], verbose=False) 
        
        # ตัวแปรเก็บตำแหน่งแมวตัวล่าสุด
        center_cat = None
        max_conf = 0
        
        # วนลูปหา object
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # ลองปริ้นค่าดู
                # print(box.xyxy)
                
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf.item()
                
                # หาจุดกึ่งกลาง
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                # เอาตัวที่มั่นใจที่สุด
                if conf > max_conf:
                    max_conf = conf
                    center_cat = (cx, cy)

                # วาดกรอบสีน้ำเงิน (BGR: 255-0-0)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                
                # ใส่ text
                cv2.putText(frame, f"Cat {conf:.2f}", (int(x1), int(y1)-10), 0, 0.5, (255,0,0), 2)
        
        # ถ้าเจอแมว ให้เก็บจุดลงใน list
        if center_cat:
            points.append(center_cat)
        
        # วาดเส้นหาง
        # ต้องเริ่มที่ 1 ไม่งั้น error
        for i in range(1, len(points)):
            if points[i - 1] is None or points[i] is None:
                continue
            
            # คำนวณความหนา ยิ่งใกล้ยิ่งหนา
            # สูตรมั่วๆ เอาให้มันดูเรียวๆ
            thick = int(5 * (i / len(points))) + 1
            
            # สีเหลือง (0, 255, 255)
            cv2.line(frame, points[i - 1], points[i], (0, 255, 255), thick)

        # ชื่อมุมขวาบน
        text = "[Phoommin] + Clicknext-Internship-2024"
        
        # คำนวณตำแหน่งเองยาก ใช้ function ช่วย
        size = cv2.getTextSize(text, 0, 0.6, 2)[0]
        x_pos = frame.shape[1] - size[0] - 10
        
        # วาดเงาดำๆ จะได้เห็นชัด
        cv2.putText(frame, text, (x_pos+1, 31), 0, 0.6, (0,0,0), 2)
        cv2.putText(frame, text, (x_pos, 30), 0, 0.6, (255,255,255), 2)

        cv2.imshow("Result", frame)

        # กด q ออก
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    # print("End job")

if __name__ == "__main__":
    main()

# Final check passed
