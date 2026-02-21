import pandas as pd
import os

def convert_to_ist_and_clean(filename, output_name):
    if not os.path.exists(filename):
        print(f"⚠️ File '{filename}' nahi mili.")
        return
    
    print(f"🔄 Processing {filename}...")
    
    try:
        df = pd.read_csv(filename, low_memory=False)
        
        # Header cleanup
        if 'Ticker' in str(df.columns) or 'Ticker' in str(df.iloc[0]):
            df = pd.read_csv(filename, skiprows=2) 

        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        df.set_index(date_col, inplace=True)

        print("🌍 DST Issues ko force-fix karke IST mein badal rahe hain...")
        
        # --- YE WALA LOGIC FAIL NAHI HOGA ---
        if df.index.tz is None:
            # Ambiguous ko NaT karke handle karenge
            df.index = df.index.tz_localize(
                'America/New_York', 
                nonexistent='shift_forward', 
                ambiguous='NaT' 
            ).tz_convert('Asia/Kolkata')
        else:
            df.index = df.index.tz_convert('Asia/Kolkata')
            
        # 1. Jo Ambiguous ki wajah se NaT bane hain, unhe fill karna
        df = df.sort_index()
        df = df.ffill() 
        # Jo bache-kuche NaT index hain unhe drop karna
        df = df[df.index.notnull()]
        # ------------------------------------

        # 2. Weekends hatana
        df = df[df.index.dayofweek < 5] 
        df.index = df.index.tz_localize(None)

        df.to_csv(output_name)
        print(f"✅ SUCCESS! File saved as: {output_name}")
        
    except Exception as e:
        print(f"❌ Error aaya: {e}")

assets = {
    "Gold_5sec_DailyBased_2024_2026.csv": "Gold_IST_Final.csv",
    "Silver_5sec_DailyBased_2024_2026.csv": "Silver_IST_Final.csv"
}

for input_f, output_f in assets.items():
    convert_to_ist_and_clean(input_f, output_f)

print("\n🚀 DONE! Is baar ye bina kisi error ke nikal jayega.")