import sys
import tkinter as tk
from tkinter import ttk
from tkinter import font
from datetime import datetime, timedelta
import pytz  # zoneinfo 대신 pytz 사용

# Windows 환경에서 UTF-8 설정
if sys.platform.startswith("win") and sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")

class CustomButton(tk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(
            background='#2196F3',  # 파란색 배경
            foreground='white',     # 흰색 텍스트
            font=('맑은 고딕', 10, 'bold'),
            relief='raised',        # 입체적인 효과
            borderwidth=0,
            padx=20,
            pady=10,
            cursor='hand2'         # 마우스 오버시 손가락 커서
        )
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, e):
        self.config(background='#1976D2')  # 더 진한 파란색

    def on_leave(self, e):
        self.config(background='#2196F3')  # 원래 파란색

def calculate_dates(work_days):
    # 한국 시간으로 현재 날짜 가져오기
    kr_tz = pytz.timezone('Asia/Seoul')
    today = datetime.now(kr_tz)
    
    # 시작일을 내일로 설정
    start_date = today + timedelta(days=1)
    # 종료일 계산 (시작일 포함하여 work_days만큼)
    end_date = start_date + timedelta(days=int(work_days)-1)
    
    return start_date, end_date

def calculate_cost(traffic_requests, storage_requests, traffic_cost_per_request, storage_cost_per_request, work_days, vat_rate=10):
    # 날짜 계산
    start_date, end_date = calculate_dates(work_days)
    date_range = f"{start_date.strftime('%m-%d')} ~ {end_date.strftime('%m-%d')}"

    # 개별 비용 계산
    traffic_cost = traffic_requests * traffic_cost_per_request
    storage_cost = storage_requests * storage_cost_per_request
    daily_total = traffic_cost + storage_cost
    
    # 총 비용 계산 (작업일수 반영)
    total = daily_total * int(work_days)
    total_with_vat = total * (1 + vat_rate/100)

    # 결과 텍스트 업데이트
    result_text.config(state='normal')
    result_text.delete(1.0, tk.END)
    
    # 작업 기간 표시 (내일부터 계산)
    result_text.insert(tk.END, f"작업 기간: {date_range}\n\n")
    
    # 일반 텍스트 삽입
    if traffic_requests > 0:
        result_text.insert(tk.END, f"트래픽 비용: {traffic_cost:,} 원\n")
    if storage_requests > 0:
        result_text.insert(tk.END, f"저장하기 비용: {storage_cost:,} 원\n")
    if traffic_requests > 0 or storage_requests > 0:
        result_text.insert(tk.END, f"일 소진 비용: {daily_total:,} 원\n\n")
        result_text.insert(tk.END, f"{work_days}일 작업 총 비용 (부가세 미포함): {total:,.0f} 원\n")
        result_text.insert(tk.END, f"{work_days}일 작업 총 비용 (부가세 포함): {total_with_vat:,.0f} 원", 'bold_blue')
        result_text.insert(tk.END, "\n\n")
        result_text.insert(tk.END, "주식회사 다인기획\n")
        result_text.insert(tk.END, "국민은행: 900901-01-688580")
    
    result_text.config(state='disabled')

def on_calculate():
    try:
        # 빈 입력값 처리
        work_days_str = entry_work_days.get().strip()
        traffic_str = entry_traffic.get().strip()
        storage_str = entry_storage.get().strip()
        traffic_cost_str = entry_traffic_cost.get().strip()
        storage_cost_str = entry_storage_cost.get().strip()
        
        # 작업일수 검증
        if not work_days_str:
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "❌ 작업 일수를 입력해주세요!")
            result_text.config(state='disabled')
            return

        # 건수와 단가 검증
        if not any([traffic_str, storage_str]):
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "❌ 최소한 하나의 건수를 입력해주세요!")
            result_text.config(state='disabled')
            return
            
        if not traffic_cost_str or not storage_cost_str:
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "❌ 단가를 모두 입력해주세요!")
            result_text.config(state='disabled')
            return

        # 값 변환
        work_days = int(work_days_str)
        traffic_requests = int(traffic_str) if traffic_str else 0
        storage_requests = int(storage_str) if storage_str else 0
        traffic_cost_per_request = int(traffic_cost_str)
        storage_cost_per_request = int(storage_cost_str)

        # 유효성 검사
        if work_days <= 0:
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "❌ 작업 일수는 1일 이상이어야 합니다.")
            result_text.config(state='disabled')
            return

        if any(x < 0 for x in [traffic_requests, storage_requests, traffic_cost_per_request, storage_cost_per_request]):
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "❌ 음수는 입력할 수 없습니다.")
            result_text.config(state='disabled')
        else:
            calculate_cost(traffic_requests, storage_requests, traffic_cost_per_request, storage_cost_per_request, work_days)
    except ValueError:
        result_text.config(state='normal')
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "❌ 숫자만 입력해주세요!")
        result_text.config(state='disabled')
    except Exception as e:
        result_text.config(state='normal')
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"❌ 예기치 않은 오류가 발생했습니다: {e}")
        result_text.config(state='disabled')

# GUI 설정
root = tk.Tk()
root.title("(c) 2025. 다인기획 Corp. All rights reserved.")
root.geometry("500x800")  # 전체 창 높이를 800으로 증가
root.configure(bg='#FAFAFA')

# 스타일 설정
style = ttk.Style()
style.theme_use('clam')  # 더 현대적인 테마 사용
style.configure('TFrame', background='#FAFAFA')
style.configure('TLabel', 
    background='#FAFAFA', 
    font=('맑은 고딕', 10),
    padding=5
)
style.configure('Title.TLabel',
    background='#FAFAFA',
    font=('맑은 고딕', 18, 'bold'),
    foreground='#1976D2'  # 진한 파란색
)
style.configure('TEntry', 
    font=('맑은 고딕', 10),
    fieldbackground='white',
    borderwidth=2
)

# 메인 프레임
main_frame = ttk.Frame(root, padding="30")
main_frame.pack(fill=tk.BOTH, expand=True)

# 제목
title_label = ttk.Label(main_frame, text="견적서", style='Title.TLabel')
title_label.pack(pady=(0, 30))

# 입력 프레임 (그림자 효과를 위한 추가 프레임)
input_outer_frame = tk.Frame(main_frame, bg='#E0E0E0', bd=1)
input_outer_frame.pack(fill=tk.X, padx=2, pady=2)

input_frame = tk.Frame(input_outer_frame, bg='white', bd=1)
input_frame.pack(fill=tk.X, padx=1, pady=1)

# 트래픽 입력
traffic_frame = ttk.Frame(input_frame)
traffic_frame.pack(fill=tk.X, padx=20, pady=10)
ttk.Label(traffic_frame, text="일 트래픽:", background='white').pack(side=tk.LEFT)
entry_traffic = ttk.Entry(traffic_frame)
entry_traffic.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))

# 트래픽 단가 입력
traffic_cost_frame = ttk.Frame(input_frame)
traffic_cost_frame.pack(fill=tk.X, padx=20, pady=10)
ttk.Label(traffic_cost_frame, text="트래픽 단가:", background='white').pack(side=tk.LEFT)
entry_traffic_cost = ttk.Entry(traffic_cost_frame)
entry_traffic_cost.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
entry_traffic_cost.insert(0, "50")  # 기본값 설정

# 저장하기 입력
storage_frame = ttk.Frame(input_frame)
storage_frame.pack(fill=tk.X, padx=20, pady=10)
ttk.Label(storage_frame, text="일 저장하기:", background='white').pack(side=tk.LEFT)
entry_storage = ttk.Entry(storage_frame)
entry_storage.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))

# 저장하기 단가 입력
storage_cost_frame = ttk.Frame(input_frame)
storage_cost_frame.pack(fill=tk.X, padx=20, pady=10)
ttk.Label(storage_cost_frame, text="저장하기 단가:", background='white').pack(side=tk.LEFT)
entry_storage_cost = ttk.Entry(storage_cost_frame)
entry_storage_cost.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
entry_storage_cost.insert(0, "50")  # 기본값 설정

# 작업 일수 입력
work_days_frame = ttk.Frame(input_frame)
work_days_frame.pack(fill=tk.X, padx=20, pady=10)
ttk.Label(work_days_frame, text="작업 일수:", background='white').pack(side=tk.LEFT)
entry_work_days = ttk.Entry(work_days_frame)
entry_work_days.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
entry_work_days.insert(0, "7")  # 기본값 7일로 설정

# 계산 버튼
calculate_button = CustomButton(main_frame, text="계산하기", command=on_calculate)
calculate_button.pack(pady=20)

# 결과 표시 영역
result_outer_frame = tk.Frame(main_frame, bg='#E0E0E0', bd=1)
result_outer_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

result_frame = tk.Frame(result_outer_frame, bg='white', bd=1)
result_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

result_text = tk.Text(result_frame, 
    height=15,  # 높이를 15로 증가
    font=('맑은 고딕', 11),
    bg='white',
    bd=0,
    padx=20,  # 좌우 여백 증가
    pady=20   # 상하 여백 증가
)
result_text.pack(fill=tk.BOTH, expand=True)
result_text.tag_configure('bold_blue', 
    foreground='#1976D2',
    font=('맑은 고딕', 11, 'bold')
)
result_text.config(state='disabled')

# Enter 키 바인딩
root.bind('<Return>', lambda event: on_calculate())

# 윈도우 중앙 정렬
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

root.mainloop()
