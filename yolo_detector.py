import cv2
from ultralytics import YOLO
from collections import deque
import time

# Phoommin | Clicknext-Internship-2024
# ไฟล์นี้เขียนขึ้นเพื่อส่งสอบ Internship ครับ 
# เน้น Detect แมว + วาดหางตามโจทย์ครับ

def main():
    # 1. โหลดโมเดล YOLOv8 Nano (ตัวเล็กสุด ทำงานเร็ว)
    # ถ้าไม่มีไฟล์ เดี๋ยว ultralytics มันโหลดให้เองครับ
    print("[Info] กำลังโหลดโมเดล...")
    try:
        model = YOLO('yolov8n.pt')
    except Exception as e:
        print(f"[Error] โหลดโมเดลไม่ได้ครับ: {e}")
        return

    # 2. เปิดไฟล์วิดีโอ (ต้องมีไฟล์ชื่อ CatZoomies.mp4 ในโฟลเดอร์เดียวกัน)
    video_path = "CatZoomies.mp4"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"[Error] เปิดไฟล์วิดีโอ {video_path} ไม่ได้ครับ เช็คชื่อไฟล์หน่อย")
        return

    # 3. เตรียมตัวแปรสำหรับวาดหาง (เก็บจุดกึ่งกลางย้อนหลัง 30 เฟรม)
    # ใช้ deque เพราะมันจัดการ memory ดีกว่า list เวลา add/pop
    trail_points = deque(maxlen=30)

    print("[Info] เริ่มรันโปรแกรม... กด 'q' เพื่อออกนะครับ")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Info] จบวิดีโอแล้วครับ")
            break

        # 4. Detect Object
        # classes=[15] คือ id ของแมวใน COCO Dataset (เช็คมาแล้วครับ)
        # verbose=False คือไม่ต้องปริ้น log รกๆ ออกมาที่ terminal
        results = model(frame, classes=[15], verbose=False)

        # ตัวแปรสำหรับเก็บตำแหน่งแมวในเฟรมนี้ (เอาตัวที่มั่นใจสุด)
        best_center = None
        max_conf = 0.0

        for r in results:
            boxes = r.boxes
            for box in boxes:
                # ดึงพิกัด bbox
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # ดึงค่า confidence
                conf = box.conf.item()

                # 5. วาดกรอบสีน้ำเงิน (Blue) ตามโจทย์
                # OpenCV ใช้สีแบบ BGR -> (255, 0, 0) คือสีน้ำเงิน
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

                # แสดง text ความมั่นใจ
                label = f"Cat: {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # หาจุดกึ่งกลางเพื่อเอาไปวาดหาง
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                # เก็บตัวที่ดีที่สุดในเฟรมนี้
                if conf > max_conf:
                    max_conf = conf
                    best_center = (cx, cy)

        # 6. อัปเดตจุดหาง
        if best_center:
            trail_points.append(best_center)

        # 7. วาดเส้นหาง (Trail)
        # ต้อง loop ตั้งแต่ index 1 เพื่อลากเส้นเชื่อมกับจุดก่อนหน้า
        for i in range(1, len(trail_points)):
            if trail_points[i - 1] is None or trail_points[i] is None:
                continue
            
            # คำนวณความหนา: ยิ่งเก่ายิ่งบาง ยิ่งใหม่ยิ่งหนา
            # สูตรบ้านๆ: (ตำแหน่ง / ความยาวรวม) * ขนาดสูงสุด + 1
            thickness = int((i / len(trail_points)) * 5) + 1
            
            # สีเส้นขอเป็นสีเหลือง (Cyan/Yellow) ตัดกับสีน้ำเงิน
            cv2.line(frame, trail_points[i - 1], trail_points[i], (0, 255, 255), thickness)

        # 8. ใส่ลายน้ำ (Watermark) มุมขวาบน
        text = "Phoommin | Clicknext-Internship-2024"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.6
        color = (255, 255, 255) # สีขาว
        thickness = 2
        
        # คำนวณตำแหน่งให้ชิดขวา
        (text_w, text_h), _ = cv2.getTextSize(text, font, scale, thickness)
        margin_x = 10
        margin_y = 30
        x = frame.shape[1] - text_w - margin_x
        y = margin_y

        # วาดเงาสีดำก่อนเพื่อให้อ่านง่าย (Shadow Effect)
        cv2.putText(frame, text, (x + 1, y + 1), font, scale, (0, 0, 0), thickness + 1)
        # วาดตัวหนังสือจริง
        cv2.putText(frame, text, (x, y), font, scale, color, thickness)

        # แสดงผล
        cv2.imshow("Clicknext Internship Exam - Phoommin", frame)

        # กด q เพื่อปิด
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[Debug] User pressed q")
            break

    # เคลียร์ memory
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
