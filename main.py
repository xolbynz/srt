#1892761406
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
import random

def now_str():
    return time.strftime("%Y-%m-%d %H:%M:%S")

wait_sec = 1
# Chrome 옵션을 확인합니다.
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--headless=new') # 주석처리 또는 제거하면 브라우저가 화면에 뜹니다.

# 크롬 창이 안 켜진다면 아래 주석을 참고하세요.
# 1. headless 옵션이 켜져 있으면 창이 뜨지 않습니다. 위 옵션을 주석처리 하세요.
# 2. chromedriver가 환경에 설치되어 있는지 확인하세요.
# 3. 경로 문제가 있다면 chromedriver 경로를 명시적으로 지정하세요.

# chromedriver 경로를 직접 지정하려면 예시:
# driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=chrome_options)
driver = webdriver.Chrome(options=chrome_options)

import yaml
##  config 만드시옹
try:
    with open(r'config.yaml', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)
except Exception as e:
    print(f"[{now_str()}] config.yaml 파일을 찾을 수 없습니다: {e}")
    exit(1)


id = config['id']
password = config['password']
kakao_phone_number = config['kakao_phone_number']
min_time = config['min_time']
max_time = config['max_time']
target_date = config['target_date']
start_station = config['start_station']
end_station = config['end_station']
kakao_birth_date = config['kakao_birth_date']
refresh_time = 10
###
try:
    # Open target website
    driver.get('https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000')
    time.sleep(1)  # Wait for page to load
    # id와 password 입력하고 로그인 버튼 클릭
    # ID 입력
    id_input = driver.find_element(By.ID, "srchDvNm01")
    id_input.clear()
    id_input.send_keys(id)

    # PW 입력
    pw_input = driver.find_element(By.ID, "hmpgPwdCphd01")
    pw_input.clear()
    pw_input.send_keys(password)

    # 로그인 버튼 클릭
    login_btn = driver.find_element(By.CSS_SELECTOR, "#login-form > fieldset > div.input-area.loginpage.clear > div.fl_l > div.con.srchDvCd1 > div > div.fl_r > input")
    login_btn.click()

    time.sleep(1)
    current_url = driver.current_url
    print(f"[{now_str()}] 현재 주소값: {current_url}")
    # '출발역' 셀렉트 박스에서 '수서'를 선택합니다.
    dpt_station_select = driver.find_element(By.ID, "dptRsStnCd")
    for option in dpt_station_select.find_elements(By.TAG_NAME, "option"):
        if option.text.strip() == start_station:
            option.click()
            print(f"[{now_str()}] 출발역 '{start_station}' 선택됨")
            break
    # '도착역' 셀렉트 박스에서 '광주송정'을 선택합니다.
    arv_station_select = driver.find_element(By.ID, "arvRsStnCd")
    for option in arv_station_select.find_elements(By.TAG_NAME, "option"):
        if option.text.strip() == end_station:
            option.click()
            print(f"[{now_str()}] 도착역 '{end_station}' 선택됨")
            break
    # 출발일자 입력 필드(dptDt)의 값을 2025.11.28로 변경합니다.
    dpt_date_input = driver.find_element(By.NAME, "dptDt")
    driver.execute_script("arguments[0].removeAttribute('readonly')", dpt_date_input)
    dpt_date_input.clear()
    dpt_date_input.send_keys(target_date)
    print(f"[{now_str()}] 출발일자 {target_date}로 변경 완료")
    # '<span>간편조회하기</span>'를 클릭합니다.
    # '출발시각' 셀렉트 박스에서 min_time에 가장 가까운 옵션을 선택합니다.
    dpt_time_select = driver.find_element(By.ID, "dptTm")
    min_h, min_m = map(int, min_time.split(":"))
    min_total_minutes = min_h * 60 + min_m

    closest_option = None
    closest_diff = None

    for option in dpt_time_select.find_elements(By.TAG_NAME, "option"):
        # option.value 예: "140000"
        value = option.get_attribute("value")
        if len(value) >= 4:
            opt_h = int(value[:2])
            opt_m = int(value[2:4])
            opt_total_minutes = opt_h * 60 + opt_m
            # 옵션이 min_time보다 크거나 같고 가장 작은 값을 선택
            if opt_total_minutes >= min_total_minutes:
                diff = opt_total_minutes - min_total_minutes
                if closest_diff is None or diff < closest_diff:
                    closest_option = option
                    closest_diff = diff

    # 만약 min_time과 같거나 큰 옵션이 없다면, 가장 마지막 옵션을 선택
    if closest_option is None:
        all_options = dpt_time_select.find_elements(By.TAG_NAME, "option")
        if all_options:
            closest_option = all_options[-1]

    if closest_option is not None:
        closest_option.click()
        print(f"[{now_str()}] 출발시각 옵션 '{closest_option.text}' 선택됨")
    else:
        print(f"[{now_str()}] 출발시각 옵션을 찾을 수 없습니다.")
    simple_search_span = driver.find_element(By.XPATH, "//span[text()='간편조회하기']")
    simple_search_span.click()
    print(f"[{now_str()}] '간편조회하기' 버튼 클릭 완료")

    
    time.sleep(wait_sec)
    # tbody element for the result rows
    tbody_selector = "#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody"
    tbody = driver.find_element(By.CSS_SELECTOR, tbody_selector)
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    # 예약이 될때까지 계속 새로고침 하면서 반복
    # 현재 페이지 주소값 저장 (현재 URL 얻기)

    예약_대기성공=0
    while True:
        time.sleep(1)
        tbody_selector = "#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody"
        try:
            wait = WebDriverWait(driver, 10)
            tbody = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, tbody_selector))
            )
            wait = WebDriverWait(driver, 10)
            rows = wait.until(lambda d: tbody.find_elements(By.TAG_NAME, "tr"))
        except Exception as e:
            print(f"[{now_str()}] {e}")    
            # print(f"예약 가능한 항목이 없습니다. {refresh_time}초 후 새로고침합니다.")
            # time.sleep(refresh_time)
            wait = WebDriverWait(driver, 10)

            # 1. 버튼이 보이도록 스크롤 (화면 "아래쪽"에 위치하게)
            search_top_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.inquery_btn"))
            )

            # 요소를 화면 하단 쪽에 맞춤 (true는 상단, false는 하단)
            driver.execute_script("arguments[0].scrollIntoView(false);", search_top_input)

            # 필요하면 조금만 더 올리거나 내릴 수도 있음
            # driver.execute_script("window.scrollBy(0, -50);")  # 위로 50px
            # driver.execute_script("window.scrollBy(0, 50);")   # 아래로 50px

            try:
                # 2. 일반 클릭 시도
                search_top_input = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input.inquery_btn"))
                )
                search_top_input.click()

            except ElementClickInterceptedException:
                # 3. 여전히 login_wrap이 가리면, JS로 강제 클릭
                search_top_input = driver.find_element(By.CSS_SELECTOR, "input.inquery_btn")
                driver.execute_script("arguments[0].click();", search_top_input)
            continue
        # time.sleep(1)
        예약_성공 = False
        for i, row in enumerate(rows):
            index = i + 1

            # td[4] div & em
            try:
                td4_div = row.find_element(By.CSS_SELECTOR, f"td:nth-child(4) > div")
                print(f"[{now_str()}] Row {index} td4 div: {td4_div.text}")
            except Exception as e:
                print(f"[{now_str()}] Row {index} td4 div not found")

            try:
                td4_em = row.find_element(By.CSS_SELECTOR, f"td:nth-child(4) > em")
                print(f"[{now_str()}] Row {index} td4 em: {td4_em.text}")
                td4_time = td4_em.text.strip()
                td4_h, td4_m = map(int, td4_time.split(":"))
                min_h, min_m = map(int, min_time.split(":"))
                max_h, max_m = map(int, max_time.split(":"))
                td4_minutes = td4_h * 60 + td4_m
                min_minutes = min_h * 60 + min_m
                max_minutes = max_h * 60 + max_m
                if td4_minutes < min_minutes:
                    print(f"[{now_str()}] Row {index} td4 em 시간({td4_time})이 최소 시간({min_time}) 미만이므로 건너뜀.")
                    continue
                if td4_minutes > max_minutes:
                    print(f"[{now_str()}] Row {index} td4 em 시간({td4_time})이 최대 시간({max_time}) 초과이므로 건너뜀.")
                    continue
                

            except Exception as e:
                print(f"[{now_str()}] Row {index} td4 em not found")

            # # td[5] div & em
            # try:
            #     td5_div = row.find_element(By.CSS_SELECTOR, f"td:nth-child(5) > div")
            #     print(f"[{now_str()}] Row {index} td5 div: {td5_div.text}")
            # except Exception as e:
            #     print(f"[{now_str()}] Row {index} td5 div not found")

            # try:
            #     td5_em = row.find_element(By.CSS_SELECTOR, f"td:nth-child(5) > em")
            #     print(f"[{now_str()}] Row {index} td5 em: {td5_em.text}")
            # except Exception as e:
            #     print(f"[{now_str()}] Row {index} td5 em not found")

            # try:
            #     td6_span = row.find_element(By.CSS_SELECTOR, f"td:nth-child(6) > a > span")
            #     print(f"[{now_str()}] 특실 {td6_span.text}")
            #     if td6_span.text.strip() == "예약하기":
            #         td6_span.click()
            #         예약_성공 = True
            #         break
            # except Exception as e:
            #     print(f"[{now_str()}] Row {index} td6 span not found")


            try:
                td7_span = row.find_element(By.CSS_SELECTOR, f"td:nth-child(7) > a > span")
                print(f"[{now_str()}] 일반실 {td7_span.text}")
                if td7_span.text.strip() == "예약하기":
                    td7_span.click()
                    예약_성공 = True
                    break
            except Exception as e:
                print(f"[{now_str()}] Row {index} td7 span not found")

            # td[8] > a > span
            if  예약_대기성공==0:
                try:
                    td8_span = row.find_element(By.CSS_SELECTOR, f"td:nth-child(8) > a > span")
                    print(f"[{now_str()}] 예약대기 {td8_span.text}")
                    if td8_span.text.strip() == "신청하기":
                        td8_span.click()
                        예약_대기성공 = 1
                        break
                except Exception as e:
                    print(f"[{now_str()}] Row {index} td8 span not found")

        if 예약_대기성공==1:
            try:
                # "예" 라디오 버튼 찾기 (id="smsY")
                sms_yes_radio = driver.find_element(By.ID, "smsY")
                if not sms_yes_radio.is_selected():
                    driver.execute_script("arguments[0].scrollIntoView(true);", sms_yes_radio)
                    try:
                        sms_yes_radio.click()
                    except Exception as radio_e:
                        print(f"[{now_str()}] smsY 라디오버튼 클릭 실패, JS로 재시도합니다.")
                        driver.execute_script("arguments[0].click();", sms_yes_radio)
                print(f"[{now_str()}] 문자 발송 여부(예)에 체크했습니다.")
                # 2. confirm() 팝업 뜰 때까지 기다렸다가 '확인' 누르기
                alert = wait.until(EC.alert_is_present())
                print(f"[{now_str()}] {alert.text}")  # 필요 없으면 지워도 됨
                alert.accept()      # ✅ '확인' 버튼에 해당
            except Exception as e:
                print(f"[{now_str()}] smsY 라디오버튼을 찾을 수 없습니다:", e)
            try:
                # "다른 좌석 유형" 라디오 버튼 찾기 (id="diffSeatY")
                diff_seat_radio = driver.find_element(By.ID, "diffSeatY")
                if not diff_seat_radio.is_selected():
                    driver.execute_script("arguments[0].scrollIntoView(true);", diff_seat_radio)
                    try:
                        diff_seat_radio.click()
                    except Exception as diff_seat_e:
                        print(f"[{now_str()}] diffSeatY 라디오버튼 클릭 실패, JS로 재시도합니다.")
                        driver.execute_script("arguments[0].click();", diff_seat_radio)
                print(f"[{now_str()}] 다른 좌석 유형(체크)에 체크했습니다.")
            except Exception as e:
                print(f"[{now_str()}] diffSeatY 라디오버튼을 찾을 수 없습니다:", e)
            try:
                # "확인" 버튼 찾기 (id="moveTicketList")
                confirm_btn = driver.find_element(By.ID, "moveTicketList")
                driver.execute_script("arguments[0].scrollIntoView(true);", confirm_btn)
                confirm_btn.click()
                print(f"[{now_str()}] '확인' 버튼(moveTicketList)을 클릭했습니다.")
                alert = wait.until(EC.alert_is_present())
                print(f"[{now_str()}] {alert.text}")  # 필요 없으면 지워도 됨
                alert.accept()
                driver.get(current_url)
                # INSERT_YOUR_CODE
                print(f"[{now_str()}] 현재 주소값: {current_url}")
                # '출발역' 셀렉트 박스에서 '수서'를 선택합니다.
                dpt_station_select = driver.find_element(By.ID, "dptRsStnCd")
                for option in dpt_station_select.find_elements(By.TAG_NAME, "option"):
                    if option.text.strip() == start_station:
                        option.click()
                        print(f"[{now_str()}] 출발역 '{start_station}' 선택됨")
                        break
                # '도착역' 셀렉트 박스에서 '광주송정'을 선택합니다.
                arv_station_select = driver.find_element(By.ID, "arvRsStnCd")
                for option in arv_station_select.find_elements(By.TAG_NAME, "option"):
                    if option.text.strip() == end_station:
                        option.click()
                        print(f"[{now_str()}] 도착역 '{end_station}' 선택됨")
                        break
                # 출발일자 입력 필드(dptDt)의 값을 2025.11.28로 변경합니다.
                dpt_date_input = driver.find_element(By.NAME, "dptDt")
                driver.execute_script("arguments[0].removeAttribute('readonly')", dpt_date_input)
                dpt_date_input.clear()
                dpt_date_input.send_keys(target_date)
                print(f"[{now_str()}] 출발일자 {target_date}로 변경 완료")
                # '<span>간편조회하기</span>'를 클릭합니다.
                # '출발시각' 셀렉트 박스에서 min_time에 가장 가까운 옵션을 선택합니다.
                dpt_time_select = driver.find_element(By.ID, "dptTm")
                min_h, min_m = map(int, min_time.split(":"))
                min_total_minutes = min_h * 60 + min_m

                closest_option = None
                closest_diff = None

                for option in dpt_time_select.find_elements(By.TAG_NAME, "option"):
                    # option.value 예: "140000"
                    value = option.get_attribute("value")
                    if len(value) >= 4:
                        opt_h = int(value[:2])
                        opt_m = int(value[2:4])
                        opt_total_minutes = opt_h * 60 + opt_m
                        # 옵션이 min_time보다 크거나 같고 가장 작은 값을 선택
                        if opt_total_minutes >= min_total_minutes:
                            diff = opt_total_minutes - min_total_minutes
                            if closest_diff is None or diff < closest_diff:
                                closest_option = option
                                closest_diff = diff

                # 만약 min_time과 같거나 큰 옵션이 없다면, 가장 마지막 옵션을 선택
                if closest_option is None:
                    all_options = dpt_time_select.find_elements(By.TAG_NAME, "option")
                    if all_options:
                        closest_option = all_options[-1]

                if closest_option is not None:
                    closest_option.click()
                    print(f"[{now_str()}] 출발시각 옵션 '{closest_option.text}' 선택됨")
                else:
                    print(f"[{now_str()}] 출발시각 옵션을 찾을 수 없습니다.")
                simple_search_span = driver.find_element(By.XPATH, "//span[text()='간편조회하기']")
                simple_search_span.click()
                print(f"[{now_str()}] '간편조회하기' 버튼 클릭 완료")

                
                time.sleep(wait_sec)
                # tbody element for the result rows
                tbody_selector = "#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody"
                tbody = driver.find_element(By.CSS_SELECTOR, tbody_selector)
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                # 예약이 될때까지 계속 새로고침 하면서 반복
                # 현재 페이지 주소값 저장 (현재 URL 얻기)
                예약_대기성공=2
                continue
            except Exception as e:
                print(f"[{now_str()}] '확인' 버튼(moveTicketList) 클릭에 실패했습니다:", e)

        if 예약_성공:
            print(f"[{now_str()}] 예약에 성공했습니다!")
            break

        else:
            random_refresh_time = random.randint(int(refresh_time/2), int(refresh_time/2 + refresh_time))
            print(f"[{now_str()}] 예약 가능한 항목이 없습니다. {random_refresh_time}초 후 새로고침합니다.")
            time.sleep(random_refresh_time)
            wait = WebDriverWait(driver, 10)

            # 1. 버튼이 보이도록 스크롤 (화면 "아래쪽"에 위치하게)
            search_top_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.inquery_btn"))
            )

            # 요소를 화면 하단 쪽에 맞춤 (true는 상단, false는 하단)
            driver.execute_script("arguments[0].scrollIntoView(false);", search_top_input)

            # 필요하면 조금만 더 올리거나 내릴 수도 있음
            # driver.execute_script("window.scrollBy(0, -50);")  # 위로 50px
            # driver.execute_script("window.scrollBy(0, 50);")   # 아래로 50px

            try:
                # 2. 일반 클릭 시도
                search_top_input = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input.inquery_btn"))
                )
                search_top_input.click()

            except ElementClickInterceptedException:
                # 3. 여전히 login_wrap이 가리면, JS로 강제 클릭
                search_top_input = driver.find_element(By.CSS_SELECTOR, "input.inquery_btn")
                driver.execute_script("arguments[0].click();", search_top_input)




    if 예약_대기성공==1:
        try:
            # "예" 라디오 버튼 찾기 (id="smsY")
            sms_yes_radio = driver.find_element(By.ID, "smsY")
            if not sms_yes_radio.is_selected():
                driver.execute_script("arguments[0].scrollIntoView(true);", sms_yes_radio)
                try:
                    sms_yes_radio.click()
                except Exception as radio_e:
                    print(f"[{now_str()}] smsY 라디오버튼 클릭 실패, JS로 재시도합니다.")
                    driver.execute_script("arguments[0].click();", sms_yes_radio)
            print(f"[{now_str()}] 문자 발송 여부(예)에 체크했습니다.")
        except Exception as e:
            print(f"[{now_str()}] smsY 라디오버튼을 찾을 수 없습니다:", e)
        try:
            # "다른 좌석 유형" 라디오 버튼 찾기 (id="diffSeatY")
            diff_seat_radio = driver.find_element(By.ID, "diffSeatY")
            if not diff_seat_radio.is_selected():
                driver.execute_script("arguments[0].scrollIntoView(true);", diff_seat_radio)
                try:
                    diff_seat_radio.click()
                except Exception as diff_seat_e:
                    print(f"[{now_str()}] diffSeatY 라디오버튼 클릭 실패, JS로 재시도합니다.")
                    driver.execute_script("arguments[0].click();", diff_seat_radio)
            print(f"[{now_str()}] 다른 좌석 유형(체크)에 체크했습니다.")
        except Exception as e:
            print(f"[{now_str()}] diffSeatY 라디오버튼을 찾을 수 없습니다:", e)
        try:
            # "확인" 버튼 찾기 (id="moveTicketList")
            confirm_btn = driver.find_element(By.ID, "moveTicketList")
            driver.execute_script("arguments[0].scrollIntoView(true);", confirm_btn)
            confirm_btn.click()
            print(f"[{now_str()}] '확인' 버튼(moveTicketList)을 클릭했습니다.")
        except Exception as e:
            print(f"[{now_str()}] '확인' 버튼(moveTicketList) 클릭에 실패했습니다:", e)
    time.sleep(1)
    try:
        # 결제하기 버튼이 나타날 때까지 대기 후 클릭
        pay_btn = WebDriverWait(driver, wait_sec).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#list-form > fieldset > div.tal_c > a.btn_large.btn_blue_dark.val_m.mgr10 > span"))
        )
        print(f"[{now_str()}] 결제하기 버튼 텍스트: {pay_btn.text}")
        if pay_btn.text.strip() == "결제하기":
            pay_btn.click()
            print(f"[{now_str()}] 결제하기 버튼을 클릭했습니다.")
        else:
            print(f"[{now_str()}] 결제하기 버튼의 텍스트가 일치하지 않습니다.")
    except Exception as e:
        print(f"[{now_str()}] 결제하기 버튼을 찾을 수 없습니다:", e)

    try:
        # Tab container와 chTab2 탭 모두 명시적으로 대기
        tab_ul = WebDriverWait(driver, wait_sec).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#select-form > fieldset > div.tab.tab4.subtab > ul"))
        )
        print(f"[{now_str()}] Tab UL found.")
        ch_tab2 = WebDriverWait(tab_ul, wait_sec).until(
            lambda ul: ul.find_element(By.CSS_SELECTOR, "#chTab2")
        )
        print(f"[{now_str()}] chTab2 element found.")
        WebDriverWait(tab_ul, wait_sec).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#chTab2"))
        )
        ch_tab2.click()
        print(f"[{now_str()}] 간편결제 clicked.")
    except Exception as e:
        print(f"[{now_str()}] 간편결제 선택 또는 클릭에 실패했습니다:", e)

    try:
        # Pay section table tr > td > div container 대기
        container_div = WebDriverWait(driver, wait_sec).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#settle_payco > div.tbl_wrap.tbl3 > table > tbody > tr > td > div"))
        )
        # radio button 명시적으로 대기
        kakao_radio = WebDriverWait(container_div, wait_sec).until(
            lambda d: d.find_element(By.ID, "kakaoPay")
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", kakao_radio)
        if not kakao_radio.is_selected():
            try:
                WebDriverWait(driver, wait_sec).until(EC.element_to_be_clickable((By.ID, "kakaoPay")))
                kakao_radio.click()
            except Exception as click_e:
                print(f"[{now_str()}] 카카오페이 라디오버튼 클릭이 직접적으로 인터셉트되었습니다. 자바스크립트로 클릭을 시도합니다.")
                driver.execute_script("arguments[0].click();", kakao_radio)
        print(f"[{now_str()}] 카카오페이 라디오버튼을 선택했습니다.")
    except Exception as e:
        print(f"[{now_str()}] 카카오페이 라디오버튼 선택 실패:", e)

    try:
        # requestIssue2 버튼이 나타나고 클릭 가능할 때까지 대기 후 클릭
        request_issue2_btn = WebDriverWait(driver, wait_sec).until(
            EC.element_to_be_clickable((By.ID, "requestIssue2"))
        )
        request_issue2_btn.click()
        print(f"[{now_str()}] 'requestIssue2' 버튼을 클릭했습니다.")
    except Exception as e:
        print(f"[{now_str()}] 'requestIssue2' 버튼 클릭에 실패했습니다:", e)
    # 카카오 페이 창 전환
    try:
        WebDriverWait(driver, wait_sec).until(lambda d: len(d.window_handles) > 1)
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[1])
    except Exception as e:
        print(f"[{now_str()}] 카카오페이 결제창으로 창 전환 실패:", e)


    # 카톡결제 탭 클릭
    try:
        # Wait until the 카톡결제 tab is present
        WebDriverWait(driver, wait_sec).until(
            EC.presence_of_element_located((By.ID, "카톡결제"))
        )
        katalk_tab = driver.find_element(By.ID, "카톡결제")
        driver.execute_script("arguments[0].scrollIntoView(true);", katalk_tab)
        katalk_tab.click()
        print(f"[{now_str()}] 카톡결제 탭을 클릭했습니다.")
    except Exception as e:
        print(f"[{now_str()}] 카톡결제 탭 클릭 실패:", e)
    # 휴대폰번호 입력
    WebDriverWait(driver, wait_sec).until(
        EC.presence_of_element_located((By.ID, "phoneNumber"))
    )
    phone_input = driver.find_element(By.ID, "phoneNumber")
    time.sleep(1)
    phone_input.send_keys(kakao_phone_number)
    print(f"[{now_str()}] 휴대폰번호를 입력했습니다.")

    # 생년월일(6자리) 입력
    WebDriverWait(driver, wait_sec).until(
        EC.presence_of_element_located((By.ID, "dateOfBirth"))
    )
    dob_input = driver.find_element(By.ID, "dateOfBirth")
    time.sleep(1)
    dob_input.send_keys(kakao_birth_date)
    print(f"[{now_str()}] 생년월일(6자리)를 입력했습니다.")
    # "결제요청" 버튼 클릭 (class: kp-m-button large primary _request-button_1y3vn_18)
    try:
        WebDriverWait(driver, wait_sec).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'kp-m-button') and contains(@class, 'primary') and .//p[text()='결제요청']]"))
        )
        kp_pay_btn = driver.find_element(
            By.XPATH, "//button[contains(@class, 'kp-m-button') and contains(@class, 'primary') and .//p[text()='결제요청']]"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", kp_pay_btn)
        kp_pay_btn.click()
        print(f"[{now_str()}] '결제요청' 버튼을 클릭했습니다.")
    except Exception as e:
        print(f"[{now_str()}] '결제요청' 버튼 클릭에 실패했습니다:", e)


finally:
    driver.quit()
