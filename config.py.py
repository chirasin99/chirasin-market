 import time, sys, threading, datetime, requests
import pandas as pd
import numpy as np
from iqoptionapi.stable_api import IQ_Option
from colorama import init, Fore, Style

init(autoreset=True)

# ====================================================================================
# 🎛️ CONTROL PANEL - FLUSH SINGLE-ROW ENGINE v236.1 (FINAL)
# ====================================================================================
EMAIL = "chirasin33334444@gmail.com"
PASSWORD = "n0923866522n"
MODE = "PRACTICE"                     # "PRACTICE" = Demo Account / "REAL" = Real Account

BOT_SWITCH = "ON"
BASE_ASSETS = ["EURUSD", "EURJPY", "GBPUSD"]     

BASE_AMOUNT = 1.0                   
MULTIPLIER = 2.3                    
MAX_STEPS = 10                      
MAX_ORDERS_PER_TREND = 99            

working_timeframe = 60  
trade_expiry = 1        

BB_PERIOD = 20                      
BB_STD = 2.0                        
BUFFER_PIPS = 0.00000               

TAKE_PROFIT = 15.0                  
STOP_LOSS = -30.0                   
LINE_TOKEN = "YOUR_LINE_TOKEN_HERE"  # 🎯 Paste your LINE Notify Token here
# ====================================================================================

GREEN_BG, RED_BG, RESET = "\033[42m\033[30m\033[1m", "\033[41m\033[37m", "\033[0m"
GREEN_TEXT, RED_TEXT, YELLOW_TEXT = "\033[1;32m", "\033[1;31m", "\033[1;33m"

net_profit_loss, win_counter, loss_counter, bot_running_flag = 0.0, 0, 0, True
lock = threading.Lock()

asset_states = {
    "EURUSD-OTC": {"current_amount": BASE_AMOUNT, "current_step": 0, "last_trigger_bar_time": 0, "trend_order_counter": 0, "trend_locked": False},
    "EURJPY-OTC": {"current_amount": BASE_AMOUNT, "current_step": 0, "last_trigger_bar_time": 0, "trend_order_counter": 0, "trend_locked": False},
    "GBPUSD-OTC": {"current_amount": BASE_AMOUNT, "current_step": 0, "last_trigger_bar_time": 0, "trend_order_counter": 0, "trend_locked": False}
}

def send_line_notification(message):
    if not LINE_TOKEN or LINE_TOKEN.strip() == "" or "YOUR_" in LINE_TOKEN: return
    url = "https://line.me"
    try: threading.Thread(target=requests.post, args=(url,), kwargs={"headers": {"Authorization": f"Bearer {LINE_TOKEN}"}, "data": {"message": message}, "timeout": 5}, daemon=True).start()
    except: pass

def process_single_row_output(asset, win_status, round_net, trade_amount, current_step_at_trade):
    global net_profit_loss, win_counter, loss_counter, bot_running_flag
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    pnl_color = GREEN_TEXT if net_profit_loss >= 0 else RED_TEXT
    pnl_sign = "+" if net_profit_loss > 0 else ""
    
    # ดันล้างแถวตัววิ่งออกไปก่อนพิมพ์ดีดผลลัพธ์ไม้จริง
    sys.stdout.write("\r" + " " * 130 + "\r")
    sys.stdout.flush()
    
    if win_status == "win":
        output_str = f"🏁 [{now_str}] [ NET PnL: {pnl_color}{pnl_sign}${net_profit_loss:.2f}{RESET} ] {GREEN_BG} WIN! {RESET} {asset} (+$ {round_net:.2f}) | Step {current_step_at_trade} [W:{win_counter}/L:{loss_counter}]"
    else:
        output_str = f"🏁 [{now_str}] [ NET PnL: {pnl_color}{pnl_sign}${net_profit_loss:.2f}{RESET} ] {RED_BG} LOSS! {RESET} {asset} (-$ {trade_amount:.2f}) | Step {current_step_at_trade} [W:{win_counter}/L:{loss_counter}]"
    
    print(output_str)
    send_line_notification(f"\n[{now_str}] PnL: {pnl_sign}${net_profit_loss:.2f}\n{'🟢 WIN!' if win_status == 'win' else '🔴 LOSS!'} {asset} ({pnl_sign}${round_net:.2f})")

    if net_profit_loss >= TAKE_PROFIT or net_profit_loss <= STOP_LOSS:
        bot_running_flag = False
        msg = f"\n🎉 [TARGET MET] Final Portfolio PnL: {pnl_sign}${net_profit_loss:.2f}" if net_profit_loss >= TAKE_PROFIT else f"\n🛑 [STOP MET] Final Portfolio PnL: ${net_profit_loss:.2f}"
        print(f"{(Fore.GREEN if net_profit_loss >= TAKE_PROFIT else Fore.RED)}{msg}{Style.RESET_ALL}"); send_line_notification(msg)

def check_past_order_result_async(asset, order_id, trade_amount, current_step_at_trade):
    global net_profit_loss, win_counter, loss_counter
    time.sleep(60)
    win_status, round_net = "loose", -trade_amount
    for _ in range(15):
        try:
            history = API.get_option_open_by_other_pc()
            if history and str(order_id) in str(history):
                for op_id, op_data in history.items():
                    if str(op_id) == str(order_id):
                        if op_data.get("win", "loose") == "win":
                            win_status = "win"
                            round_net = round(float(op_data.get("payout", 0)) - trade_amount, 2)
                            if round_net <= 0: round_net = round(trade_amount * 0.82, 2)
                        break
                break
        except: pass
        time.sleep(1)
        
    with lock:
        if win_status == "win":
            net_profit_loss += round_net; win_counter += 1
            asset_states[asset]["current_amount"], asset_states[asset]["current_step"] = BASE_AMOUNT, 0
        else:
            round_net = round(-trade_amount, 2)
            net_profit_loss += round_net; loss_counter += 1
            asset_states[asset]["current_step"] = current_step_at_trade + 1
            if asset_states[asset]["current_step"] < MAX_STEPS: asset_states[asset]["current_amount"] = BASE_AMOUNT * (MULTIPLIER ** asset_states[asset]["current_step"])
            else: asset_states[asset]["current_amount"], asset_states[asset]["current_step"] = BASE_AMOUNT, 0
        asset_states[asset]["trend_order_counter"], asset_states[asset]["trend_locked"] = 0, False
        process_single_row_output(asset, win_status, round_net, trade_amount, current_step_at_trade)

def scan_signal_engine(asset):
    if not bot_running_flag: return
    try:
        candles = API.get_candles(asset, working_timeframe, 40, int(time.time()))
        if candles is None or not isinstance(candles, list) or len(candles) < 25: return
    except: return
    df = pd.DataFrame(candles)
    if 'max' in df.columns: df.rename(columns={'max': 'high'}, inplace=True)
    if 'min' in df.columns: df.rename(columns={'min': 'low'}, inplace=True)
    if 'close' not in df.columns: return
    df['basis'] = df['close'].rolling(window=BB_PERIOD).mean()
    df['std'] = df['close'].rolling(window=BB_PERIOD).std(ddof=1)
    df['upper_band'] = df['basis'] + (BB_STD * df['std'])
    df['lower_band'] = df['basis'] - (BB_STD * df['std'])
    signal_bar = df.iloc[-2]; signal_bar_time = signal_bar['from']
    c_open, c_close, c_high, c_low, c_upper, c_lower = float(signal_bar['open']), float(signal_bar['close']), float(signal_bar['high']), float(signal_bar['low']), float(signal_bar['upper_band']), float(signal_bar['lower_band'])
    if c_low > c_lower and c_high < c_upper: asset_states[asset]["trend_order_counter"], asset_states[asset]["trend_locked"] = 0, False
    buy_signal = (c_close > c_open) and (c_close >= c_upper)
    sell_signal = (c_close < c_open) and (c_close <= c_lower)
    action = "call" if buy_signal else ("put" if sell_signal else None)
    if action is not None and signal_bar_time != asset_states[asset]["last_trigger_bar_time"]:
        if MAX_ORDERS_PER_TREND > 0 and asset_states[asset]["trend_order_counter"] >= MAX_ORDERS_PER_TREND: asset_states[asset]["trend_locked"] = True; return
        if BOT_SWITCH == "ON" and not asset_states[asset]["trend_locked"]:
            asset_states[asset]["last_trigger_bar_time"] = signal_bar_time
            asset_states[asset]["trend_order_counter"] += 1
            trade_amount = round(asset_states[asset]["current_amount"], 2)
            current_step_at_trade = asset_states[asset]["current_step"]
            now_str = datetime.datetime.now().strftime("%H:%M:%S")
            pnl_color = GREEN_TEXT if net_profit_loss >= 0 else RED_TEXT
            pnl_sign = "+" if net_profit_loss > 0 else ""
            
            # บังคับพิมพ์บันทึกแถวคำสั่งซื้อจริงแยกต่างหากแบบชัดเจน
            sys.stdout.write("\r" + " " * 130 + "\r")
            print(f"🎯 [{now_str}] [ NET PnL: {pnl_color}{pnl_sign}${net_profit_loss:.2f}{RESET} ] ORDER -> {asset} | {action.upper()} | Step {current_step_at_trade} | ${trade_amount}")
            
            status, order_id = API.buy(trade_amount, asset, action, trade_expiry)
            if status and order_id is not None: threading.Thread(target=check_past_order_result_async, args=(asset, order_id, trade_amount, current_step_at_trade), daemon=True).start()
            else: print(f"❌ [{now_str}] [{asset}] Order Rejected by Server.")

if __name__ == "__main__":
    print(f"{Fore.CYAN}Connecting to IQ Option...{Style.RESET_ALL}")
    API = IQ_Option(EMAIL, PASSWORD); API.SESSION_HEADER = {"User-Agent": "Mozilla/5.0"}
    check_connect, reason = API.connect()
    if not check_connect: print(f"{Fore.RED}❌ Connection Failed: {reason}{Style.RESET_ALL}"); sys.exit()
    print(f"{Fore.GREEN}✅ Connection Successful!{Style.RESET_ALL}"); API.change_balance(MODE)
    print(f"\n{Fore.GREEN}🚀 ENGINE STATUS: v236.1 (FLUSH REFRESH MODE)...{Style.RESET_ALL}\n")
    
    while bot_running_flag:
        if not API.check_connect(): API.connect(); API.change_balance(MODE)
        for target_asset in BASE_ASSETS: scan_signal_engine(f"{target_asset}-OTC")
        
        # 🕒 ล็อกเวลาให้อยู่กับที่บรรทัดสุดท้าย กระพริบเฉพาะตัวเลขวินาที ไม่ล้นจอ และถอด "โหมดแก้ไขด่วน" ในตัวให้เสร็จสรรพ
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        pnl_color = GREEN_TEXT if net_profit_loss >= 0 else RED_TEXT
        pnl_sign = "+" if net_profit_loss > 0 else ""
        sys.stdout.write(f"\r⏳ [{now_str}] | Port Net PnL: {pnl_color}{pnl_sign}${net_profit_loss:.2f}{RESET} | Bot is scanning market actively...")
        sys.stdout.flush()
        time.sleep(0.5)
        
    print(f"\n{Fore.YELLOW}🏁 Bot stopped smoothly based on portfolio targets.{Style.RESET_ALL}")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 