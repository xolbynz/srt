import sys
import os
import threading
import time
import random
import logging
import tkinter as tk
from tkinter import messagebox

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException

WAIT_SEC = 1

def now_str():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def app_dir():
    """
    - PyInstaller onefile로 실행 시: sys.executable이 있는 폴더(= exe가 있는 폴더)
    - 일반 실행 시: 현재 스크립트 폴더
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def setup_logger():
    log_path = os.path.join(app_dir(), "srt_macro.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.info("=== SRT Macro Started ===")
    logging.info(f"App dir: {app_dir()}")
    logging.info(f"Log path: {log_path}")

def find_chromedriver():
    """
    1) exe/스크립트 폴더에 chromedriver.exe(Windows) 또는 chromedriver(mac/linux)가 있으면 사용
    2) 없으면 Selenium Manager(설치환경에 따라 자동 드라이버 관리) 시도
       - Selenium Manager가 막히는 환경이 많아서 1) 방식 권장
    """
    exe_name = "chromedriver.exe" if os.name == "nt" else "chromedriver"
    local_path = os.path.join(app_dir(), exe_name)
    if os.path.exists(local_path):
        return local_path
    return None  # Selenium Manager 사용(드라이버 path 명시 안함)

def safe_quit(driver):
    try:
        driver.quit()
    except Exception:
        pass

# ---------------- GUI + Bot ----------------

class SRTMacroApp:
    def __init__(self):
        setup_logger()

        self.window = tk.Tk()
        self.window.title("고속철도 예약 매크로 (EXE 배포용)")
        self.window.protocol("WM_DELETE_WINDOW", self.window.quit)

        # Input vars
        self.id_var = tk.StringVar()
        self.pw_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.min_time_var = tk.StringVar()
        self.max_time_var = tk.StringVar()
        self.target_date_var = tk.StringVar()
        self.start_station_var = tk.StringVar()
        self.end_station_var = tk.StringVar()
        self.birth_var = tk.StringVar()

        # Layout
        row = 0
        tk.Label(self.window, text="오타 나면 안 됨고 주의해서 입력해주세요. 예) 를 잘 봐주세요").grid(row=row, column=0, columnspan=2, sticky="w"); row += 1
        tk.Label(self.window, text="ID:").grid(row=row, column=0, sticky="w")
        tk.Entry(self.window, textvariable=self.id_var).grid(row=row, column=1); row += 1

        tk.Label(self.window, text="PW:").grid(row=row, column=0, sticky="w")
        tk.Entry(self.window, textvariable=self.pw_var, show="*").grid(row=row, column=1); row += 1

        tk.Label(self.window, text="휴대폰번호(01012345678):").grid(row=row, column=0, sticky="w")
        tk.Entry(self.window, textvariable=self.phone_var).grid(row=row, column=1); row += 1

        tk.Label(self.window, text="출발 최소 시간 (예: 15:00):").grid(row=row, column=0, sticky="w")
        tk.Entry(self.window, textvariable=self.min_time_var).grid(row=row, column=1); row += 1

        tk.Label(self.window, text="출발 최대 시간 (예: 18:30):").grid(row=row, column=0, sticky="w")
        tk.Entry(self.window, textvariable=self.max_time_var).grid(row=row, column=1); row += 1

        tk.Label(self.window, text="출발일자 (예: 2025.12.26):").grid(row=row, column=0, sticky="w")
        tk.Entry(self.window, textvariable=self.target_date_var).grid(row=row, column=1); row += 1

        tk.Label(self.window, text="출발역(ex 광주송정):").grid(row=row, column=0, sticky="w")
        tk.Entry(self.window, textvariable=self.start_station_var).grid(row=row, column=1); row += 1

        tk.Label(self.window, text="도착역(ex 수서):").grid(row=row, column=0, sticky="w")
        tk.Entry(self.window, textvariable=self.end_station_var).grid(row=row, column=1); row += 1

        tk.Label(self.window, text="카카오 생년월일(941122):").grid(row=row, column=0, sticky="w")
        tk.Entry(self.window, textvariable=self.birth_var).grid(row=row, column=1); row += 1

        tk.Button(
            self.window,
            text="예약 시작",
            command=self.start_bot,
            bg="#2255aa",
            fg="white"
        ).grid(row=row, column=0, columnspan=2, pady=10)

    def validate(self):
        fields = [
            self.id_var.get().strip(),
            self.pw_var.get().strip(),
            self.phone_var.get().strip(),
            self.min_time_var.get().strip(),
            self.max_time_var.get().strip(),
            self.target_date_var.get().strip(),
            self.start_station_var.get().strip(),
            self.end_station_var.get().strip(),
            self.birth_var.get().strip(),
        ]
        return all(fields)

    def start_bot(self):
        if not self.validate():
            messagebox.showerror("입력오류", "모든 정보를 입력하세요")
            return

        # UI 숨기고 스레드로 실행
        self.window.withdraw()
        t = threading.Thread(target=self.main_bot, daemon=True)
        t.start()

    def main_bot(self):
        # 입력값
        user_id = self.id_var.get().strip()
        password = self.pw_var.get().strip()
        kakao_phone_number = self.phone_var.get().strip()
        min_time = self.min_time_var.get().strip()
        max_time = self.max_time_var.get().strip()
        target_date = self.target_date_var.get().strip()
        start_station = self.start_station_var.get().strip()
        end_station = self.end_station_var.get().strip()
        kakao_birth_date = self.birth_var.get().strip()

        refresh_time = 10  # 랜덤 리프레시 기준

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--headless=new")  # 필요하면 활성화

        driver = None
        try:
            chromedriver_path = find_chromedriver()

            if chromedriver_path:
                logging.info(f"Using chromedriver: {chromedriver_path}")
                driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
            else:
                # Selenium Manager 시도(환경에 따라 막힐 수 있음)
                logging.info("chromedriver not found next to exe. Trying Selenium Manager...")
                driver = webdriver.Chrome(options=chrome_options)

            # 1) 로그인 페이지
            login_url = "https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000"
            driver.get(login_url)
            time.sleep(1)

            # 2) 로그인
            id_input = driver.find_element(By.ID, "srchDvNm01")
            id_input.clear()
            id_input.send_keys(user_id)
            time.sleep(1)
            pw_input = driver.find_element(By.ID, "hmpgPwdCphd01")
            pw_input.clear()
            pw_input.send_keys(password)
            time.sleep(1)
            login_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR,
                    "#login-form > fieldset > div.input-area.loginpage.clear > div.fl_l > div.con.srchDvCd1 > div > div.fl_r > input")
                )
            )
            login_btn.click()
            time.sleep(1)   
            current_url = driver.current_url
            logging.info(f"현재 주소값: {current_url}")

            # 3) 출발/도착역
            dpt_station_select = driver.find_element(By.ID, "dptRsStnCd")
            for option in dpt_station_select.find_elements(By.TAG_NAME, "option"):
                if option.text.strip() == start_station:
                    option.click()
                    logging.info(f"출발역 '{start_station}' 선택됨")
                    break

            arv_station_select = driver.find_element(By.ID, "arvRsStnCd")
            for option in arv_station_select.find_elements(By.TAG_NAME, "option"):
                if option.text.strip() == end_station:
                    option.click()
                    logging.info(f"도착역 '{end_station}' 선택됨")
                    break

            # 4) 출발일자
            dpt_date_input = driver.find_element(By.NAME, "dptDt")
            driver.execute_script("arguments[0].removeAttribute('readonly')", dpt_date_input)
            dpt_date_input.clear()
            dpt_date_input.send_keys(target_date)
            logging.info(f"출발일자 {target_date}로 변경 완료")

            # 5) 출발시각(최소시간 이하 중 가장 가까운 옵션)
            dpt_time_select = driver.find_element(By.ID, "dptTm")
            min_h, min_m = map(int, min_time.split(":"))
            min_total_minutes = min_h * 60 + min_m

            closest_option = None
            closest_diff = None
            for option in dpt_time_select.find_elements(By.TAG_NAME, "option"):
                value = option.get_attribute("value") or ""
                if len(value) >= 4:
                    opt_h = int(value[:2])
                    opt_m = int(value[2:4])
                    opt_total_minutes = opt_h * 60 + opt_m
                    if opt_total_minutes <= min_total_minutes:
                        diff = min_total_minutes - opt_total_minutes
                        if closest_diff is None or diff < closest_diff:
                            closest_option = option
                            closest_diff = diff

            if closest_option is None:
                all_options = dpt_time_select.find_elements(By.TAG_NAME, "option")
                if all_options:
                    closest_option = all_options[-1]

            if closest_option is not None:
                closest_option.click()
                logging.info(f"출발시각 옵션 '{closest_option.text}' 선택됨")
            else:
                logging.info("출발시각 옵션을 찾을 수 없습니다.")

            driver.maximize_window()

            # 6) 간편조회하기
            simple_search_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="search-form"]/fieldset/div/div/button[2]'))
            )
            simple_search_btn.click()
            logging.info("'간편조회하기' 버튼 클릭 완료")
            time.sleep(2)

            # 7) NetFunnel 대기 체크
            while True:
                try:
                    netfunnel_top = driver.find_element(By.CSS_SELECTOR, "#NetFunnel_Skin_Top")
                    if netfunnel_top.is_displayed():
                        logging.info("접속 대기창 표시중... 1초 대기")
                        try:
                            cnt = driver.find_element(By.ID, "NetFunnel_Loading_Popup_Count").text
                            logging.info(f"대기표시: {cnt}")
                        except Exception:
                            pass
                        time.sleep(1)
                        continue
                    time.sleep(1)
                    continue
                except Exception:
                    logging.info("NetFunnel 대기창 없음. 진행")
                    break

            # 8) 결과 테이블 로딩
            wait = WebDriverWait(driver, 100000)
            tbody_selector = "#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody"
            tbody = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, tbody_selector)))
            rows = wait.until(lambda d: tbody.find_elements(By.TAG_NAME, "tr"))

            reservation_wait_state = 0  # 0:없음, 1:신청 클릭됨(확인 필요), 2:신청 완료 후 재조회중

            while True:
                time.sleep(1)
                try:
                    wait10 = WebDriverWait(driver, 10)
                    tbody = wait10.until(EC.presence_of_element_located((By.CSS_SELECTOR, tbody_selector)))
                    rows = wait10.until(lambda d: tbody.find_elements(By.TAG_NAME, "tr"))
                except Exception as e:
                    logging.info(f"결과 테이블 로딩 예외: {e}")
                    # 재조회 클릭 시도
                    try:
                        wait10 = WebDriverWait(driver, 10)
                        inquery = wait10.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.inquery_btn")))
                        driver.execute_script("arguments[0].scrollIntoView(false);", inquery)
                        try:
                            wait10.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.inquery_btn"))).click()
                        except ElementClickInterceptedException:
                            driver.execute_script("arguments[0].click();", inquery)
                    except Exception as e2:
                        logging.info(f"재조회 클릭 실패: {e2}")
                    continue

                reserved = False

                for row in rows:
                    # 시간 필터 (td4)
                    try:
                        td4_time = row.find_element(By.CSS_SELECTOR, "td:nth-child(4) > em").text.strip()
                        td4_h, td4_m = map(int, td4_time.split(":"))

                        min_hh, min_mm = map(int, min_time.split(":"))
                        max_hh, max_mm = map(int, max_time.split(":"))

                        td4_minutes = td4_h * 60 + td4_m
                        min_minutes = min_hh * 60 + min_mm
                        max_minutes = max_hh * 60 + max_mm

                        if td4_minutes < min_minutes or td4_minutes > max_minutes:
                            continue
                    except Exception:
                        pass

                    # 예약하기 (td7)
                    try:
                        td7_span = row.find_element(By.CSS_SELECTOR, "td:nth-child(7) > a > span")
                        if td7_span.text.strip() == "예약하기":
                            td7_span.click()
                            reserved = True
                            logging.info("예약하기 클릭 성공")
                            break
                    except Exception:
                        pass

                    # 신청하기 (td8) - 최초 1회만
                    if reservation_wait_state == 0:
                        try:
                            td8_span = row.find_element(By.CSS_SELECTOR, "td:nth-child(8) > a > span")
                            if td8_span.text.strip() == "신청하기":
                                td8_span.click()
                                reservation_wait_state = 1
                                logging.info("신청하기 클릭 성공")
                                break
                        except Exception:
                            pass

                # 신청하기 후 확인
                if reservation_wait_state == 1:
                    try:
                        sms_yes = driver.find_element(By.ID, "smsY")
                        if not sms_yes.is_selected():
                            driver.execute_script("arguments[0].scrollIntoView(true);", sms_yes)
                            try:
                                sms_yes.click()
                            except Exception:
                                driver.execute_script("arguments[0].click();", sms_yes)

                        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
                        alert.accept()
                    except Exception:
                        pass

                    try:
                        diff_seat = driver.find_element(By.ID, "diffSeatY")
                        if not diff_seat.is_selected():
                            driver.execute_script("arguments[0].scrollIntoView(true);", diff_seat)
                            try:
                                diff_seat.click()
                            except Exception:
                                driver.execute_script("arguments[0].click();", diff_seat)
                    except Exception:
                        pass

                    try:
                        confirm_btn = driver.find_element(By.ID, "moveTicketList")
                        driver.execute_script("arguments[0].scrollIntoView(true);", confirm_btn)
                        confirm_btn.click()

                        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
                        alert.accept()

                        driver.get(current_url)
                        reservation_wait_state = 2
                        logging.info("신청 완료 처리 후 재조회 페이지로 이동")
                        continue
                    except Exception:
                        pass

                if reserved:
                    break

                # 예약 실패 시 랜덤 대기 후 재조회
                random_refresh_time = random.randint(int(refresh_time / 2), int(refresh_time / 2 + refresh_time))
                logging.info(f"예약 없음. {random_refresh_time}s 후 재조회")
                time.sleep(random_refresh_time)

                # NetFunnel 재체크
                while True:
                    try:
                        nf = driver.find_element(By.CSS_SELECTOR, "#NetFunnel_Skin_Top")
                        if nf.is_displayed():
                            time.sleep(1)
                            continue
                        time.sleep(1)
                        continue
                    except Exception:
                        break

                try:
                    wait10 = WebDriverWait(driver, 10)
                    inquery = wait10.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.inquery_btn")))
                    driver.execute_script("arguments[0].scrollIntoView(false);", inquery)
                    try:
                        wait10.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.inquery_btn"))).click()
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", inquery)
                except Exception as e:
                    logging.info(f"재조회 실패: {e}")

            # 9) 결제 파트 (원본 흐름 유지)
            time.sleep(1)
            try:
                pay_btn = WebDriverWait(driver, WAIT_SEC).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#list-form > fieldset > div.tal_c > a.btn_large.btn_blue_dark.val_m.mgr10 > span"))
                )
                if pay_btn.text.strip() == "결제하기":
                    pay_btn.click()
                    logging.info("결제하기 클릭")
            except Exception:
                pass

            try:
                tab_ul = WebDriverWait(driver, WAIT_SEC).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#select-form > fieldset > div.tab.tab4.subtab > ul"))
                )
                ch_tab2 = tab_ul.find_element(By.CSS_SELECTOR, "#chTab2")
                ch_tab2.click()
                logging.info("결제수단 탭(chTab2) 클릭")
            except Exception:
                pass

            try:
                container_div = WebDriverWait(driver, WAIT_SEC).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#settle_payco > div.tbl_wrap.tbl3 > table > tbody > tr > td > div"))
                )
                kakao_radio = container_div.find_element(By.ID, "kakaoPay")
                driver.execute_script("arguments[0].scrollIntoView(true);", kakao_radio)
                if not kakao_radio.is_selected():
                    try:
                        WebDriverWait(driver, WAIT_SEC).until(EC.element_to_be_clickable((By.ID, "kakaoPay")))
                        kakao_radio.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", kakao_radio)
                logging.info("카카오페이 선택")
            except Exception:
                pass

            try:
                request_issue2_btn = WebDriverWait(driver, WAIT_SEC).until(
                    EC.element_to_be_clickable((By.ID, "requestIssue2"))
                )
                request_issue2_btn.click()
                logging.info("requestIssue2 클릭")
            except Exception:
                pass

            try:
                WebDriverWait(driver, WAIT_SEC).until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[1])
                logging.info("결제 팝업 창으로 전환")
            except Exception:
                pass

            try:
                WebDriverWait(driver, WAIT_SEC).until(EC.presence_of_element_located((By.ID, "카톡결제")))
                katalk_tab = driver.find_element(By.ID, "카톡결제")
                driver.execute_script("arguments[0].scrollIntoView(true);", katalk_tab)
                katalk_tab.click()
                logging.info("카톡결제 탭 클릭")
            except Exception:
                pass

            WebDriverWait(driver, WAIT_SEC).until(EC.presence_of_element_located((By.ID, "phoneNumber")))
            phone_input = driver.find_element(By.ID, "phoneNumber")
            time.sleep(1)
            phone_input.send_keys(kakao_phone_number)

            WebDriverWait(driver, WAIT_SEC).until(EC.presence_of_element_located((By.ID, "dateOfBirth")))
            dob_input = driver.find_element(By.ID, "dateOfBirth")
            time.sleep(1)
            dob_input.send_keys(kakao_birth_date)

            try:
                WebDriverWait(driver, WAIT_SEC).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'kp-m-button') and contains(@class, 'primary') and .//p[text()='결제요청']]"))
                )
                kp_pay_btn = driver.find_element(
                    By.XPATH, "//button[contains(@class, 'kp-m-button') and contains(@class, 'primary') and .//p[text()='결제요청']]"
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", kp_pay_btn)
                kp_pay_btn.click()
                logging.info("결제요청 클릭")
            except Exception:
                pass

            messagebox.showinfo("완료", "흐름이 종료되었습니다. 로그(srt_macro.log)를 확인하세요.")
            logging.info("Flow finished.")

        except Exception as e:
            logging.exception("치명 오류 발생")
            messagebox.showerror("오류", f"오류 발생: {e}\n로그(srt_macro.log)를 확인하세요.")
        finally:
            if driver:
                safe_quit(driver)
            try:
                self.window.quit()
            except Exception:
                pass


if __name__ == "__main__":
    app = SRTMacroApp()
    app.window.mainloop()
