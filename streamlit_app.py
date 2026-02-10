import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io

# ---------------------------------------------------------
# 1. SETUP & STYLE
# ---------------------------------------------------------
st.set_page_config(page_title="Prosthesis Registry & TUG", layout="wide", page_icon="🦿")

# CSS ตกแต่งให้ดูสะอาดตาและซ่อน Footer
st.markdown("""
    <style>
    .big-font { font-size: 24px !important; font-weight: bold; }
    .tug-display { 
        font-size: 60px; 
        font-weight: bold; 
        color: #2E86C1; 
        text-align: center;
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stButton button { height: 3em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SESSION STATE MANAGEMENT (ระบบจดจำค่า)
# ---------------------------------------------------------
# ค่าเริ่มต้นทั้งหมด (ป้องกันข้อมูลหาย)
default_values = {
    # General
    'hn': '', 'fname': '', 'gender': 'ชาย', 'age': 0, 
    'weight': 0.0, 'height': 0.0, 'province': 'กรุงเทพมหานคร',
    # Medical
    'cause': 'อุบัติเหตุ', 'side': 'ขวา', 'level': 'Transtibial', 
    'k_level': 'K1', 'comorbidities': [],
    # Prosthesis
    'socket': 'PTB', 'suspension': 'Pin Lock', 'foot': 'SACH',
    # TUG Data
    'tug_running': False, 'start_time': None,
    't1': 0.00, 't2': 0.00, 't3': 0.00,
    'tug_avg': 0.00, 'tug_status': '-'
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------
# 3. FUNCTIONS (ระบบทำงานเบื้องหลัง)
# ---------------------------------------------------------

def calculate_tug():
    """คำนวณผล TUG"""
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

def create_html_report():
    """สร้างรายงาน HTML สำหรับพิมพ์"""
    html = f"""
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Sarabun', sans-serif; padding: 30px; }}
            h1 {{ text-align: center; color: #333; }}
            .section {{ margin-top: 20px; border-bottom: 1px solid #ccc; padding-bottom: 10px; }}
            .header {{ font-size: 18px; font-weight: bold; color: #154360; margin-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 8px; border-bottom: 1px solid #eee; }}
            .label {{ font-weight: bold; width: 30%; }}
            .tug-box {{ text-align: center; padding: 15px; background: #eee; margin-top: 20px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>📄 รายงานผลการประเมิน (Prosthesis Report)</h1>
        <div style="text-align: right; color: gray; font-size: 12px;">Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>

        <div class="section">
            <div class="header">1. ข้อมูลทั่วไป (General Info)</div>
            <table>
                <tr><td class="label">HN:</td><td>{st.session_state.hn}</td></tr>
                <tr><td class="label">ชื่อ-สกุล:</td><td>{st.session_state.fname}</td></tr>
                <tr><td class="label">เพศ / อายุ:</td><td>{st.session_state.gender} / {st.session_state.age} ปี</td></tr>
                <tr><td class="label">ที่อยู่:</td><td>{st.session_state.province}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="header">2. ข้อมูลการแพทย์ (Medical)</div>
            <table>
                <tr><td class="label">สาเหตุ / ระดับ:</td><td>{st.session_state.cause} / {st.session_state.level} ({st.session_state.side})</td></tr>
                <tr><td class="label">K-Level:</td><td>{st.session_state.k_level}</td></tr>
                <tr><td class="label">โรคประจำตัว:</td><td>{", ".join(st.session_state.comorbidities) if st.session_state.comorbidities else "-"}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="header">3. กายอุปกรณ์ (Prosthesis)</div>
            <table>
                <tr><td class="label">Socket:</td><td>{st.session_state.socket}</td></tr>
                <tr><td class="label">Suspension:</td><td>{st.session_state.suspension}</td></tr>
                <tr><td class="label">Foot:</td><td>{st.session_state.foot}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="header">4. ผลทดสอบการเดิน (TUG Test)</div>
            <table>
                <tr><td class="label">Times:</td><td>{st.session_state.t1} / {st.session_state.t2} / {st.session_state.t3} วินาที</td></tr>
            </table>
            <div class="tug-box">
                <h2>เฉลี่ย (Average): {st.session_state.tug_avg:.2f} วินาที</h2>
                <h3>ผลการประเมิน: {st.session_state.tug_status}</h3>
            </div>
        </div>
        
        <script>window.print();</script>
    </body>
    </html>
    """
    return html

# ---------------------------------------------------------
# 4. UI LAYOUT (หน้าจอใช้งาน)
# ---------------------------------------------------------

st.title("🏥 Digital Prosthesis Registry")

# Sidebar: ปุ่มพิมพ์และดาวน์โหลด
st.sidebar.header("🖨️ จัดการรายงาน")
if st.sidebar.button("👁️ พิมพ์รายงาน (Print)", type="primary"):
    if st.session_state.hn == "":
        st.sidebar.error("⚠️ กรุณากรอก HN ก่อนพิมพ์")
    else:
        # ใช้ dialog เพื่อแยกหน้าต่างพิมพ์ ไม่ให้กวนหน้าหลัก
        @st.dialog("ตัวอย่างรายงาน")
        def show_preview():
            st.components.v1.html(create_html_report(), height=600, scrolling=True)
        show_preview()

# ปุ่มดาวน์โหลด (แก้ Bug File Not Found)
html_data = create_html_report()
st.sidebar.download_button(
    label="💾 ดาวน์โหลด HTML",
    data=io.BytesIO(html_data.encode('utf-8')), # แปลงเป็น Bytes ป้องกัน Error
    file_name=f"Report_{st.session_state.hn if st.session_state.hn else 'Unknown'}.html",
    mime="text/html"
)

# Tabs แบ่งหน้าจอให้ชัดเจน
tab1, tab2 = st.tabs(["📝 1. บันทึกข้อมูล (Registry)", "⏱️ 2. จับเวลาเดิน (TUG Test)"])

# --- TAB 1: REGISTRY ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ข้อมูลส่วนตัว")
        st.text_input("HN (รหัสผู้ป่วย)", key="hn")
        st.text_input("ชื่อ-นามสกุล", key="fname")
        c_a, c_b = st.columns(2)
        c_a.selectbox("เพศ", ["ชาย", "หญิง"], key="gender")
        c_b.number_input("อายุ (ปี)", min_value=0, key="age")
        st.selectbox("จังหวัด", ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "อื่นๆ"], key="province")
    
    with col2:
        st.subheader("ข้อมูลการแพทย์")
        st.selectbox("สาเหตุการตัดขา", ["อุบัติเหตุ", "เบาหวาน", "มะเร็ง", "อื่นๆ"], key="cause")
        st.selectbox("ระดับการตัด", ["Transtibial (ใต้เข่า)", "Transfemoral (เหนือเข่า)", "Syme"], key="level")
        st.radio("ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="side")
        st.multiselect("โรคประจำตัว", ["เบาหวาน", "ความดัน", "โรคหัวใจ"], key="comorbidities")
        st.markdown("---")
        st.subheader("ส่วนประกอบขาเทียม")
        c_x, c_y = st.columns(2)
        c_x.selectbox("Socket", ["PTB", "TSB", "Other"], key="socket")
        c_y.selectbox("Suspension", ["Pin Lock", "Suction", "Belt"], key="suspension")
        st.selectbox("Foot (เท้าเทียม)", ["SACH", "Single Axis", "Dynamic Carbon"], key="foot")

# --- TAB 2: TUG TEST ---
with tab2:
    st.header("⏱️ Timed Up and Go Test")
    
    # ส่วนแสดงผลนาฬิกา
    if st.session_state.tug_running:
        # คำนวณเวลาสด
        elapsed = time.time() - st.session_state.start_time
        st.markdown(f'<div class="tug-display">{elapsed:.2f} s</div>', unsafe_allow_html=True)
        
        # ปุ่มหยุด
        if st.button("⏹️ STOP (หยุด)", type="primary", use_container_width=True):
            st.session_state.tug_running = False
            # บันทึกเวลาลงช่องว่างอัตโนมัติ
            final_time = elapsed
            if st.session_state.t1 == 0: st.session_state.t1 = final_time
            elif st.session_state.t2 == 0: st.session_state.t2 = final_time
            elif st.session_state.t3 == 0: st.session_state.t3 = final_time
            calculate_tug() # คำนวณผลใหม่
            st.rerun()
            
        # สั่งให้หน้ารีเฟรชเพื่อให้นาฬิกาเดิน (เฉพาะตอนจับเวลาเท่านั้น)
        time.sleep(0.1)
        st.rerun()
        
    else:
        # นาฬิกาหยุดนิ่ง
        st.markdown(f'<div class="tug-display" style="color:#aaa;">0.00 s</div>', unsafe_allow_html=True)
        if st.button("▶️ START (เริ่มจับเวลา)", type="secondary", use_container_width=True):
            st.session_state.start_time = time.time()
            st.session_state.tug_running = True
            st.rerun()

    st.markdown("---")
    
    # ตารางบันทึกผล 3 ครั้ง
    c1, c2, c3 = st.columns(3)
    t1_in = c1.number_input("ครั้งที่ 1 (วินาที)", key="t1", on_change=calculate_tug)
    t2_in = c2.number_input("ครั้งที่ 2 (วินาที)", key="t2", on_change=calculate_tug)
    t3_in = c3.number_input("ครั้งที่ 3 (วินาที)", key="t3", on_change=calculate_tug)

    # ปุ่ม Reset
    if st.button("🔄 ล้างค่าเวลาทั้งหมด"):
        st.session_state.t1 = 0.0
        st.session_state.t2 = 0.0
        st.session_state.t3 = 0.0
        st.session_state.tug_avg = 0.0
        st.session_state.tug_status = "-"
        st.rerun()

    # ผลลัพธ์
    if st.session_state.tug_avg > 0:
        color = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#27AE60"
        st.markdown(f"""
        <div style="background-color: {color}; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px;">
            <h2>Average: {st.session_state.tug_avg:.2f} s</h2>
            <h1>{st.session_state.tug_status}</h1>
        </div>
        """, unsafe_allow_html=True)