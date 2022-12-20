# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 18:22:31 2022

@author: hwlee
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
from random import randint

# =============================================================================
# USER INPUT
# =============================================================================
input_dep_stn = '수서'
input_arr_stn = '부산'

input_dep_date = '20221221' # 1개월 이내(YYYYMMDD)
input_dep_time = '16' # 00, 02, 14, 16 형식
input_num_of_trains = 3 # 검색 결과 상단에서부터 예약 가능 여부 확인할 기차 수

input_seat_class = '무관' # 특실, 일반실, 무관
input_seat_num = '기능추가예정' # 좌석수
input_seat_select = '수동선택' # 수동선택, 자동선택
want_standing_seat = True # 입석도 괜찮나요? True, False
want_queue = True # 예약 대기 원하나요? True, False

# =============================================================================
# %% AUTOMATIC EXECUTION
# =============================================================================

# 현재 크롬 버전에 맞게 ChromeDriver 자동 설치
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 로그인 페이지로 이동
driver.get('https://etk.srail.co.kr/cmc/01/selectLoginForm.do')
driver.implicitly_wait(15) # 페이지 다 뜰 때 까지 기다림

driver.find_element(By.ID, 'srchDvNm01').send_keys('2080926322') # 회원번호
driver.find_element(By.ID, 'hmpgPwdCphd01').send_keys('1q2w#E$R') # 비밀번호
driver.find_element(By.XPATH, '//*[@id="login-form"]/fieldset/div[1]/div[1]\
                    /div[2]/div/div[2]/input').click() # 확인버튼 (by full XPath)
driver.implicitly_wait(5)            

# 기차 조회 페이지로 이동
driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do')
driver.implicitly_wait(5)

# 출발지/도착지 입력
dep_stn = driver.find_element(By.ID, 'dptRsStnCdNm') # 출발지
dep_stn.clear() # default값 지우기
dep_stn.send_keys(input_dep_stn)

arr_stn = driver.find_element(By.ID, 'arvRsStnCdNm') # 도착지
arr_stn.clear()
arr_stn.send_keys(input_arr_stn)

# 출발날짜 입력
dep_date = driver.find_element(By.ID, 'dptDt') # 출발날짜
driver.execute_script("arguments[0].setAttribute('style','display: True;')"\
                      , dep_date) # 날짜 드롭다운 리스트 보이게
try:
    Select(dep_date).select_by_value(input_dep_date) # 출발날짜 선택
except: print('선택 불가능한 날짜입니다.')

# 출발시간 입력
dep_time = driver.find_element(By.ID, 'dptTm') # 출발시간
driver.execute_script("arguments[0].setAttribute('style','display: True;')"\
                      , dep_time)
Select(dep_time).select_by_visible_text(input_dep_time) # 출발시간 선택(by Visible Text)
driver.find_element(By.XPATH, "//input[@value='조회하기']").click() # 조회버튼
driver.implicitly_wait(5)
                                  
# 예약 정보 표시
print('기차를 조회합니다\n')
print('출발역:%s, 도착역:%s' %(input_dep_stn, input_arr_stn))
print('인원:%s, 등급:%s' %(input_seat_num, input_seat_class))
print('좌석선택:%s, 입석선택여부:%s' %(input_seat_select, want_standing_seat))
print('날짜:%s, 시간:%s시 이후' %(input_dep_date, input_dep_time))
print('%s개의 기차 중 예약' %input_num_of_trains)
print('예약 대기 사용:%s\n' %want_queue)

# =============================================================================
# %% 예매하기
# =============================================================================
# 예매 페이지로 이동
train_list = driver.find_elements(By.CSS_SELECTOR, '#result-form > fieldset >\
                                  div.tbl_wrap.th_thead > table > tbody > tr')
                                  
# 좌석 등급에 따라 index assigning
if input_seat_class == '특실': # td:nth-child(6) = 특실
    seat_class_num = 6
else: seat_class_num = 7 # 일반실 or 무관

# =============================================================================
# 기차 예매하기
is_reserved = False
counter = 0
while True:
    for i in range(1, input_num_of_trains + 1): # 검색 결과 상위 x개에 대해 loop
        # 좌석 등급 index에 따라 해당 버튼 text 추출    
        seat_class = driver.find_element(By.CSS_SELECTOR, f"#result-form >\
                                         fieldset > div.tbl_wrap.th_thead >\
                                         table > tbody > tr:nth-child({i}) >\
                                         td:nth-child(%s)" 
                                         %seat_class_num).text
        # 예약 대기 버튼 text 추출
        queue = driver.find_element(By.CSS_SELECTOR, f"#result-form >\
                                    fieldset > div.tbl_wrap.th_thead > table >\
                                    tbody > tr:nth-child({i}) >\
                                    td:nth-child(8)").text
        # 수동선택
        if input_seat_select == '수동선택':    
            if '예약하기' in seat_class:
                print('예약 가능')
                driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div/\
                                    div[3]/div[1]/form/fieldset/div[6]/table/\
                                    tbody/tr[{i}]/td[%s]/div/a/span" 
                                    %seat_class_num).click()
                is_reserved = True
                break

        # 자동선택
        elif input_seat_select == '자동선택':
            if want_standing_seat == True:           
                if ('예약하기' in seat_class) | ('입석+좌석' in seat_class):
                    print('예약 가능')
                    driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/\
                                        div/div[3]/div[1]/form/fieldset/\
                                        div[6]/table/tbody/tr[{i}]/td[%s]/a/\
                                        span" %seat_class_num).click()
                    is_reserved = True
                    break
                
            elif want_standing_seat == False:  
                if '예약하기' in seat_class:
                    print('예약 가능')
                    driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/\
                                        div/div[3]/div[1]/form/fieldset/\
                                        div[6]/table/tbody/tr[{i}]/td[%s]/a/\
                                        span" %seat_class_num).click()
                    is_reserved = True
                    break
                
        if want_queue == True:
            if "신청하기" in queue:
                print("예약 대기 완료")
                driver.find_element(By.CSS_SELECTOR, f"#result-form >\
                                    fieldset > div.tbl_wrap.th_thead >\
                                    table > tbody > tr:nth-child({i}) >\
                                    td:nth-child(8) > a").click()
                is_reserved = True
                break
                
        # 좌석등급 무관        
        if input_seat_class == '무관':
            
            if input_seat_select == '수동선택':    
                if '예약하기' in seat_class:
                    print('예약 가능')
                    driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/\
                                        div/div[3]/div[1]/form/fieldset/\
                                        div[6]/table/tbody/tr[{i}]/td[6]/div/\
                                        a/span").click()
                    is_reserved = True
                    break
                
            elif input_seat_select == '자동선택':
                if want_standing_seat == True:           
                    if ('예약하기' in seat_class) | ('입석+좌석' in seat_class):
                        print('예약 가능')
                        driver.find_element(By.XPATH, f"/html/body/div[1]/\
                                            div[4]/div/div[3]/div[1]/form/\
                                            fieldset/div[6]/table/tbody/\
                                            tr[{i}]/td[6]/a/span" 
                                            %seat_class_num).click()
                        is_reserved = True
                        break
                    
                elif want_standing_seat == False:  
                    if '예약하기' in seat_class:
                        print('예약 가능')
                        driver.find_element(By.XPATH, f"/html/body/div[1]/\
                                            div[4]/div/div[3]/div[1]/form/\
                                            fieldset/div[6]/table/tbody/\
                                            tr[{i}]/td[6]/a/span" 
                                            %seat_class_num).click()
                        is_reserved = True
                        break
# =============================================================================

    if not is_reserved:
        time.sleep(randint(2, 4)) # 2~4초 랜덤으로 기다리기
        submit = driver.find_element(By.XPATH, "//input[@value='조회하기']") # 다시 조회하기
        driver.execute_script("arguments[0].click();", submit)
        print('새로고침 %s회' %counter)
        counter += 1
        driver.implicitly_wait(8)
        time.sleep(0.5)
        
    else: break

