import requests
import sys
import threading
import time
from tkinter import *
from tkinter import messagebox

SERVER_URL = "http://127.0.0.1:5000"  # 서버의 공인(외부) IP:(포트)5000 으로 변경

# 라이선스 상태를 주기적으로 확인
def check_license_status_periodically(license_key):
    while True:
        time.sleep(30)
        try:
            response = requests.post(SERVER_URL + "/check_license", json={"license_key": license_key})
            result = response.json()
            if result["status"] == "revoked":
                # print("관리자에 의해 사용이 중단되었습니다")
                messagebox.showinfo(title="revoked", message="관리자에 의해 사용이 중단되었습니다")
                sys.exit()
            elif result["status"] == "error":
                # print("라이선스 기간 만료 또는 오류로 프로그램이 종료됩니다")
                messagebox.showinfo(title="error", message="라이선스 기간 만료 또는 오류로 프로그램이 종료됩니다")
                sys.exit()
        except Exception as e:
            # print(f"서버 연결 실패: {e}")
            continue  # 일시적인 오류는 무시하고 재시도

# 라이선스 해제 요청
def release_license(license_key):
    try:
        requests.post(SERVER_URL + "/release_license", json={"license_key": license_key})
    except:
        pass  # 실패해도 무시

# 라이선스 인증시 프로그램 실행
def main():
    def submit_license():
        license_key = license_entry.get().strip()

        try:
            response = requests.post(SERVER_URL + "/check_license", json={"license_key": license_key})
            result = response.json()

            if result["status"] == "ok":
                lab2.config(text="라이선스 인증 성공")
                input_license_window.destroy()

                # 백그라운드에서 상태 확인 스레드 실행
                checker_thread = threading.Thread(target=check_license_status_periodically, args=(license_key,),
                                                  daemon=True)
                checker_thread.start()

                try:
                    main_program()
                finally:
                    release_license(license_key)

            elif result["status"] == "denied":
                lab2.config(text="라이선스 키가 이미 사용 중입니다")
            elif result["status"] == "revoked":
                lab2.config(text="라이선스가 관리자에 의해 사용 중단되었습니다")
            elif result["status"] == "error":
                lab2.config(text=f"오류: {result['message']}")
            else:
                lab2.config(text="알 수 없는 오류")

        except Exception as e:
            lab2.config(text=f"서버 연결 실패")

    # 라이선스 입력 창
    input_license_window = Tk()
    input_license_window.title('라이선스 인증')
    input_license_window.minsize(width=470, height=180)

    lab1 = Label(input_license_window, text="라이선스 키를 입력하세요")
    lab1.pack(pady=10)

    license_entry = Entry(input_license_window, width=40)
    license_entry.pack(pady=5)

    submit_btn = Button(input_license_window, text="확인", command=submit_license)
    submit_btn.pack(pady=5)

    lab2 = Label(input_license_window, text="", wraplength=450)
    lab2.pack()

    input_license_window.mainloop()

def main_program():
    print("프로그램이 실행 중입니다.")
    ###########################################################################################################################
    # 여기에 주요 프로그램 기능 작성
    input("Enter 눌러 종료: ")
    ###########################################################################################################################

if __name__ == "__main__":
    main()
