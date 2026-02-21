from SmartApi import SmartConnect
import pyotp
import pandas as pd
from datetime import datetime, timedelta
import time

# --- DETAILS ---
api_key = "oLKE27Hl"
client_id = "A52096737"
password = "2004" # Aapka MPIN
totp_secret = "AICJGYHLTN2SN4UO3EVCEQBL2Q"

obj = SmartConnect(api_key=api_key)
token = pyotp.TOTP(totp_secret).now()
obj.generateSession(client_id, password, token)

# --- LOOP LOGIC FOR 1.5 YEARS ---
all_data = []
current_to_date = datetime.now()
final_from_date = current_to_date - timedelta(days=540) # 1.5 saal

print("📡 1.5 saal ka data tukdon mein fetch ho raha hai (30 days per request)...")

while current_to_date > final_from_date:
    temp_from_date = current_to_date - timedelta(days=30)
    
    params = {
        "exchange": "NSE",
        "symboltoken": "99926037",
        "interval": "ONE_MINUTE",
        "fromdate": temp_from_date.strftime('%Y-%m-%d %H:%M'),
        "todate": current_to_date.strftime('%Y-%m-%d %H:%M')
    }
    
    try:
        response = obj.getCandleData(params)
        if response and response.get('data'):
            all_data.extend(response['data'])
            print(f"✅ Fetched: {temp_from_date.date()} to {current_to_date.date()}")
        
        # Thoda gap (delay) taaki API limit hit na ho
        time.sleep(0.5) 
        
    except Exception as e:
        print(f"⚠️ Error on {temp_from_date}: {e}")
    
    # Agle chunk ke liye date piche le jayein
    current_to_date = temp_from_date

# --- SAVE EVERYTHING ---
if all_data:
    df = pd.DataFrame(all_data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df = df.sort_values(by='time') # Time ke hisaab se seedha karein
    df.to_csv("FinNifty_2_1.5_Years_Full.csv", index=False)
    print(f"\n🚀 MISSION SUCCESS! Poora data save ho gaya: finNifty_1.5_Years_Full.csv")
    print(f"Total Rows: {len(df)}")
else:
    print("❌ Kuch bhi data nahi mila.")

obj.terminateSession(client_id)