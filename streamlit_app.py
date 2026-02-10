import streamlit as st
import time
import io
from datetime import datetime, date

# ---------------------------------------------------------
# 1. SETUP & CUSTOM CSS (UX/UI UPGRADE)
# ---------------------------------------------------------
st.set_page_config(page_title="Prosthesis Registry & TUG", layout="wide", page_icon="🦿")

st.markdown("""
    <style>
    /* Import Font */
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }

    /* Header Styling */
    .main-header {
        background: linear-gradient(90deg, #1F618D 0%, #2980B9 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Section Headers */
    .section-header {
        color: #1F618D;
        font-weight: bold;
        font-size: 1.2em;
        border-bottom: 2px solid #AED6F1;
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* Input Fields Styling */
    .stTextInput input, .stNumberInput input, .stSelectbox, .stDateInput {
        border-radius: 8px !important;
    }

    /* TUG Timer Display */
    .tug-display { 
        font-size: 90px; 
        font-weight: 700; 
        color: #2E86C1; 
        text-align: center;
        background: #F4F6F7;
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 20px;
        font-family: 'Courier New', monospace;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.05);
        border: 1px solid #ddd;
    }

    /* Result Box */
    .result-box {
        padding: 25px; 
        border-radius: 15px; 
        text-align: center; 
        margin-top: 25px; 
        color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    
    /* Buttons */
    .stButton button { 
        height: 3.5em; 
        font-weight: bold; 
        border-radius: 8px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SESSION STATE & LOGIC
# ---------------------------------------------------------
def reset_tug_callback():
    st.session_state.t1 = 0.0
    st.session_state.t2 = 0.0
    st.session_state.t3 = 0.0
    st.session_state.tug_avg = 0.0
    st.session_state.tug_status = "-"
    st.session_state.tug_running = False
    st.session_state.start_time = None

def calculate_tug():
    times = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0]
    if times:
        avg = sum(times) / len(times)
        st.session_state.tug_avg = avg
        st.session_state.tug_status = "⚠️ High Fall Risk (เสี่ยงล้มสูง)" if avg >= 13.5 else "✅ Normal Mobility (ปกติ)"
    else:
        st.session_state.tug_avg = 0.0
        st.session_state.tug_status = "-"

# ตั้งค่า Default (เพิ่มฟิลด์ให้ครบถ้วน)
defaults = {
    # 1. Identity
    'hn': '', 'cid': '', 'fname': '', 'gender': 'ชาย', 
    'dob': date(1970, 1, 1), 'age': 0,
    # 2. Contact & Address
    'phone': '', 'address': '', 'province': 'กรุงเทพมหานคร', 
    # 3. Social & Rights
    'nationality': 'ไทย', 'religion': 'พุทธ', 'occupation': 'ไม่ระบุ',
    'rights': 'บัตรทอง (UC)', 'emergency_contact': '', 'emergency_phone': '',
    # 4. Physical
    'weight': 0.0, 'height': 0.0, 'service_date': date.today(),
    # 5. Medical
    'cause': 'อุบัติเหตุ', 'side': 'ขวา', 'level': 'Transtibial', 
    'k_level': 'K1', 'comorbidities': [],
    # 6. Prosthesis
    'socket': 'PTB', 'suspension': 'Pin Lock', 'foot': 'SACH', 
    'knee': 'None (Below Knee)', 'liner': 'None',
    # TUG
    'tug_running': False, 'start_time': None,
    't1': 0.0, 't2': 0.0, 't3': 0.0, 'tug_avg': 0.0, 'tug_status': '-'
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------
# 3. HTML REPORT GENERATOR
# ---------------------------------------------------------
def create_html_report():
    dob_str = st.session_state.dob.strftime('%d/%m/%Y')
    service_str = st.session_state.service_date.strftime('%d/%m/%Y')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Sarabun', sans-serif; padding: 40px; line-height: 1.5; font-size: 14px; }}
            h1 {{ text-align: center; color: #1F618D; margin-bottom: 5px; }}
            h3 {{ text-align: center; color: #555; margin-top: 0; font-weight: normal; }}
            .header-box {{ border: 1px solid #333; padding: 10px; margin-bottom: 20px; text-align: right; font-size: 12px; }}
            h2 {{ 
                color: #fff; background-color: #1F618D; 
                padding: 5px 10px; border-radius: 3px; 
                font-size: 16px; margin-top: 20px; 
            }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 5px; }}
            td {{ padding: 6px; border-bottom: 1px solid #eee; vertical-align: top; }}
            .label {{ font-weight: bold; width: 30%; color: #333; background-color: #f9f9f9; }}
            .tug-result {{ 
                text-align: center; border: 2px solid #1F618D; padding: 15px; 
                margin-top: 20px; border-radius: 8px; background-color: #F2F3F4;
            }}
        </style>
    </head>
    <body>
        <h1>แบบบันทึกข้อมูลกายอุปกรณ์ (Prosthesis Registry)</h1>
        <h3>โรงพยาบาล........................................................</h3>
        
        <div class="header-box">
            วันที่รับบริการ: {service_str} | HN: {st.session_state.hn}
        </div>
        
        <h2>1. ข้อมูลทั่วไป (General Information)</h2>
        <table>
            <tr><td class="label">เลขบัตรประชาชน:</td><td>{st.session_state.cid}</td></tr>
            <tr><td class="label">ชื่อ-นามสกุล:</td><td>{st.session_state.fname}</td></tr>
            <tr><td class="label">วันเกิด (อายุ):</td><td>{dob_str} ({st.session_state.age} ปี)</td></tr>
            <tr><td class="label">เพศ / ศาสนา:</td><td>{st.session_state.gender} / {st.session_state.religion}</td></tr>
            <tr><td class="label">สัญชาติ:</td><td>{st.session_state.nationality}</td></tr>
            <tr><td class="label">ที่อยู่:</td><td>{st.session_state.address} จ.{st.session_state.province}</td></tr>
            <tr><td class="label">เบอร์โทรศัพท์:</td><td>{st.session_state.phone}</td></tr>
            <tr><td class="label">อาชีพ:</td><td>{st.session_state.occupation}</td></tr>
            <tr><td class="label">สิทธิการรักษา:</td><td>{st.session_state.rights}</td></tr>
            <tr><td class="label">ผู้ติดต่อฉุกเฉิน:</td><td>{st.session_state.emergency_contact} ({st.session_state.emergency_phone})</td></tr>
        </table>

        <h2>2. ข้อมูลทางกายภาพและการแพทย์</h2>
        <table>
            <tr><td class="label">น้ำหนัก / ส่วนสูง:</td><td>{st.session_state.weight} กก. / {st.session_state.height} ซม.</td></tr>
            <tr><td class="label">โรคประจำตัว:</td><td>{", ".join(st.session_state.comorbidities) if st.session_state.comorbidities else "-"}</td></tr>
            <tr><td class="label">สาเหตุการตัดขา:</td><td>{st.session_state.cause}</td></tr>
            <tr><td class="label">ระดับการตัด / ข้าง:</td><td>{st.session_state.level} ({st.session_state.side})</td></tr>
            <tr><td class="label">ระดับสมรรถภาพ (K-Level):</td><td>{st.session_state.k_level}</td></tr>
        </table>

        <h2>3. ส่วนประกอบขาเทียม (Components)</h2>
        <table>
            <tr><td class="label">Socket:</td><td>{st.session_state.socket}</td></tr>
            <tr><td class="label">Suspension:</td><td>{st.session_state.suspension}</td></tr>
            <tr><td class="label">Liner:</td><td>{st.session_state.liner}</td></tr>
            <tr><td class="label">Knee:</td><td>{st.session_state.knee}</td></tr>
            <tr><td class="label">Foot:</td><td>{st.session_state.foot}</td></tr>
        </table>

        <h2>4. ผลการทดสอบเดิน (TUG Test)</h2>
        <table>
            <tr>
                <td style="text-align:center;"><b>ครั้งที่ 1</b><br>{st.session_state.t1} วินาที</td>
                <td style="text-align:center;"><b>ครั้งที่ 2</b><br>{st.session_state.t2} วินาที</td>
                <td style="text-align:center;"><b>ครั้งที่ 3</b><br>{st.session_state.t3} วินาที</td>
            </tr>
        </table>
        
        <div class="tug-result">
            <div style="font-size: 1.1em;">เวลาเฉลี่ย (Average)</div>
            <div style="font-size: 2em; font-weight:bold; color: #1F618D;">{st.session_state.tug_avg:.2f} s</div>
            <div style="font-size: 1.2em; margin-top:5px;">{st.session_state.tug_status}</div>
        </div>
    </body>
    </html>
    """
    return html

# ---------------------------------------------------------
# 4. MAIN APP UI
# ---------------------------------------------------------

# Header Logo/Title
st.markdown('<div class="main-header"><h1>🏥 Digital Prosthesis Registry System</h1></div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📂 เมนูจัดการ")
st.sidebar.info("ระบบบันทึกข้อมูลกายอุปกรณ์และทดสอบการเดิน (TUG)")
html_data = create_html_report()
st.sidebar.download_button(
    label="💾 ดาวน์โหลดรายงาน (HTML)",
    data=io.BytesIO(html_data.encode('utf-8')),
    file_name=f"Prosthesis_Report_{st.session_state.hn}.html",
    mime="text/html",
    use_container_width=True
)

# Tabs
tab1, tab2 = st.tabs(["📝 บันทึกข้อมูล (Registry)", "⏱️ จับเวลาเดิน (TUG Test)"])

# === TAB 1: REGISTRY ===
with tab1:
    st.caption("กรอกข้อมูลตามลำดับ (แบบฟอร์มมาตรฐาน)")
    
    # --- Group 1: ข้อมูลระบุตัวตน ---
    st.markdown('<div class="section-header">1. ข้อมูลระบุตัวตน (Identity)</div>', unsafe_allow_html=True)
    st.date_input("📅 วันที่รับบริการ", key="service_date")
    st.text_input("รหัสผู้ป่วย (HN)", key="hn", placeholder="เช่น 66-00123")
    st.text_input("เลขบัตรประชาชน (CID)", key="cid", max_chars=13)
    st.text_input("ชื่อ-นามสกุล", key="fname")
    st.date_input("วันเดือนปีเกิด", key="dob")
    st.number_input("อายุ (ปี)", min_value=0, key="age")
    st.selectbox("เพศ", ["ชาย", "หญิง"], key="gender")

    # --- Group 2: ข้อมูลติดต่อและสิทธิ ---
    st.markdown('<div class="section-header">2. ข้อมูลติดต่อและสิทธิ (Contact & Rights)</div>', unsafe_allow_html=True)
    st.text_input("เบอร์โทรศัพท์", key="phone")
    st.text_area("ที่อยู่ปัจจุบัน", key="address", height=80, placeholder="บ้านเลขที่, หมู่, ซอย, ถนน, แขวง/ตำบล, เขต/อำเภอ")
    st.selectbox("จังหวัด", ["กรุงเทพมหานคร", "ปทุมธานี", "นนทบุรี", "สมุทรปราการ", "เชียงใหม่", "ขอนแก่น", "ภูเก็ต", "อื่นๆ"], key="province")
    st.text_input("อาชีพ", key="occupation")
    st.selectbox("สิทธิการรักษา", ["บัตรทอง (UC)", "ประกันสังคม (SS)", "ข้าราชการ (CSMBS)", "ชำระเงินเอง (Cash)", "อื่นๆ"], key="rights")
    st.text_input("ชื่อผู้ติดต่อฉุกเฉิน", key="emergency_contact")
    st.text_input("เบอร์ผู้ติดต่อฉุกเฉิน", key="emergency_phone")

    # --- Group 3: ข้อมูลทางแพทย์ ---
    st.markdown('<div class="section-header">3. ข้อมูลทางการแพทย์ (Medical)</div>', unsafe_allow_html=True)
    st.number_input("น้ำหนัก (กก.)", 0.0, step=0.1, key="weight")
    st.number_input("ส่วนสูง (ซม.)", 0.0, step=1.0, key="height")
    st.multiselect("โรคประจำตัว", ["เบาหวาน", "ความดัน", "โรคหัวใจ", "โรคไต", "ไม่มี"], key="comorbidities")
    st.selectbox("สาเหตุการตัดขา", ["อุบัติเหตุ", "เบาหวาน", "มะเร็ง", "ความผิดปกติแต่กำเนิด", "อื่นๆ"], key="cause")
    st.selectbox("ระดับการตัด", ["Transtibial (ใต้เข่า)", "Transfemoral (เหนือเข่า)", "Knee Disarticulation", "Syme", "Hip Disarticulation"], key="level")
    st.radio("ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="side")
    st.selectbox("K-Level (ก่อนทำ)", ["K0", "K1", "K2", "K3", "K4"], key="k_level")

    # --- Group 4: ขาเทียม ---
    st.markdown('<div class="section-header">4. ส่วนประกอบขาเทียม (Components)</div>', unsafe_allow_html=True)
    st.selectbox("Socket Design", ["PTB", "PTB-SC", "TSB", "Ischial Containment", "Other"], key="socket")
    st.selectbox("Suspension", ["Pin Lock", "Suction (Valve)", "Vacuum (Active)", "Cuff & Belt", "Lanyard"], key="suspension")
    st.selectbox("Liner", ["Pelite (Foam)", "Silicone", "Gel", "None (Hard socket)"], key="liner")
    st.selectbox("Knee Joint", ["None (Below Knee)", "Single Axis", "Polycentric", "Hydraulic", "Microprocessor"], key="knee")
    st.selectbox("Foot", ["SACH", "Single Axis", "Dynamic Response (Carbon)", "Hydraulic Ankle"], key="foot")

# === TAB 2: TUG ===
with tab2:
    st.markdown('<div class="section-header" style="text-align:center;">⏱️ Timed Up and Go Test</div>', unsafe_allow_html=True)
    
    # Timer Display Area
    if st.session_state.tug_running:
        elapsed = time.time() - st.session_state.start_time
        st.markdown(f'<div class="tug-display">{elapsed:.2f}</div>', unsafe_allow_html=True)
        
        # Stop Button
        if st.button("⏹️ STOP (หยุดจับเวลา)", type="primary", use_container_width=True):
            st.session_state.tug_running = False
            final_time = elapsed
            if st.session_state.t1 == 0: st.session_state.t1 = final_time
            elif st.session_state.t2 == 0: st.session_state.t2 = final_time
            elif st.session_state.t3 == 0: st.session_state.t3 = final_time
            calculate_tug()
            st.rerun()
            
        time.sleep(0.03) # Smooth update
        st.rerun()
    else:
        st.markdown(f'<div class="tug-display" style="color:#BDC3C7;">0.00</div>', unsafe_allow_html=True)
        if st.button("▶️ START (เริ่มจับเวลา)", type="primary", use_container_width=True):
            st.session_state.start_time = time.time()
            st.session_state.tug_running = True
            st.rerun()

    st.markdown("---")
    
    # Manual Input Section
    c1, c2, c3 = st.columns(3)
    c1.number_input("ครั้งที่ 1 (วินาที)", key="t1", on_change=calculate_tug)
    c2.number_input("ครั้งที่ 2 (วินาที)", key="t2", on_change=calculate_tug)
    c3.number_input("ครั้งที่ 3 (วินาที)", key="t3", on_change=calculate_tug)

    st.button("🔄 ล้างค่า (Reset)", on_click=reset_tug_callback, use_container_width=True)

    # Result Banner
    if st.session_state.tug_avg > 0:
        bg_color = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#27AE60"
        st.markdown(f"""
            <div class="result-box" style="background-color: {bg_color};">
                <h3 style="color:white; margin:0;">Average Time</h3>
                <h1 style="color:white; margin:0; font-size:3em;">{st.session_state.tug_avg:.2f} s</h1>
                <h2 style="color:white; margin-top:10px; background:none;">{st.session_state.tug_status}</h2>
            </div>
        """, unsafe_allow_html=True)