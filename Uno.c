#include <SoftwareSerial.h>
#include <DFRobotDFPlayerMini.h>
#include <Servo.h>

// DFPlayer Mini 모듈과 통신하기 위한 SoftwareSerial 설정
SoftwareSerial mySerial(10, 11); // RX, TX
DFRobotDFPlayerMini myDFPlayer;

// 소리 재생 플래그 및 시간
bool isPlaying = false;
unsigned long playStartTime = 0;
const unsigned long playDuration = 10000; // 10초

// 서보 모터 설정
Servo servo1;
Servo servo2;

void setup() {
  // 시리얼 통신 시작
  Serial.begin(9600);
  mySerial.begin(9600);
  
  // DFPlayer Mini 초기화
  if (!myDFPlayer.begin(mySerial)) {
    Serial.println("DFPlayer Mini 초기화 실패!");
    while (true);
  }
  Serial.println("DFPlayer Mini 초기화 성공!");

  // 음량 설정 (0 ~ 30)
  myDFPlayer.volume(30);

  // 서보 모터 초기화
  servo1.attach(5); // 서보 모터 1을 디지털 핀 5에 연결
  servo2.attach(6); // 서보 모터 2를 디지털 핀 6에 연결
}

void loop() {
  // 라즈베리 파이로부터 명령 수신
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    if (command == "play" && !isPlaying) {
      // 소리 재생 명령
      myDFPlayer.play(1);
      isPlaying = true;
      playStartTime = millis();
      Serial.println("Playing MP3");
    } else if (command == "stop" && isPlaying) {
      // 소리 중지 명령
      myDFPlayer.stop();
      isPlaying = false;
      Serial.println("Stopped MP3");
    } else {
      // 객체 위치 값 수신
      int zone = command.toInt();
      int angle = map(zone, 0, 9, 0, 180); // 구역 번호를 0도에서 180도 사이의 각도로 변환
      servo2.write(angle); // 서보 모터 2를 해당 각도로 회전
    }
  }

  // 소리 재생 시간 확인
  if (isPlaying && (millis() - playStartTime > playDuration)) {
    myDFPlayer.stop();
    isPlaying = false;
    Serial.println("Stopped MP3 after 10 seconds");
    servo1.write(80);
    delay(3000);
    servo1.write(20);
    delay(3000);
 }
}