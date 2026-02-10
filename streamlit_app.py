import streamlit as st
import time
import io
import pandas as pd
import os
from datetime import datetime, date

# ---------------------------------------------------------
# 1. SETUP & MODERN UI STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="Prosthesis Registry", layout="wide", page_icon="🦿")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }

    .main-title { text-align: center; font-size: 2.5em; font-weight: 700; color: #154360; margin-top: -20px; }
    .sub-title { text-align: center; font-size: 1.1em; color: #5D6D7E; margin-bottom: 20px; }

    .tug-display { 
        font-size: 80px; font-weight: 700; color: #2E86C1; 
        text-align: center; background-color: #f4f6f7; 
        padding: 30px; border-radius: 20px; margin-bottom: 20px;
        font-family: 'Courier New', monospace; border: 3px solid #d6eaf8;
    }
    
    .result-box {
        padding: 20px; border-radius: 15px; text-align: center; 
        color: white; font-weight: bold; font-size: 1.3em;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-top: 15px;
    }

    .streamlit-expanderHeader { font-size: 1.1em; font-weight: 600; color: #1F618D; background-color: #ffffff; border: 1px solid #eee; border-radius: 8px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SESSION STATE MANAGEMENT (FULL VERSION)
# ---------------------------------------------------------
defaults = {
    'hn': '', 'fname': '', 'dob': date(1980, 1, 1), 'gender': 'ชาย', 
    'country': 'Thailand', 'country_ot': '',
    'province': 'กรุงเทพมหานคร', 'province_ot': '',
    'nationality': 'ไทย', 'nationality_ot': '',
    'weight': 0.0, 'height': 0.0,
    'comorbidities': [], 'comorb_ot': '',
    'cause': 'อุบัติเหตุ', 'cause_ot': '',
    'amp_year': 2560, 'side': 'ขวา', 'level': 'Transtibial', 'level_ot': '',
    'stump_len': 'ปานกลาง', 'stump_shape': 'Cylindrical', 'shape_ot': '',
    'surgery': 'ไม่ใช่', 'surg_details': [], 'k_level': 'K1',
    'personnel': [], 'personnel_ot': '',
    'rehab': 'ไม่เคย', 'rehab_act': [], 'rehab_act_ot': '',
    'service': [], 'service_ot': '',
    'date_cast': date.today(), 'date_deliv': date.today(),
    'socket': 'PTB', 'socket_ot': '',
    'liner': 'None', 'liner_ot': '',
    'suspension': [], 'susp_ot': '',
    'foot': [], 'foot_ot': '',
    'knee': [], 'knee_ot': '', 
    'assist': 'ไม่ใช้', 'assist_ot': '',
    'stand_hr': '1-3 ชั่วโมง', 'walk_hr': '1-3 ชั่วโมง',
    'fall': 'ไม่', 'fall_freq': '', 'fall_inj': 'ไม่',
    'q31_1': 'ไม่มีปัญหา (0-4%)', 'q31_2': 'ไม่มีปัญหา (0-4%)',
    'q32_1': 'ไม่มีปัญหา (0-4%)', 'q32_2': 'ไม่มีปัญหา (0-4%)',
    'supp_fam': 'ใช่', 'supp_org': 'ไม่ใช่', 'supp_src': [], 'supp_src_ot': '',
    # TUG 
    'tug_running': False, 'start_time': None,
    't1': 0.0, 't2': 0.0, 't3': 0.0, 'tug_avg': 0.0, 'tug_status': '-'
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def get_txt(val, ot_key):
    if isinstance(val, list):
        if not val: return "-"
        text = ", ".join(val)
        if ("Other" in val or "อื่นๆ" in val) and ot_key in st.session_state:
            text += f" ({st.session_state[ot_key]})"
        return text
    if (val == "Other" or val == "อื่นๆ") and ot_key in st.session_state:
        return f"{val} ({st.session_state[ot_key]})"
    return str(val) if val else "-"

def calculate_tug():
    times = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0.01]
    if times:
        avg = sum(times) / len(times)
        st.session_state.tug_avg = round(avg, 2)
        st.session_state.tug_status = "⚠️ High Fall Risk" if avg >= 13.5 else "✅ Normal Mobility"
    else:
        st.session_state.tug_avg = 0.0
        st.session_state.tug_status = "-"

def reset_tug():
    st.session_state.t1 = 0.0
    st.session_state.t2 = 0.0
    st.session_state.t3 = 0.0
    st.session_state.tug_avg = 0.0
    st.session_state.tug_status = "-"
    st.session_state.tug_running = False

# ---------------------------------------------------------
# 3. HTML REPORT GENERATION
# ---------------------------------------------------------
def create_html():
    dob_str = st.session_state.dob.strftime('%d/%m/%Y')
    age = date.today().year - st.session_state.dob.year
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Sarabun', sans-serif; padding: 20px; }}
            h1 {{ color: #1F618D; border-bottom: 2px solid #1F618D; }}
            .section {{ margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 8px; }}
            .label {{ font-weight: bold; color: #555; width: 30%; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 8px; border-bottom: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <h1>Prosthesis Registry Report</h1>
        <div class="section">
            <h3>1. ข้อมูลทั่วไป</h3>
            <table>
                <tr><td class="label">HN:</td><td>{st.session_state.hn}</td></tr>
                <tr><td class="label">ชื่อ-สกุล:</td><td>{st.session_state.fname}</td></tr>
                <tr><td class="label">วันเกิด:</td><td>{dob_str} (อายุ {age} ปี)</td></tr>
                <tr><td class="label">ที่อยู่:</td><td>{get_txt(st.session_state.province, 'province_ot')}</td></tr>
            </table>
        </div>
        <div class="section">
            <h3>TUG Test Result</h3>
            <p>Trial 1: {st.session_state.t1:.2f} s</p>
            <p>Trial 2: {st.session_state.t2:.2f} s</p>
            <p>Trial 3: {st.session_state.t3:.2f} s</p>
            <hr>
            <p><b>Average: {st.session_state.tug_avg:.2f} s ({st.session_state.tug_status})</b></p>
        </div>
    </body>
    </html>
    """

# ---------------------------------------------------------
# 4. SAVE TO CSV
# ---------------------------------------------------------
def save_to_csv():
    if not st.session_state.hn:
        st.toast('⚠️ กรุณากรอก HN ก่อนบันทึก', icon='⚠️')
        return
    
    data = {
        'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'HN': [st.session_state.hn],
        'Name': [st.session_state.fname],
        'TUG_Avg': [st.session_state.tug_avg]
    }
    df = pd.DataFrame(data)
    path = 'prosthesis_database.csv'
    if not os.path.exists(path):
        df.to_csv(path, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(path, mode='a', header=False, index=False, encoding='utf-8-sig')
    st.toast(f'✅ บันทึกข้อมูล HN: {st.session_state.hn} แล้ว', icon='💾')

# ---------------------------------------------------------
# MAIN UI
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="main-title">🏥 Digital Prosthesis Registry</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">ระบบบันทึกข้อมูลกายอุปกรณ์และทดสอบการเดิน</div>', unsafe_allow_html=True)

with col_h2:
    st.download_button(
        "📥 Download & Auto-Save",
        data=create_html().encode('utf-8'),
        file_name=f"Report_{st.session_state.hn}.html",
        mime="text/html",
        type="primary",
        on_click=save_to_csv,
        use_container_width=True
    )

tab1, tab2 = st.tabs(["📝 Registry Form", "⏱️ TUG Test"])

with tab1:
    with st.expander("1. ข้อมูลทั่วไป (General Info)", expanded=True):
        st.date_input("1. วัน/เดือน/ปีเกิด", key="dob")
        st.selectbox("2. เพศ", ["ชาย", "หญิง"], key="gender")
        st.selectbox("4. จังหวัด", ["กรุงเทพมหานคร", "เชียงใหม่", "ภูเก็ต", "Other"], key="province")
        if st.session_state.province == "Other": st.text_input("ระบุจังหวัด", key="province_ot")
        st.text_input("6. เลขประจำตัวผู้ป่วย (HN)", key="hn")
        st.text_input("ชื่อ-นามสกุล", key="fname")
        st.number_input("7. น้ำหนัก (kg)", key="weight", step=0.1)
        st.number_input("8. ส่วนสูง (cm)", key="height", step=1.0)

    with st.expander("2. ข้อมูลทางการแพทย์", expanded=False):
        st.multiselect("9. โรคประจำตัว", ["เบาหวาน", "ความดัน", "Other"], key="comorbidities")
        st.selectbox("10. สาเหตุการตัดขา", ["อุบัติเหตุ", "เบาหวาน", "Other"], key="cause")
        st.radio("12. ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="side")
        st.selectbox("13. ระดับการตัดขา", ["Transtibial", "Transfemoral", "Other"], key="level")
        st.selectbox("15. รูปทรงตอขา", ["Conical", "Cylindrical", "Other"], key="stump_shape")

    with st.expander("4. กายอุปกรณ์ (Prosthesis)", expanded=False):
        st.selectbox("23. Socket Type", ["PTB", "TSB", "Other"], key="socket")
        st.multiselect("25. Suspension", ["Pin Lock", "Suction", "Other"], key="suspension")
        st.multiselect("26. Foot", ["SACH", "Dynamic", "Other"], key="foot")

    with st.expander("5. สังคมและการใช้งาน", expanded=False):
        st.selectbox("28. อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "ไม้เท้า", "Walker", "Other"], key="assist")
        st.radio("30. ประวัติล้ม (6 เดือน)", ["ไม่", "มี"], horizontal=True, key="fall")

with tab2:
    st.markdown('<div style="text-align:center; font-weight:bold; font-size:1.5em;">⏱️ Timed Up and Go Test</div>', unsafe_allow_html=True)
    
    # TIMER LOGIC
    timer_placeholder = st.empty()
    if st.session_state.tug_running:
        elapsed = time.time() - st.session_state.start_time
        timer_placeholder.markdown(f'<div class="tug-display">{elapsed:.2f} s</div>', unsafe_allow_html=True)
        if st.button("⏹️ STOP", type="primary", use_container_width=True):
            final_val = round(time.time() - st.session_state.start_time, 2)
            st.session_state.tug_running = False
            # ยัดลงช่องว่าง
            if st.session_state.t1 == 0: st.session_state.t1 = final_val
            elif st.session_state.t2 == 0: st.session_state.t2 = final_val
            elif st.session_state.t3 == 0: st.session_state.t3 = final_val
            calculate_tug()
            st.rerun()
        time.sleep(0.05)
        st.rerun()
    else:
        timer_placeholder.markdown(f'<div class="tug-display" style="color:#ccc;">0.00 s</div>', unsafe_allow_html=True)
        if st.button("▶️ START", type="primary", use_container_width=True):
            st.session_state.start_time = time.time()
            st.session_state.tug_running = True
            st.rerun()

    st.divider()
    
    # MANUAL INPUTS (ผูกกับ State ตรงๆ)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.t1 = st.number_input("Trial 1 (s)", value=st.session_state.t1, format="%.2f", step=0.01)
    with c2:
        st.session_state.t2 = st.number_input("Trial 2 (s)", value=st.session_state.t2, format="%.2f", step=0.01)
    with c3:
        st.session_state.t3 = st.number_input("Trial 3 (s)", value=st.session_state.t3, format="%.2f", step=0.01)

    calculate_tug()
    
    if st.button("🔄 Reset Timer", use_container_width=True):
        reset_tug()
        st.rerun()

    if st.session_state.tug_avg > 0:
        bg = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#27AE60"
        st.markdown(f"""
        <div class="result-box" style="background:{bg};">
            <div>Average Time: {st.session_state.tug_avg:.2f} s</div>
            <div style="font-size:1.5em; margin-top:5px;">{st.session_state.tug_status}</div>
        </div>
        """, unsafe_allow_html=True)

# SIDEBAR DATABASE PREVIEW
if os.path.exists('prosthesis_database.csv'):
    st.sidebar.markdown("### 📊 Database Preview")
    df_preview = pd.read_csv('prosthesis_database.csv')
    st.sidebar.dataframe(df_preview.tail(5))
    st.sidebar.download_button("📊 Download Database (CSV)", data=df_preview.to_csv(index=False).encode('utf-8-sig'), file_name="database.csv", mime="text/csv")