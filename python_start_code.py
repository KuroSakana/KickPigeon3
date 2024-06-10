import cv2
import torch
import serial
import time

# 아두이노와의 직렬 통신 설정
ser = serial.Serial('/dev/ttyACM0', 9600)

# YOLOv5 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'custom', path='../runs/train/exp9/weights/last.pt')  # 학습된 모델 경로 설정

# 웹캠 설정
cap = cv2.VideoCapture(0)

# MP3 재생 플래그
is_playing = False

# 객체 위치를 10개의 구역으로 나누어 구역 번호 반환
def get_zone(x, frame_width):
    zone_width = frame_width / 10
    return int(x // zone_width)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLOv5로 객체 감지
    results = model(frame)

    # 감지된 객체 정보
    detections = results.xyxy[0].cpu().numpy()

    if len(detections) > 0:
        for *box, conf, cls in detections:
            # 감지된 객체의 박스를 화면에 표시
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'{model.names[int(cls)]} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 객체의 중심 x 좌표 계산
            x_center = (x1 + x2) / 2
            frame_width = frame.shape[1]
            zone = get_zone(x_center, frame_width)
            
            # 구역 번호 반전
            reversed_zone = 9 - zone
            
            # 아두이노로 반전된 위치 값 전송
            ser.write(f'{reversed_zone}\n'.encode())

        if not is_playing:
            # 물체가 감지되었고 재생 중이 아닌 경우
            ser.write(b"play\n")  # 아두이노로 재생 명령 전송
            print("Playing MP3")
            is_playing = True
            start_time = time.time()  # 재생 시작 시간 기록
        else:
            # 물체가 계속 감지되는 경우
            if time.time() - start_time > 30:
                # 재생 시간이 30초를 초과한 경우
                ser.write(b"stop\n")  # 아두이노로 재생 중지 명령 전송
                print("Stopped MP3")
                is_playing = False
    else:
        if is_playing:
            # 물체가 감지되지 않고 재생 중인 경우
            ser.write(b"stop\n")  # 아두이노로 재생 중지 명령 전송
            print("Stopped MP3")
            is_playing = False

    # 결과를 화면에 표시
    cv2.imshow('YOLOv5', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 해제
cap.release()
cv2.destroyAllWindows()