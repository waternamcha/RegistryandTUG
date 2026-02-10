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

    /* Main Title */
    .main-title { text-align: center; font-size: 2.5em; font-weight: 700; color: #154360; margin-top: -20px; }
    .sub-title { text-align: center; font-size: 1.1em; color: #5D6D7E; margin-bottom: 20px; }

    /* TUG Timer */
    .tug-display { 
        font-size: 80px; font-weight: 700; color: #2E86C1; 
        text-align: center; background-color: #f4f6f7; 
        padding: 30px; border-radius: 20px; margin-bottom: 20px;
        font-family: 'Courier New', monospace; border: 3px solid #d6eaf8;
    }
    
    /* Result Box */
    .result-box {
        padding: 20px; border-radius: 15px; text-align: center; 
        color: white; font-weight: bold; font-size: 1.3em;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-top: 15px;
    }

    /* Expander */
    .streamlit-expanderHeader { font-size: 1.1em; font-weight: 600; color: #1F618D; background-color: #ffffff; border: 1px solid #eee; border-radius: 8px; }
    .stTextInput>div>div>input { border-radius: 8px; }
    .stSelectbox>div>div>div { border-radius: 8px; }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    /* Mobile Responsive Adjustments */
    @media (max-width: 600px) {
        .main-title { font-size: 1.8em; }
        .tug-display { font-size: 50px; padding: 20px; }
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# ---------------------------------------------------------
defaults = {
    'hn': '', 'fname': '', 'dob': date(1980, 1, 1), 'age': 0, 'gender': 'ชาย', 
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
    # TUG State
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
    # ดึงค่าจาก state โดยตรง
    times = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0.01]
    if times:
        avg = sum(times) / len(times)
        st.session_state.tug_avg = avg
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
# 3. HTML REPORT
# ---------------------------------------------------------
def create_html():
    dob = st.session_state.dob.strftime('%d/%m/%Y')
    age_calc = date.today().year - st.session_state.dob.year
    date_cast_str = st.session_state.date_cast.strftime('%d/%m/%Y')
    date_deliv_str = st.session_state.date_deliv.strftime('%d/%m/%Y')
    t1_val, t2_val, t3_val = st.session_state.t1, st.session_state.t2, st.session_state.t3
    avg_val, status_val = st.session_state.tug_avg, st.session_state.tug_status

    html = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Sarabun', sans-serif; padding: 20px; color: #333; line-height: 1.5; font-size: 14px; }}
            h1 {{ text-align: center; border-bottom: 2px solid #1F618D; padding-bottom: 10px; color: #1F618D; font-size: 1.6em; }}
            .section {{ margin-top: 15px; background: #fff; padding: 10px; border-radius: 8px; border: 1px solid #ddd; page-break-inside: avoid; }}
            .sec-head {{ color: #154360; font-weight: bold; font-size: 1.1em; margin-bottom: 8px; border-left: 5px solid #154360; padding-left: 10px; background-color: #f4f6f7; padding: 5px 10px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 5px; border-bottom: 1px solid #eee; vertical-align: top; }}
            .lbl {{ font-weight: bold; width: 35%; color: #555; }}
            .tug-box {{ text-align: center; border: 2px solid #1F618D; padding: 10px; margin-top: 15px; border-radius: 10px; background: #f0f8ff; }}
            .value {{ color: #000; }}
        </style>
    </head>
    <body>
        <div style="text-align:right; font-size:0.8em; color:gray;">Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        <h1>Prosthesis Registry Report</h1>
        <div class="section">
            <div class="sec-head">1. ข้อมูลทั่วไป</div>
            <table>
                <tr><td class="lbl">HN:</td><td>{st.session_state.hn}</td></tr>
                <tr><td class="lbl">ชื่อ-สกุล:</td><td>{st.session_state.fname}</td></tr>
                <tr><td class="lbl">วันเกิด:</td><td>{dob} ({age_calc} ปี)</td></tr>
            </table>
        </div>
        <div class="section">
            <div class="sec-head">4. กายอุปกรณ์</div>
            <table>
                <tr><td class="lbl">Socket:</td><td>{get_txt(st.session_state.socket, 'socket_ot')}</td></tr>
                <tr><td class="lbl">Foot:</td><td>{get_txt(st.session_state.foot, 'foot_ot')}</td></tr>
            </table>
        </div>
        <div class="tug-box">
            <h3 style="margin:0;">TUG Test Result</h3>
            <h1 style="margin:5px 0;">{avg_val:.2f} s</h1>
            <h3 style="color:{'#C0392B' if avg_val >= 13.5 else '#27AE60'};">{status_val}</h3>
            <p>(T1: {t1_val:.2f} | T2: {t2_val:.2f} | T3: {t3_val:.2f})</p>
        </div>
    </body>
    </html>
    """
    return html

# ---------------------------------------------------------
# 4. SAVE & MAIN APP LOGIC
# ---------------------------------------------------------
def save_to_csv():
    if st.session_state.hn == "":
        st.toast('⚠️ ไม่ได้บันทึก: กรุณากรอก HN ก่อน', icon='⚠️')
        return
    
    data = {
        'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'HN': [st.session_state.hn], 'Name': [st.session_state.fname],
        'TUG_Avg': [st.session_state.tug_avg], 'TUG_Status': [st.session_state.tug_status]
    }
    df = pd.DataFrame(data)
    file_path = 'prosthesis_database.csv'
    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(file_path, mode='a', header=False, index=False, encoding='utf-8-sig')
    st.toast(f'✅ บันทึก HN: {st.session_state.hn} เรียบร้อย!', icon='💾')

html_data = create_html()

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="main-title">🏥 Digital Prosthesis Registry</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">ระบบบันทึกข้อมูลกายอุปกรณ์และทดสอบการเดิน (OM Platform)</div>', unsafe_allow_html=True)

with col_h2:
    st.write("")
    st.download_button("📥 Download & Auto-Save", data=io.BytesIO(html_data.encode('utf-8')), file_name=f"Report_{st.session_state.hn}.html", mime="text/html", type="primary", use_container_width=True, on_click=save_to_csv)

# Sidebar
if os.path.exists('prosthesis_database.csv'):
    df_db = pd.read_csv('prosthesis_database.csv')
    st.sidebar.download_button(label="📊 Download Database (CSV)", data=df_db.to_csv(index=False).encode('utf-8-sig'), file_name="prosthesis_database.csv", mime="text/csv", use_container_width=True)

# --- TABS ---
tab1, tab2 = st.tabs(["📝 Registry Form", "⏱️ TUG Test"])

with tab1:
    with st.expander("1. ข้อมูลทั่วไป (General Info)", expanded=True):
        st.date_input("1. วัน/เดือน/ปีเกิด", key="dob")
        st.text_input("6. เลขประจำตัวผู้ป่วย (HN)", key="hn")
        st.text_input("ชื่อ-นามสกุล (Name)", key="fname")
        st.number_input("7. น้ำหนัก (kg)", 0.0, step=0.1, key="weight")
        st.number_input("8. ส่วนสูง (cm)", 0.0, step=1.0, key="height")
    # ... (ส่วน Medical, Rehab, Prosthesis, Social อื่นๆ คงไว้ตามเดิม)
    with st.expander("2. ข้อมูลทางการแพทย์", expanded=False):
        st.selectbox("10. สาเหตุการตัดขา", ["อุบัติเหตุ", "เบาหวาน", "Other"], key="cause")
        st.radio("12. ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], key="side")
    with st.expander("4. กายอุปกรณ์", expanded=False):
        st.selectbox("23. Socket Type", ["PTB", "TSB", "Other"], key="socket")
        st.multiselect("26. Foot", ["SACH", "Dynamic", "Other"], key="foot")

with tab2:
    st.markdown('<div class="section-title" style="text-align:center; margin-top:20px;">⏱️ Timed Up and Go Test</div>', unsafe_allow_html=True)
    
    # Timer Display Logic
    if st.session_state.tug_running:
        elapsed = time.time() - st.session_state.start_time
        st.markdown(f'<div class="tug-display">{elapsed:.2f} s</div>', unsafe_allow_html=True)
        if st.button("⏹️ STOP", type="primary", use_container_width=True):
            fin = round(elapsed, 2)
            # แก้ไขบัค: บันทึกเข้า State โดยตรงก่อน Rerun
            if st.session_state.t1 <= 0.01: st.session_state.t1 = fin
            elif st.session_state.t2 <= 0.01: st.session_state.t2 = fin
            elif st.session_state.t3 <= 0.01: st.session_state.t3 = fin
            st.session_state.tug_running = False
            calculate_tug()
            st.rerun()
        time.sleep(0.05)
        st.rerun()
    else:
        st.markdown(f'<div class="tug-display" style="color:#ccc;">0.00 s</div>', unsafe_allow_html=True)
        if st.button("▶️ START", type="primary", use_container_width=True):
            st.session_state.start_time = time.time()
            st.session_state.tug_running = True
            st.rerun()

    st.markdown("---")
    
    # แก้ไขบัคช่องกรอก: ใช้ value ผูกกับ state และใช้ key ที่ต่างกันเล็กน้อยเพื่อป้องกัน Shadowing
    c1, c2, c3 = st.columns(3)
    with c1:
        v1 = st.number_input("Trial 1", value=st.session_state.t1, step=0.01, format="%.2f", key="input_t1")
        st.session_state.t1 = v1
    with c2:
        v2 = st.number_input("Trial 2", value=st.session_state.t2, step=0.01, format="%.2f", key="input_t2")
        st.session_state.t2 = v2
    with c3:
        v3 = st.number_input("Trial 3", value=st.session_state.t3, step=0.01, format="%.2f", key="input_t3")
        st.session_state.t3 = v3
    
    # อัปเดตค่าเฉลี่ยทุกครั้งที่ตัวเลขเปลี่ยน
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