import cv2
from ultralytics import YOLO

VIDEO_YOLU = "Videolar/deneme2.mp4"

KIRMIZI = (0, 0, 255)
YESIL = (0, 255, 0)

model = YOLO("yolo11n.pt")
cap = cv2.VideoCapture(VIDEO_YOLU)

if not cap.isOpened():
    raise SystemExit(f"Video açılamadı: {VIDEO_YOLU}")

# Bölge tanımlama (video boyutlarını doğrudan videodan al)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

x1 = int(w * 0.28)
x2 = int(w * 0.63)
y1 = int(h * 0.08)
y2 = int(h * 0.58)

gecenler = set()  # bölgeye giren kişilerin ID'leri

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, classes=[0], persist=True, verbose=False)
    boxes = results[0].boxes

    iceride_var = False

    if boxes.id is not None:
        for box, tid in zip(boxes.xyxy, boxes.id):
            bx1, by1, bx2, by2 = map(int, box)
            tid = int(tid)

            # Ayak noktası: kutunun alt-orta noktası
            cx = (bx1 + bx2) // 2
            cy = by2

            iceride = x1 < cx < x2 and y1 < cy < y2
            if iceride:
                iceride_var = True
                gecenler.add(tid)

            renk = YESIL if iceride else KIRMIZI
            cv2.rectangle(frame, (bx1, by1), (bx2, by2), renk, 2)
            cv2.circle(frame, (cx, cy), 4, renk, -1)
            cv2.putText(frame, f"ID {tid}", (bx1, max(by1 - 8, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, renk, 2)

    # İçeride biri varsa bölge yeşil, yoksa kırmızı
    bolge_renk = YESIL if iceride_var else KIRMIZI
    cv2.rectangle(frame, (x1, y1), (x2, y2), bolge_renk, 2)
    cv2.putText(frame, f"Gecen Kisi: {len(gecenler)}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, KIRMIZI, 2)

    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
