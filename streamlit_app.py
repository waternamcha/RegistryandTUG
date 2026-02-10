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
    .streamlit-expanderHeader { font-size: 1.1em; font-weight: 600; color: #1F618D; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. ROBUST SESSION STATE INITIALIZATION
# ---------------------------------------------------------
initial_values = {
    'hn': '', 'fname': '', 'dob': date(1980, 1, 1), 'gender': 'ชาย',
    'country': 'Thailand', 'country_ot': '', 'province': 'กรุงเทพมหานคร', 'province_ot': '',
    'nationality': 'ไทย', 'nationality_ot': '', 'weight': 0.0, 'height': 0.0,
    'comorbidities': [], 'comorb_ot': '', 'cause': 'อุบัติเหตุ', 'cause_ot': '',
    'amp_year': 2560, 'side': 'ขวา', 'level': 'Transtibial', 'level_ot': '',
    'stump_len': 'ปานกลาง', 'stump_shape': 'Cylindrical', 'shape_ot': '',
    'surgery': 'ไม่ใช่', 'surg_details': [], 'k_level': 'K1',
    'personnel': [], 'personnel_ot': '', 'rehab': 'ไม่เคย', 'rehab_act': [], 'rehab_act_ot': '',
    'service': [], 'service_ot': '', 'date_cast': date.today(), 'date_deliv': date.today(),
    'socket': 'PTB', 'socket_ot': '', 'liner': 'None', 'liner_ot': '',
    'suspension': [], 'susp_ot': '', 'foot': [], 'foot_ot': '', 'knee': [], 'knee_ot': '',
    'assist': 'ไม่ใช้', 'assist_ot': '', 'stand_hr': '1-3 ชั่วโมง', 'walk_hr': '1-3 ชั่วโมง',
    'fall': 'ไม่', 'fall_freq': '', 'fall_inj': 'ไม่',
    'q31_1': 'ไม่มีปัญหา (0-4%)', 'q31_2': 'ไม่มีปัญหา (0-4%)',
    'q32_1': 'ไม่มีปัญหา (0-4%)', 'q32_2': 'ไม่มีปัญหา (0-4%)',
    'supp_fam': 'ใช่', 'supp_org': 'ไม่ใช่', 'supp_src': [], 'supp_src_ot': '',
    't1': 0.0, 't2': 0.0, 't3': 0.0, 'tug_avg': 0.0, 'tug_status': '-',
    'tug_running': False, 'start_time': None
}

for key, value in initial_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

def get_txt(key, ot_key=None):
    val = st.session_state.get(key, "-")
    if isinstance(val, list):
        if not val: return "-"
        text = ", ".join(val)
        if ot_key and ("Other" in val or "อื่นๆ" in val):
            text += f" ({st.session_state.get(ot_key, '')})"
        return text
    if ot_key and (val == "Other" or val == "อื่นๆ"):
        return f"{val} ({st.session_state.get(ot_key, '')})"
    return str(val)

def calculate_tug():
    # ดึงค่าตรงๆ จาก state เพื่อป้องกัน AttributeError
    t1 = st.session_state.get('t1', 0.0)
    t2 = st.session_state.get('t2', 0.0)
    t3 = st.session_state.get('t3', 0.0)
    valid_times = [t for t in [t1, t2, t3] if t > 0.01]
    if valid_times:
        avg = sum(valid_times) / len(valid_times)
        st.session_state.tug_avg = round(avg, 2)
        st.session_state.tug_status = "⚠️ High Fall Risk" if avg >= 13.5 else "✅ Normal Mobility"
    else:
        st.session_state.tug_avg = 0.0
        st.session_state.tug_status = "-"

# ---------------------------------------------------------
# 3. HTML REPORT GENERATION
# ---------------------------------------------------------
def create_html():
    dob_str = st.session_state.get('dob').strftime('%d/%m/%Y')
    age = date.today().year - st.session_state.get('dob').year
    
    html = f"""
    <div style="font-family: 'Sarabun', sans-serif; padding: 20px; line-height: 1.6;">
        <h2 style="color: #1F618D; border-bottom: 2px solid #1F618D;">Prosthesis Registry Report</h2>
        <p><b>HN:</b> {st.session_state.hn} | <b>Name:</b> {st.session_state.fname}</p>
        <p><b>DOB:</b> {dob_str} ({age} ปี) | <b>Gender:</b> {st.session_state.gender}</p>
        <hr>
        <h4>Medical Information</h4>
        <p><b>Cause:</b> {get_txt('cause', 'cause_ot')} | <b>Side:</b> {st.session_state.side} | <b>Level:</b> {get_txt('level', 'level_ot')}</p>
        <p><b>K-Level:</b> {st.session_state.k_level}</p>
        <hr>
        <h4>Prosthesis Details</h4>
        <p><b>Socket:</b> {get_txt('socket', 'socket_ot')} | <b>Foot:</b> {get_txt('foot', 'foot_ot')}</p>
        <hr>
        <div style="background: #f0f8ff; padding: 15px; border-radius: 10px; border: 1px solid #1F618D; text-align: center;">
            <h3 style="margin:0;">TUG Test Result</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{st.session_state.tug_avg:.2f} s</p>
            <p style="color: {'red' if st.session_state.tug_avg >= 13.5 else 'green'};">{st.session_state.tug_status}</p>
            <p style="font-size: 0.8em;">(T1: {st.session_state.t1:.2f}, T2: {st.session_state.t2:.2f}, T3: {st.session_state.t3:.2f})</p>
        </div>
    </div>
    """
    return html

def save_to_csv():
    if not st.session_state.hn:
        st.toast("⚠️ กรุณากรอก HN ก่อนบันทึก", icon="⚠️")
        return
    
    data = {
        'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'HN': [st.session_state.hn], 'Name': [st.session_state.fname],
        'TUG_Avg': [st.session_state.tug_avg], 'TUG_Status': [st.session_state.tug_status]
    }
    df = pd.DataFrame(data)
    file = 'prosthesis_database.csv'
    df.to_csv(file, mode='a', header=not os.path.exists(file), index=False, encoding='utf-8-sig')
    st.toast(f"✅ บันทึกข้อมูล HN: {st.session_state.hn} สำเร็จ!", icon="💾")

# ---------------------------------------------------------
# 4. MAIN INTERFACE
# ---------------------------------------------------------
col_title, col_btn = st.columns([3, 1])
with col_title:
    st.markdown('<div class="main-title">🏥 Digital Prosthesis Registry</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">ระบบบันทึกข้อมูลกายอุปกรณ์และทดสอบการเดิน (OM Platform)</div>', unsafe_allow_html=True)

with col_btn:
    st.download_button(
        "📥 Download & Auto-Save",
        data=create_html(),
        file_name=f"Report_{st.session_state.hn}.html",
        mime="text/html",
        on_click=save_to_csv,
        use_container_width=True,
        type="primary"
    )

tab1, tab2 = st.tabs(["📝 Registry Form", "⏱️ TUG Test"])

with tab1:
    with st.expander("1. ข้อมูลทั่วไป (General Info)", expanded=True):
        st.date_input("1. วัน/เดือน/ปีเกิด", key="dob")
        st.selectbox("2. เพศ", ["ชาย", "หญิง"], key="gender")
        st.selectbox("3. ประเทศที่อยู่อาศัย", ["Thailand", "Other"], key="country")
        if st.session_state.country == "Other": st.text_input("ระบุประเทศ", key="country_ot")
        st.selectbox("4. จังหวัด", ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "ภูเก็ต", "Other"], key="province")
        if st.session_state.province == "Other": st.text_input("ระบุจังหวัด", key="province_ot")
        st.selectbox("5. สัญชาติ", ["ไทย", "Other"], key="nationality")
        if st.session_state.nationality == "Other": st.text_input("ระบุสัญชาติ", key="nationality_ot")
        st.text_input("6. เลขประจำตัวผู้ป่วย (HN)", key="hn")
        st.text_input("ชื่อ-นามสกุล", key="fname")
        st.number_input("7. น้ำหนัก (kg)", key="weight", step=0.1)
        st.number_input("8. ส่วนสูง (cm)", key="height", step=1.0)

    with st.expander("2. ข้อมูลการตัดขาและสุขภาพ", expanded=False):
        st.multiselect("9. โรคประจำตัว", ["เบาหวาน", "ความดัน", "หัวใจ", "มะเร็ง", "Other"], key="comorbidities")
        if "Other" in st.session_state.comorbidities: st.text_input("ระบุโรค", key="comorb_ot")
        st.selectbox("10. สาเหตุการตัดขา", ["อุบัติเหตุ", "เบาหวาน", "หลอดเลือด", "Other"], key="cause")
        if st.session_state.cause == "Other": st.text_input("ระบุสาเหตุ", key="cause_ot")
        st.number_input("11. ปีที่ตัดขา (พ.ศ.)", 2490, 2600, key="amp_year")
        st.radio("12. ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="side")
        st.selectbox("13. ระดับการตัดขา", ["Transtibial", "Transfemoral", "Knee disarticulation", "Other"], key="level")
        if st.session_state.level == "Other": st.text_input("ระบุระดับ", key="level_ot")
        st.selectbox("14. ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"], key="stump_len")
        st.selectbox("15. รูปทรงตอขา", ["Conical", "Cylindrical", "Bulbous", "Other"], key="stump_shape")
        if st.session_state.stump_shape == "Other": st.text_input("ระบุรูปทรง", key="shape_ot")
        st.radio("16. ผ่าตัดเพิ่มเติม", ["ไม่ใช่", "ใช่"], horizontal=True, key="surgery")
        if st.session_state.surgery == "ใช่": st.multiselect("รายละเอียด", ["ตัดกระดูก", "ตัดผิวหนัง"], key="surg_details")
        st.selectbox("17. K-Level ก่อนตัด", ["K0", "K1", "K2", "K3", "K4"], key="k_level")

    with st.expander("3. การฟื้นฟู (Rehab)", expanded=False):
        st.multiselect("18. บุคลากรที่ดูแล", ["นักกายอุปกรณ์", "นักกายภาพ", "แพทย์", "Other"], key="personnel")
        st.radio("19. ประวัติฟื้นฟู", ["ไม่เคย", "เคย"], key="rehab")
        if st.session_state.rehab == "เคย":
            st.multiselect("กิจกรรม", ["ถุงลดบวม", "ฝึกเดิน", "Other"], key="rehab_act")

    with st.expander("4. กายอุปกรณ์ (Prosthesis)", expanded=False):
        st.multiselect("20. บริการครั้งนี้", ["ทำใหม่", "ซ่อม", "เปลี่ยนเบ้า", "Other"], key="service")
        c1, c2 = st.columns(2)
        with c1: st.date_input("21. วันที่หล่อแบบ", key="date_cast")
        with c2: st.date_input("22. วันที่ได้รับ", key="date_deliv")
        st.selectbox("23. Socket Type", ["PTB", "TSB", "KBM", "Other"], key="socket")
        if st.session_state.socket == "Other": st.text_input("ระบุ Socket", key="socket_ot")
        st.selectbox("24. Liner", ["None", "Silicone", "Gel", "Other"], key="liner")
        st.multiselect("25. Suspension", ["Pin Lock", "Suction", "Vacuum", "Other"], key="suspension")
        st.multiselect("26. Foot", ["SACH", "Dynamic", "Microprocessor", "Other"], key="foot")
        if "Other" in st.session_state.foot: st.text_input("ระบุ Foot", key="foot_ot")
        st.multiselect("27. Knee", ["Single Axis", "Polycentric", "Other"], key="knee")

    with st.expander("5. สังคมและการใช้งาน", expanded=False):
        st.selectbox("28. อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "ไม้เท้า", "Walker", "Other"], key="assist")
        st.selectbox("29.1 เวลายืนต่อวัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="stand_hr")
        st.selectbox("29.2 เวลาเดินต่อวัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="walk_hr")
        st.radio("30. ประวัติล้ม (6 เดือน)", ["ไม่", "มี"], horizontal=True, key="fall")
        st.radio("33.1 การดูแลจากครอบครัว", ["ใช่", "ไม่ใช่"], key="supp_fam")
        st.radio("33.2 สนับสนุนจากองค์กร", ["ไม่ใช่", "ใช่"], key="supp_org")

with tab2:
    st.markdown('<div style="text-align:center; font-weight:bold; font-size:1.5em;">⏱️ Timed Up and Go Test</div>', unsafe_allow_html=True)
    
    # TIMER LOGIC
    placeholder = st.empty()
    if st.session_state.tug_running:
        elapsed = time.time() - st.session_state.start_time
        placeholder.markdown(f'<div class="tug-display">{elapsed:.2f} s</div>', unsafe_allow_html=True)
        if st.button("⏹️ STOP", type="primary", use_container_width=True):
            final_val = round(time.time() - st.session_state.start_time, 2)
            st.session_state.tug_running = False
            # ยัดลงช่องว่าง Trial 1 -> 2 -> 3
            if st.session_state.t1 == 0: st.session_state.t1 = final_val
            elif st.session_state.t2 == 0: st.session_state.t2 = final_val
            elif st.session_state.t3 == 0: st.session_state.t3 = final_val
            calculate_tug()
            st.rerun()
        time.sleep(0.05)
        st.rerun()
    else:
        placeholder.markdown(f'<div class="tug-display" style="color:#ccc;">0.00 s</div>', unsafe_allow_html=True)
        if st.button("▶️ START", type="primary", use_container_width=True):
            st.session_state.start_time = time.time()
            st.session_state.tug_running = True
            st.rerun()

    st.divider()
    
    # TRIAL INPUTS (บังคับค่าผ่าน value= เพื่อความเสถียร)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.t1 = st.number_input("Trial 1 (s)", value=st.session_state.t1, format="%.2f", step=0.01)
    with c2:
        st.session_state.t2 = st.number_input("Trial 2 (s)", value=st.session_state.t2, format="%.2f", step=0.01)
    with c3:
        st.session_state.t3 = st.number_input("Trial 3 (s)", value=st.session_state.t3, format="%.2f", step=0.01)

    calculate_tug()
    
    if st.button("🔄 Reset Timer Scores", use_container_width=True):
        st.session_state.t1, st.session_state.t2, st.session_state.t3 = 0.0, 0.0, 0.0
        st.session_state.tug_avg = 0.0
        st.rerun()

    if st.session_state.tug_avg > 0:
        bg = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#27AE60"
        st.markdown(f'<div class="result-box" style="background:{bg}">Average: {st.session_state.tug_avg} s ({st.session_state.tug_status})</div>', unsafe_allow_html=True)

# SIDEBAR PREVIEW
if os.path.exists('prosthesis_database.csv'):
    st.sidebar.markdown("### 📊 Recent Records")
    df = pd.read_csv('prosthesis_database.csv')
    st.sidebar.dataframe(df.tail(10))