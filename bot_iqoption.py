# =======================================================
# 📡 IQ OPTION INDICATOR BRIDGE FOR BB 9, 1.5 SYSTEM
# =======================================================
import time

def check_indicator_signal(api, asset, timeframe=60):
    """
    ฟังก์ชันดึงค่าแท่งเทียนมาคำนวณเงื่อนไขลูกศร BB 9, 1.5 อัตโนมัติบนบอท Python
    """
    # ดึงข้อมูลแท่งเทียนย้อนหลัง 15 แท่งเพื่อความแม่นยำ
    candles = api.get_candles(asset, timeframe, 15, time.time())
    if not candles or len(candles) < 3:
        return None

    # แปลงข้อมูลแท่งเทียนย้อนหลัง (Index -1 คือแท่งปัจจุบันที่วิ่งอยู่, -2 คือแท่งที่เพิ่งปิดตัว)
    curr = candles[-1]
    prev = candles[-2]
    
    # คำนวณค่าเทคนิคอลแบบเดียวกับในสคริปต์กราฟ (BB 9, 1.5)
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(candles)
    df['basis'] = df['close'].rolling(window=9).mean()
    df['std'] = df['close'].rolling(window=9).std()
    df['upper'] = df['basis'] + (1.5 * df['std'])
    df['lower'] = df['basis'] - (1.5 * df['std'])
    
    # ตรวจสอบค่าแถวล่าสุด
    p_close, p_open, p_lower, p_upper = prev['close'], prev['open'], df['lower'].iloc[-2], df['upper'].iloc[-2]
    c_close, c_open, c_lower, c_upper = curr['close'], curr['open'], df['lower'].iloc[-1], df['upper'].iloc[-1]
    
    # [1] ตรวจสอบเงื่อนไขลูกศรเขียว (CALL)
    call_arrow = (p_close < p_open and p_close < p_lower) and \
                 (c_close > c_open and c_open < c_lower and c_close > c_lower)
                 
    # [2] ตรวจสอบเงื่อนไขลูกศรแดง (PUT)
    put_arrow = (p_close > p_open and p_close > p_upper) and \
                (c_close < c_open and c_open > c_upper and c_close < c_upper)
                
    if call_arrow:
        return "CALL"
    elif put_arrow:
        return "PUT"
    return None
