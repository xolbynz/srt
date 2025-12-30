import subprocess
import time

while True:
    try:
        # main.py를 실행 (파이썬 인터프리터 명령어/경로는 환경에 따라 다를 수 있음)
        process = subprocess.Popen(['python', 'main.py'])
        process.wait()
        print("[cont.py] main.py가 종료되었습니다. 5초 후 재시작합니다...")
        time.sleep(5)
    except Exception as e:
        print(f"[cont.py] 예외 발생: {e}. 10초 후 재시작합니다...")
        time.sleep(10)
