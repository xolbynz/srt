### config.yaml 만들어
```
id: "0000"
password: ""
kakao_phone_number: ""

min_time: "14:00"
max_time: "17:00"
target_date: "2025.12.03"  
start_station: "수서"
end_station: "광주송정"
kakao_birth_date: "0000"
refresh_time: 120
```












## 빌드해서 해볼래?
### 창문
```
pyinstaller --onefile --noconsole --name SRT_Macro srt_macro.py
```
### 맥도날드
```
pyinstaller --onefile --windowed --name SRT_Macro srt_macro.py
```