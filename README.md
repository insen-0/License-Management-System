# License-Management-System
파이썬 프로그램의 라이선스 관리 시스템입니다.


## 작동 방식
클라이언트 프로그램(LMS_client.py) 시작 시 사용자에게 라이선스 키를 입력받고 유효한 경우 main_program()으로 진입하며,
이후 60초 간격으로 서버측(LMS_server.py)에 해당 키의 상태를 확인받습니다.

키가 삭제되거나 기간이 만료되는 등 유효하지 않은 상태일 경우 프로그램이 종료됩니다.


## 사용법
- 라이선스를 관리하여 사용 여부를 제어할 코드 내용을 LMS_client.py의 main_program() 안에 작성합니다.

- LMS_client.py의 "SERVER_URL"을 서버의 IP로 변경합니다.

- LMS_server 코드가 작동중인 상태에서 LMS_client 코드를 실행하면 미리 등록되어있는 키로 프로그램 시작이 가능합니다.
  (LMS_server.py가 중단되면 LMS_client.py도 종료되므로, LMS_server는 항시 작동 중이어야 합니다.)

- LMS_GUI.py를 사용하여 라이선스 키를 쉽게 생성,수정,삭제할 수 있습니다.
![LMS_GUI 예시 이미지](https://github.com/insen-0/License-Management-System/blob/main/LMS_GUI_%EC%98%88%EC%8B%9C.png)
