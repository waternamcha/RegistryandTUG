import streamlit as st
import time
import io
from datetime import datetime

# ---------------------------------------------------------
# 1. SETUP & STYLE
# ---------------------------------------------------------
st.set_page_config(page_title="Prosthesis Registry & TUG", layout="wide", page_icon="🦿")

st.markdown("""
    <style>
    .tug-display { 
        font-size: 80px; 
        font-weight: bold; 
        color: #2E86C1; 
        text-align: center;
        background-color: #f0f8ff;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 20px;
        font-family: 'Courier New', monospace;
    }
    .result-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-top: 20px;
        color: white;
    }
    .stButton button { height: 3em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SESSION STATE & CALLBACKS (หัวใจสำคัญ)
# ---------------------------------------------------------

# ฟังก์ชันสำหรับ Reset ค่า (ต้องทำแบบนี้ถึงจะไม่ Error)
def reset_tug_callback():
    st.session_state.t1 = 0.0
    st.session_state.t2 = 0.0
    st.session_state.t3 = 0.0
    st.session_state.tug_avg = 0.0
    st.session_state.tug_status = "-"
    st.session_state.tug_running = False
    st.session_state.start_time = None

# ฟังก์ชันคำนวณ TUG เมื่อมีการเปลี่ยนตัวเลข
def calculate_tug():
    times = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0]
    if times:
        avg = sum(times) / len(times)
        st.session_state.tug_avg = avg
        if avg >= 13.5:
            st.session_state.tug_status = "⚠️ High Fall Risk (เสี่ยงล้มสูง)"
        else:
            st.session_state.tug_status = "✅ Normal Mobility (ปกติ)"
    else:
        st.session_state.tug_avg = 0.0
        st.session_state.tug_status = "-"

# ตั้งค่าเริ่มต้นทั้งหมด (ป้องกันข้อมูลหาย)
defaults = {
    # General
    'hn': '', 'fname': '', 'gender': 'ชาย', 'age': 0, 
    'weight': 0.0, 'height': 0.0, 'province': 'กรุงเทพมหานคร',
    'nationality': 'ไทย',
    # Medical
    'cause': 'อุบัติเหตุ', 'side': 'ขวา', 'level': 'Transtibial', 
    'k_level': 'K1', 'comorbidities': [], 'surgery_date': None,
    # Prosthesis
    'socket': 'PTB', 'suspension': 'Pin Lock', 'foot': 'SACH', 
    'knee': 'None (Below Knee)', 'liner': 'None',
    # TUG Data
    'tug_running': False, 'start_time': None,
    't1': 0.0, 't2': 0.0, 't3': 0.0,
    'tug_avg': 0.0, 'tug_status': '-'
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------
# 3. HTML REPORT GENERATOR
# ---------------------------------------------------------
def create_html_report():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Report_{st.session_state.hn}</title>
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Sarabun', sans-serif; padding: 40px; line-height: 1.6; }}
            h1 {{ text-align: center; color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }}
            h2 {{ color: #154360; margin-top: 30px; background: #eee; padding: 5px 10px; border-radius: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; vertical-align: top; }}
            .label {{ font-weight: bold; width: 30%; color: #555; }}
            .tug-result {{ 
                text-align: center; border: 3px solid #333; padding: 20px; 
                margin-top: 20px; border-radius: 10px; font-size: 1.2em;
            }}
        </style>
    </head>
    <body>
        <div style="text-align:right; font-size:12px; color:gray;">พิมพ์เมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        <h1>แบบบันทึกข้อมูลกายอุปกรณ์ (Prosthesis Registry)</h1>
        
        <h2>1. ข้อมูลทั่วไป (General Info)</h2>
        <table>
            <tr><td class="label">HN:</td><td>{st.session_state.hn}</td></tr>
            <tr><td class="label">ชื่อ-สกุล:</td><td>{st.session_state.fname}</td></tr>
            <tr><td class="label">เพศ / อายุ:</td><td>{st.session_state.gender} / {st.session_state.age} ปี</td></tr>
            <tr><td class="label">น้ำหนัก / ส่วนสูง:</td><td>{st.session_state.weight} กก. / {st.session_state.height} ซม.</td></tr>
            <tr><td class="label">ที่อยู่:</td><td>{st.session_state.province} ({st.session_state.nationality})</td></tr>
        </table>

        <h2>2. ข้อมูลการแพทย์ (Medical History)</h2>
        <table>
            <tr><td class="label">โรคประจำตัว:</td><td>{", ".join(st.session_state.comorbidities) if st.session_state.comorbidities else "-"}</td></tr>
            <tr><td class="label">สาเหตุการตัด:</td><td>{st.session_state.cause}</td></tr>
            <tr><td class="label">ระดับ / ข้าง:</td><td>{st.session_state.level} ({st.session_state.side})</td></tr>
            <tr><td class="label">ระดับสมรรถภาพ (K-Level):</td><td>{st.session_state.k_level}</td></tr>
        </table>

        <h2>3. ส่วนประกอบขาเทียม (Prosthesis Components)</h2>
        <table>
            <tr><td class="label">Socket Design:</td><td>{st.session_state.socket}</td></tr>
            <tr><td class="label">Suspension:</td><td>{st.session_state.suspension}</td></tr>
            <tr><td class="label">Liner:</td><td>{st.session_state.liner}</td></tr>
            <tr><td class="label">Knee Joint:</td><td>{st.session_state.knee}</td></tr>
            <tr><td class="label">Foot:</td><td>{st.session_state.foot}</td></tr>
        </table>

        <h2>4. ผลการทดสอบเดิน (TUG Test)</h2>
        <table>
            <tr>
                <td><b>ครั้งที่ 1:</b> {st.session_state.t1} s</td>
                <td><b>ครั้งที่ 2:</b> {st.session_state.t2} s</td>
                <td><b>ครั้งที่ 3:</b> {st.session_state.t3} s</td>
            </tr>
        </table>
        
        <div class="tug-result">
            <b>เวลาเฉลี่ย (Average): {st.session_state.tug_avg:.2f} วินาที</b><br>
            <span style="font-size: 1.5em; font-weight:bold;">{st.session_state.tug_status}</span>
        </div>
    </body>
    </html>
    """
    return html

# ---------------------------------------------------------
# 4. MAIN APP UI
# ---------------------------------------------------------
st.title("🏥 Digital Prosthesis Registry")

# --- SIDEBAR: ปุ่ม Download ปุ่มเดียวตามสั่ง ---
st.sidebar.header("📂 จัดการไฟล์")
html_data = create_html_report()
st.sidebar.download_button(
    label="💾 ดาวน์โหลดรายงาน (HTML)",
    data=io.BytesIO(html_data.encode('utf-8')), # แก้บั๊ก File not found
    file_name=f"Report_{st.session_state.hn}.html",
    mime="text/html"
)

# --- TABS ---
tab1, tab2 = st.tabs(["📝 1. กรอกข้อมูล (Registry)", "⏱️ 2. จับเวลา (TUG Test)"])

# === TAB 1: ข้อมูล (คอลัมน์เดียว + ข้อมูลครบ) ===
with tab1:
    st.info("กรุณากรอกข้อมูลให้ครบถ้วนก่อนกดดาวน์โหลด")
    
    with st.expander("👤 ข้อมูลส่วนตัว", expanded=True):
        st.text_input("HN (รหัสผู้ป่วย)", key="hn")
        st.text_input("ชื่อ-นามสกุล", key="fname")
        st.number_input("อายุ (ปี)", min_value=0, step=1, key="age")
        st.selectbox("เพศ", ["ชาย", "หญิง"], key="gender")
        st.number_input("น้ำหนัก (กก.)", min_value=0.0, step=0.1, key="weight")
        st.number_input("ส่วนสูง (ซม.)", min_value=0.0, step=1.0, key="height")
        st.selectbox("จังหวัด", ["กรุงเทพมหานคร", "ปทุมธานี", "นนทบุรี", "เชียงใหม่", "ขอนแก่น", "ภูเก็ต", "อื่นๆ"], key="province")
        st.selectbox("สัญชาติ", ["ไทย", "อื่นๆ"], key="nationality")

    with st.expander("🏥 ข้อมูลการแพทย์"):
        st.multiselect("โรคประจำตัว", ["เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "โรคไต", "ไม่มี"], key="comorbidities")
        st.selectbox("สาเหตุการตัดขา", ["อุบัติเหตุ", "เบาหวาน (Diabetes)", "มะเร็ง", "ความผิดปกติแต่กำเนิด", "อื่นๆ"], key="cause")
        st.selectbox("ระดับการตัด", ["Transtibial (ใต้เข่า)", "Transfemoral (เหนือเข่า)", "Knee Disarticulation", "Syme", "Hip Disarticulation"], key="level")
        st.radio("ข้าง", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="side")
        st.selectbox("K-Level (ก่อนทำ)", ["K0", "K1", "K2", "K3", "K4"], key="k_level")

    with st.expander("🦿 ส่วนประกอบขาเทียม"):
        st.selectbox("Socket Design", ["PTB", "PTB-SC", "TSB", "Ischial Containment", "Quadrilateral", "Other"], key="socket")
        st.selectbox("Suspension", ["Pin Lock", "Suction (Valve)", "Vacuum (Active)", "Cuff & Belt", "Lanyard"], key="suspension")
        st.selectbox("Liner Interface", ["Pelite (Foam)", "Silicone", "Gel", "Polyurethane", "None (Hard socket)"], key="liner")
        st.selectbox("Knee Joint", ["None (Below Knee)", "Single Axis", "Polycentric", "Hydraulic", "Microprocessor"], key="knee")
        st.selectbox("Foot", ["SACH", "Single Axis", "Dynamic Response (Carbon)", "Hydraulic Ankle"], key="foot")

# === TAB 2: TUG (แก้ปุ่ม Reset แล้ว) ===
with tab2:
    st.header("⏱️ Timed Up and Go (TUG)")
    
    # ส่วนแสดงนาฬิกา
    if st.session_state.tug_running:
        elapsed = time.time() - st.session_state.start_time
        st.markdown(f'<div class="tug-display">{elapsed:.2f} s</div>', unsafe_allow_html=True)
        
        if st.button("⏹️ STOP (หยุด)", type="primary", use_container_width=True):
            st.session_state.tug_running = False
            final_time = elapsed
            # Auto-fill logic
            if st.session_state.t1 == 0: st.session_state.t1 = final_time
            elif st.session_state.t2 == 0: st.session_state.t2 = final_time
            elif st.session_state.t3 == 0: st.session_state.t3 = final_time
            calculate_tug()
            st.rerun()
            
        time.sleep(0.05) # Refresh rate
        st.rerun()
    else:
        st.markdown(f'<div class="tug-display" style="color:#aaa;">0.00 s</div>', unsafe_allow_html=True)
        if st.button("▶️ START (เริ่มจับเวลา)", type="primary", use_container_width=True):
            st.session_state.start_time = time.time()
            st.session_state.tug_running = True
            st.rerun()

    st.markdown("---")

    # Input Fields (Manual Adjust)
    c1, c2, c3 = st.columns(3)
    c1.number_input("ครั้งที่ 1 (วินาที)", key="t1", on_change=calculate_tug)
    c2.number_input("ครั้งที่ 2 (วินาที)", key="t2", on_change=calculate_tug)
    c3.number_input("ครั้งที่ 3 (วินาที)", key="t3", on_change=calculate_tug)

    # ปุ่ม Reset ที่แก้ไขแล้ว
    st.button("🔄 ล้างค่าเวลาทั้งหมด (Reset)", on_click=reset_tug_callback, type="secondary", use_container_width=True)

    # แสดงผลลัพธ์
    if st.session_state.tug_avg > 0:
        bg_color = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#27AE60"
        st.markdown(f"""
            <div class="result-box" style="background-color: {bg_color};">
                <h3>Average Time: {st.session_state.tug_avg:.2f} s</h3>
                <h1>{st.session_state.tug_status}</h1>
            </div>
        """, unsafe_allow_html=True)