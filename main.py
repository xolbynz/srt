#1892761406
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    print(f"config.yaml 파일을 찾을 수 없습니다: {e}")
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
refresh_time = 120
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
    # '출발역' 셀렉트 박스에서 '수서'를 선택합니다.
    dpt_station_select = driver.find_element(By.ID, "dptRsStnCd")
    for option in dpt_station_select.find_elements(By.TAG_NAME, "option"):
        if option.text.strip() == start_station:
            option.click()
            print(f"출발역 '{start_station}' 선택됨")
            break
    # '도착역' 셀렉트 박스에서 '광주송정'을 선택합니다.
    arv_station_select = driver.find_element(By.ID, "arvRsStnCd")
    for option in arv_station_select.find_elements(By.TAG_NAME, "option"):
        if option.text.strip() == end_station:
            option.click()
            print(f"도착역 '{end_station}' 선택됨")
            break
    # 출발일자 입력 필드(dptDt)의 값을 2025.11.28로 변경합니다.
    dpt_date_input = driver.find_element(By.NAME, "dptDt")
    driver.execute_script("arguments[0].removeAttribute('readonly')", dpt_date_input)
    dpt_date_input.clear()
    dpt_date_input.send_keys(target_date)
    print(f"출발일자 {target_date}로 변경 완료")
    # '<span>간편조회하기</span>'를 클릭합니다.
    simple_search_span = driver.find_element(By.XPATH, "//span[text()='간편조회하기']")
    simple_search_span.click()
    print("'간편조회하기' 버튼 클릭 완료")

    
    time.sleep(wait_sec)
    # tbody element for the result rows
    tbody_selector = "#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody"
    tbody = driver.find_element(By.CSS_SELECTOR, tbody_selector)
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    # 예약이 될때까지 계속 새로고침 하면서 반복
    while True:
        tbody_selector = "#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody"
        try:
            tbody = driver.find_element(By.CSS_SELECTOR, tbody_selector)
            rows = tbody.find_elements(By.TAG_NAME, "tr")
        except Exception as e:
            print("tbody를 찾을 수 없습니다. 1초 후 새로고침.")
            time.sleep(1)
            driver.refresh()
            continue

        예약_성공 = False
        for i, row in enumerate(rows):
            index = i + 1
            # td[4] div & em
            try:
                td4_div = row.find_element(By.CSS_SELECTOR, f"td:nth-child(4) > div")
                print(f"Row {index} td4 div: {td4_div.text}")
            except Exception as e:
                print(f"Row {index} td4 div not found")

            try:
                td4_em = row.find_element(By.CSS_SELECTOR, f"td:nth-child(4) > em")
                print(f"Row {index} td4 em: {td4_em.text}")
                td4_time = td4_em.text.strip()
                td4_h, td4_m = map(int, td4_time.split(":"))
                min_h, min_m = map(int, min_time.split(":"))
                max_h, max_m = map(int, max_time.split(":"))
                td4_minutes = td4_h * 60 + td4_m
                min_minutes = min_h * 60 + min_m
                max_minutes = max_h * 60 + max_m
                if td4_minutes < min_minutes:
                    print(f"Row {index} td4 em 시간({td4_time})이 최소 시간({min_time}) 미만이므로 건너뜀.")
                    continue
                if td4_minutes > max_minutes:
                    print(f"Row {index} td4 em 시간({td4_time})이 최대 시간({max_time}) 초과이므로 건너뜀.")
                    continue
                

            except Exception as e:
                print(f"Row {index} td4 em not found")

            # # td[5] div & em
            # try:
            #     td5_div = row.find_element(By.CSS_SELECTOR, f"td:nth-child(5) > div")
            #     print(f"Row {index} td5 div: {td5_div.text}")
            # except Exception as e:
            #     print(f"Row {index} td5 div not found")

            # try:
            #     td5_em = row.find_element(By.CSS_SELECTOR, f"td:nth-child(5) > em")
            #     print(f"Row {index} td5 em: {td5_em.text}")
            # except Exception as e:
            #     print(f"Row {index} td5 em not found")

            # try:
            #     td6_span = row.find_element(By.CSS_SELECTOR, f"td:nth-child(6) > a > span")
            #     print(f"특실 {td6_span.text}")
            #     if td6_span.text.strip() == "예약하기":
            #         td6_span.click()
            #         예약_성공 = True
            #         break
            # except Exception as e:
            #     print(f"Row {index} td6 span not found")


            try:
                td7_span = row.find_element(By.CSS_SELECTOR, f"td:nth-child(7) > a > span")
                print(f"일반실 {td7_span.text}")
                if td7_span.text.strip() == "예약하기":
                    td7_span.click()
                    예약_성공 = True
                    break
            except Exception as e:
                print(f"Row {index} td7 span not found")

            # td[8] > a > span
            try:
                td8_span = row.find_element(By.CSS_SELECTOR, f"td:nth-child(8) > a > span")
                print(f"예약대기 {td8_span.text}")
                if td8_span.text.strip() == "예약하기":
                    td8_span.click()
                    예약_성공 = True
                    break
            except Exception as e:
                print(f"Row {index} td8 span not found")



        if 예약_성공:
            print("예약에 성공했습니다!")
            break
        else:
            print(f"예약 가능한 항목이 없습니다. {refresh_time}초 후 새로고침합니다.")
            time.sleep(refresh_time)
            driver.refresh()
    
    time.sleep(1)
    try:
        pay_btn = driver.find_element(By.CSS_SELECTOR, "#list-form > fieldset > div.tal_c > a.btn_large.btn_blue_dark.val_m.mgr10 > span")
        print(f"결제하기 버튼 텍스트: {pay_btn.text}")
        if pay_btn.text.strip() == "결제하기":
            pay_btn.click()
            print("결제하기 버튼을 클릭했습니다.")
        else:
            print("결제하기 버튼의 텍스트가 일치하지 않습니다.")
    except Exception as e:
        print("결제하기 버튼을 찾을 수 없습니다:", e)
    try:
        # Find the tab container
        tab_ul = driver.find_element(By.CSS_SELECTOR, "#select-form > fieldset > div.tab.tab4.subtab > ul")
        print("Tab UL found.")
        
        # Find the tab with id 'chTab2'
        ch_tab2 = tab_ul.find_element(By.CSS_SELECTOR, "#chTab2")
        print("chTab2 element found.")
        
        # Click the tab
        ch_tab2.click()
        print("chTab2 clicked.")
    except Exception as e:
        print("chTab2 선택 또는 클릭에 실패했습니다:", e)
    try:
        # Find the containing div under the specific pay section
        container_div = driver.find_element(By.CSS_SELECTOR, "#settle_payco > div.tbl_wrap.tbl3 > table > tbody > tr > td > div")
        # Within this container, find the radio element for 카카오페이
        kakao_radio = container_div.find_element(By.ID, "kakaoPay")
        driver.execute_script("arguments[0].scrollIntoView(true);", kakao_radio)
        if not kakao_radio.is_selected():
            try:
                kakao_radio.click()
            except Exception as click_e:
                print("카카오페이 라디오버튼 클릭이 직접적으로 인터셉트되었습니다. 자바스크립트로 클릭을 시도합니다.")
                driver.execute_script("arguments[0].click();", kakao_radio)
        print("카카오페이 라디오버튼을 선택했습니다.")
    except Exception as e:
        print("카카오페이 라디오버튼 선택 실패:", e)

    try:
        # Find the element with id 'requestIssue2'
        request_issue2_btn = driver.find_element(By.ID, "requestIssue2")
        request_issue2_btn.click()
        print("'requestIssue2' 버튼을 클릭했습니다.")
    except Exception as e:
        print("'requestIssue2' 버튼 클릭에 실패했습니다:", e)
    # 카카오 페이 창 전환
    # 새 창이나 탭이 열릴 때까지 기다림
    WebDriverWait(driver, wait_sec).until(lambda d: len(d.window_handles) > 1)
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[1])


    # 카톡결제 탭 클릭
    try:
        # Wait until the 카톡결제 tab is present
        WebDriverWait(driver, wait_sec).until(
            EC.presence_of_element_located((By.ID, "카톡결제"))
        )
        katalk_tab = driver.find_element(By.ID, "카톡결제")
        driver.execute_script("arguments[0].scrollIntoView(true);", katalk_tab)
        katalk_tab.click()
        print("카톡결제 탭을 클릭했습니다.")
    except Exception as e:
        print("카톡결제 탭 클릭 실패:", e)
    # 휴대폰번호 입력
    WebDriverWait(driver, wait_sec).until(
        EC.presence_of_element_located((By.ID, "phoneNumber"))
    )
    phone_input = driver.find_element(By.ID, "phoneNumber")
    time.sleep(1)
    phone_input.send_keys(kakao_phone_number)
    print("휴대폰번호를 입력했습니다.")

    # 생년월일(6자리) 입력
    WebDriverWait(driver, wait_sec).until(
        EC.presence_of_element_located((By.ID, "dateOfBirth"))
    )
    dob_input = driver.find_element(By.ID, "dateOfBirth")
    time.sleep(1)
    dob_input.send_keys(kakao_birth_date)
    print("생년월일(6자리)를 입력했습니다.")
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
        print("'결제요청' 버튼을 클릭했습니다.")
    except Exception as e:
        print("'결제요청' 버튼 클릭에 실패했습니다:", e)


finally:
    driver.quit()
