import streamlit as st
import time
import io
from datetime import datetime, date

# ---------------------------------------------------------
# 1. SETUP & MODERN UI STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="Prosthesis Registry", layout="wide", page_icon="🦿")

st.markdown("""
    <style>
    /* Import Font */
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
        background-color: #f8f9fa;
    }

    /* Card Styling */
    .form-card {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e9ecef;
    }

    /* Headers */
    .section-title {
        color: #154360;
        font-size: 1.4em;
        font-weight: bold;
        margin-bottom: 20px;
        border-left: 5px solid #2980B9;
        padding-left: 10px;
    }

    /* TUG Timer */
    .tug-display { 
        font-size: 80px; font-weight: 700; color: #2E86C1; 
        text-align: center; background: white; 
        padding: 40px; border-radius: 20px; margin-bottom: 20px;
        font-family: 'Courier New', monospace;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Result Box */
    .result-box {
        padding: 20px; border-radius: 12px; text-align: center; 
        color: white; font-weight: bold; font-size: 1.2em;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# ---------------------------------------------------------
if 'init' not in st.session_state:
    # Default values matching PDF structure
    defaults = {
        # 1. General Info (PDF Items 1-8)
        'hn': '', 'fname': '', 
        'dob': date(1980, 1, 1), 'age': 0,
        'gender': 'ชาย', 
        'country': 'Thailand', 'country_ot': '',
        'province': 'กรุงเทพมหานคร', 'province_ot': '',
        'nationality': 'ไทย', 'nationality_ot': '',
        'weight': 0.0, 'height': 0.0,
        
        # 2. Medical (PDF Items 9-17)
        'comorbidities': [], 'comorb_ot': '',
        'cause': 'อุบัติเหตุ', 'cause_ot': '',
        'amp_year': 2560, 'side': 'ขวา',
        'level': 'Transtibial', 'level_ot': '',
        'stump_len': 'ปานกลาง', 
        'stump_shape': 'Cylindrical', 'shape_ot': '',
        'surgery': 'ไม่ใช่', 'surg_details': [],
        'k_level': 'K1',
        
        # 3. Rehab (PDF Items 18-19)
        'personnel': [], 'personnel_ot': '',
        'rehab': 'ไม่เคย', 'rehab_act': [], 'rehab_act_ot': '',
        
        # 4. Prosthesis (PDF Items 20-27)
        'service': [], 'service_ot': '',
        'date_cast': date.today(), 'date_deliv': date.today(),
        'socket': 'PTB', 'socket_ot': '',
        'liner': 'None', 'liner_ot': '',
        'suspension': [], 'susp_ot': '',
        'foot': [], 'foot_ot': '',
        'knee': [], 'knee_ot': '', # Only for Transfemoral+
        
        # 5. Social (PDF Items 28-33)
        'assist': 'ไม่ใช้', 'assist_ot': '',
        'stand_hr': '1-3 ชั่วโมง', 'walk_hr': '1-3 ชั่วโมง',
        'fall': 'ไม่', 'fall_freq': '', 'fall_inj': 'ไม่',
        'q31_1': 'ไม่มีปัญหา (0-4%)', 'q31_2': 'ไม่มีปัญหา (0-4%)',
        'q32_1': 'ไม่มีปัญหา (0-4%)', 'q32_2': 'ไม่มีปัญหา (0-4%)',
        'supp_fam': 'ใช่', 'supp_org': 'ไม่ใช่', 
        'supp_src': [], 'supp_src_ot': '',
        
        # TUG
        'tug_running': False, 'start_time': None,
        't1': 0.0, 't2': 0.0, 't3': 0.0, 'tug_avg': 0.0, 'tug_status': '-'
    }
    for k, v in defaults.items():
        st.session_state[k] = v
    st.session_state.init = True

# Helper to get "Other" text
def get_txt(val, ot_key):
    if val == "Other" or val == "อื่นๆ" or (isinstance(val, list) and ("Other" in val or "อื่นๆ" in val)):
        return f"{val} ({st.session_state[ot_key]})"
    return str(val)

# TUG Logic
def calculate_tug():
    times = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0]
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
# 3. HTML REPORT GENERATOR
# ---------------------------------------------------------
def create_html():
    dob = st.session_state.dob.strftime('%d/%m/%Y')
    
    # Calculate Age logic (if needed for display update)
    age_calc = date.today().year - st.session_state.dob.year
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Sarabun', sans-serif; padding: 40px; color: #333; }}
            h1 {{ text-align: center; border-bottom: 2px solid #1F618D; padding-bottom: 10px; color: #1F618D; }}
            .section {{ margin-top: 25px; background: #f8f9fa; padding: 15px; border-radius: 8px; }}
            .sec-head {{ color: #154360; font-weight: bold; font-size: 1.1em; margin-bottom: 10px; border-left: 4px solid #154360; padding-left: 8px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 6px; border-bottom: 1px solid #eee; vertical-align: top; }}
            .lbl {{ font-weight: bold; width: 35%; color: #555; }}
            .tug-box {{ text-align: center; border: 2px solid #1F618D; padding: 15px; margin-top: 20px; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div style="text-align:right; font-size:0.8em;">พิมพ์เมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        <h1>แบบบันทึกข้อมูลกายอุปกรณ์ (Prosthesis Registry)</h1>
        
        <div class="section">
            <div class="sec-head">1. ข้อมูลทั่วไป (General Information)</div>
            <table>
                <tr><td class="lbl">1. วัน/เดือน/ปีเกิด:</td><td>{dob} (อายุ {age_calc} ปี)</td></tr>
                <tr><td class="lbl">2. เพศ:</td><td>{st.session_state.gender}</td></tr>
                <tr><td class="lbl">3. ประเทศที่อยู่อาศัย:</td><td>{get_txt(st.session_state.country, 'country_ot')}</td></tr>
                <tr><td class="lbl">4. จังหวัดที่อยู่อาศัย:</td><td>{get_txt(st.session_state.province, 'province_ot')}</td></tr>
                <tr><td class="lbl">5. สัญชาติ:</td><td>{get_txt(st.session_state.nationality, 'nationality_ot')}</td></tr>
                <tr><td class="lbl">6. HN:</td><td>{st.session_state.hn}</td></tr>
                <tr><td class="lbl">ชื่อ-นามสกุล:</td><td>{st.session_state.fname}</td></tr>
                <tr><td class="lbl">7. น้ำหนัก:</td><td>{st.session_state.weight} กก.</td></tr>
                <tr><td class="lbl">8. ส่วนสูง:</td><td>{st.session_state.height} ซม.</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">2. ข้อมูลทางการแพทย์ (Medical)</div>
            <table>
                <tr><td class="lbl">9. โรคประจำตัว:</td><td>{get_txt(st.session_state.comorbidities, 'comorb_ot')}</td></tr>
                <tr><td class="lbl">10. สาเหตุการตัดขา:</td><td>{get_txt(st.session_state.cause, 'cause_ot')}</td></tr>
                <tr><td class="lbl">11. ปีที่ตัดขา:</td><td>{st.session_state.amp_year}</td></tr>
                <tr><td class="lbl">12. ข้างที่ตัด:</td><td>{st.session_state.side}</td></tr>
                <tr><td class="lbl">13. ระดับการตัดขา:</td><td>{get_txt(st.session_state.level, 'level_ot')}</td></tr>
                <tr><td class="lbl">14-15. ตอขา:</td><td>ยาว: {st.session_state.stump_len}, รูปทรง: {get_txt(st.session_state.stump_shape, 'shape_ot')}</td></tr>
                <tr><td class="lbl">16. ผ่าตัดเพิ่มเติม:</td><td>{st.session_state.surgery} {st.session_state.surg_details}</td></tr>
                <tr><td class="lbl">17. K-Level ก่อนตัด:</td><td>{st.session_state.k_level}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">3-4. การฟื้นฟูและกายอุปกรณ์</div>
            <table>
                <tr><td class="lbl">18. บุคลากร:</td><td>{get_txt(st.session_state.personnel, 'personnel_ot')}</td></tr>
                <tr><td class="lbl">19. การฟื้นฟู:</td><td>{st.session_state.rehab} ({get_txt(st.session_state.rehab_act, 'rehab_act_ot')})</td></tr>
                <tr><td class="lbl">20. การบริการ:</td><td>{get_txt(st.session_state.service, 'service_ot')}</td></tr>
                <tr><td class="lbl">21-22. วันที่:</td><td>หล่อแบบ: {st.session_state.date_cast} / รับ: {st.session_state.date_deliv}</td></tr>
                <tr><td class="lbl">23. Socket:</td><td>{get_txt(st.session_state.socket, 'socket_ot')}</td></tr>
                <tr><td class="lbl">24. Liner:</td><td>{get_txt(st.session_state.liner, 'liner_ot')}</td></tr>
                <tr><td class="lbl">25. Suspension:</td><td>{get_txt(st.session_state.suspension, 'susp_ot')}</td></tr>
                <tr><td class="lbl">26. Foot:</td><td>{get_txt(st.session_state.foot, 'foot_ot')}</td></tr>
                <tr><td class="lbl">27. Knee:</td><td>{get_txt(st.session_state.knee, 'knee_ot')}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">5. สังคมและการใช้งาน</div>
            <table>
                <tr><td class="lbl">28. อุปกรณ์ช่วยเดิน:</td><td>{get_txt(st.session_state.assist, 'assist_ot')}</td></tr>
                <tr><td class="lbl">29. ยืน/เดิน (ต่อวัน):</td><td>{st.session_state.stand_hr} / {st.session_state.walk_hr}</td></tr>
                <tr><td class="lbl">30. ประวัติล้ม:</td><td>{st.session_state.fall} (บาดเจ็บ: {st.session_state.fall_inj})</td></tr>
                <tr><td class="lbl">31. สังคม:</td><td>ตนเอง: {st.session_state.q31_1} / เทียบคนอื่น: {st.session_state.q31_2}</td></tr>
                <tr><td class="lbl">32. งาน:</td><td>ตนเอง: {st.session_state.q32_1} / เทียบคนอื่น: {st.session_state.q32_2}</td></tr>
                <tr><td class="lbl">33. สนับสนุน:</td><td>ครอบครัว: {st.session_state.supp_fam} / องค์กร: {st.session_state.supp_org} ({get_txt(st.session_state.supp_src, 'supp_src_ot')})</td></tr>
            </table>
        </div>

        <div class="tug-box">
            <h3>ผลการทดสอบ TUG</h3>
            <h1>{st.session_state.tug_avg:.2f} s</h1>
            <h2>{st.session_state.tug_status}</h2>
        </div>
    </body>
    </html>
    """
    return html

# ---------------------------------------------------------
# 4. APP LAYOUT
# ---------------------------------------------------------
st.title("🏥 Prosthesis Registry & OM Platform")

# Sidebar
st.sidebar.markdown("### 📥 Report")
html_data = create_html()
st.sidebar.download_button(
    "💾 Download HTML Report",
    data=io.BytesIO(html_data.encode('utf-8')),
    file_name=f"Report_{st.session_state.hn}.html",
    mime="text/html",
    use_container_width=True
)

tab1, tab2 = st.tabs(["📝 Registry Form", "⏱️ TUG Test"])

# --- TAB 1: REGISTRY (Single Column, Card Style) ---
with tab1:
    
    # --- Section 1: General ---
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">1. ข้อมูลทั่วไป (General Info)</div>', unsafe_allow_html=True)
    
    st.date_input("1. วัน/เดือน/ปีเกิด (Date of Birth)", key="dob")
    
    # Auto calc age display
    age_now = date.today().year - st.session_state.dob.year
    st.caption(f"อายุปัจจุบัน: {age_now} ปี")
    
    st.selectbox("2. เพศ (Gender)", ["ชาย", "หญิง"], key="gender")
    
    st.selectbox("3. ประเทศที่อยู่อาศัย", ["Thailand", "Other"], key="country")
    if st.session_state.country == "Other": 
        st.text_input("ระบุประเทศ", key="country_ot")
    
    st.selectbox("4. จังหวัดที่อยู่อาศัย", ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "ภูเก็ต", "Other"], key="province")
    if st.session_state.province == "Other": 
        st.text_input("ระบุจังหวัด", key="province_ot")
    
    st.selectbox("5. สัญชาติ", ["ไทย", "Other"], key="nationality")
    if st.session_state.nationality == "Other": 
        st.text_input("ระบุสัญชาติ", key="nationality_ot")
    
    st.text_input("6. เลขประจำตัวผู้ป่วย (HN)", key="hn")
    st.text_input("ชื่อ-นามสกุล (Name)", key="fname")
    
    st.number_input("7. น้ำหนัก (kg)", 0.0, step=0.1, key="weight")
    st.number_input("8. ส่วนสูง (cm)", 0.0, step=1.0, key="height")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Section 2: Medical ---
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">2. ข้อมูลการตัดขาและสุขภาพ</div>', unsafe_allow_html=True)
    
    st.multiselect("9. โรคประจำตัว", ["เบาหวาน", "ความดัน", "หัวใจ", "มะเร็ง", "ติดเชื้อ", "ไม่มี", "Other"], key="comorbidities")
    if "Other" in st.session_state.comorbidities: 
        st.text_input("ระบุโรค", key="comorb_ot")
    
    st.selectbox("10. สาเหตุการตัดขา", ["อุบัติเหตุ", "เบาหวาน", "หลอดเลือด", "มะเร็ง", "ติดเชื้อ", "พิการแต่กำเนิด", "Other"], key="cause")
    if st.session_state.cause == "Other": 
        st.text_input("ระบุสาเหตุ", key="cause_ot")
    
    st.number_input("11. ปีที่ตัดขา (พ.ศ.)", 2490, 2600, key="amp_year")
    st.radio("12. ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="side")
    
    st.selectbox("13. ระดับการตัดขา", ["Ankle disarticulation", "Transtibial", "Knee disarticulation", "Transfemoral", "Other"], key="level")
    if st.session_state.level == "Other": 
        st.text_input("ระบุระดับ", key="level_ot")
    
    st.selectbox("14. ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"], key="stump_len")
    st.selectbox("15. รูปทรงตอขา", ["Conical", "Cylindrical", "Bulbous", "Other"], key="stump_shape")
    if st.session_state.stump_shape == "Other": 
        st.text_input("ระบุรูปทรง", key="shape_ot")
    
    st.radio("16. ผ่าตัดเพิ่มเติม", ["ไม่ใช่", "ใช่"], horizontal=True, key="surgery")
    if st.session_state.surgery == "ใช่":
        st.multiselect("รายละเอียดการผ่าตัด", ["ตัดกระดูก", "ตัดผิวหนัง", "ตัดระดับสูงขึ้น"], key="surg_details")
    
    st.selectbox("17. K-Level ก่อนตัด", ["K0", "K1", "K2", "K3", "K4"], key="k_level")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Section 3: Rehab ---
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">3. การฟื้นฟู (Rehab)</div>', unsafe_allow_html=True)
    st.multiselect("18. บุคลากรที่ดูแล", ["นักกายอุปกรณ์", "นักกายภาพ", "แพทย์", "พยาบาล", "Other"], key="personnel")
    if "Other" in st.session_state.personnel: 
        st.text_input("ระบุบุคลากร", key="personnel_ot")
    
    st.radio("19. เคยฟื้นฟูหรือไม่", ["ไม่เคย", "เคย"], horizontal=True, key="rehab")
    if st.session_state.rehab == "เคย":
        st.multiselect("กิจกรรม", ["ถุงลดบวม", "ผ้ายืด", "เบ้าซิลิโคน", "ฝึกเดิน", "Other"], key="rehab_act")
        if "Other" in st.session_state.rehab_act: 
            st.text_input("ระบุกิจกรรม", key="rehab_act_ot")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Section 4: Prosthesis ---
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">4. กายอุปกรณ์ (Prosthesis)</div>', unsafe_allow_html=True)
    st.multiselect("20. การบริการครั้งนี้", ["ทำใหม่", "เปลี่ยนเบ้า", "ซ่อม", "Other"], key="service")
    if "Other" in st.session_state.service: 
        st.text_input("ระบุบริการ", key="service_ot")
    
    c1, c2 = st.columns(2)
    with c1: st.date_input("21. วันที่หล่อแบบ", key="date_cast")
    with c2: st.date_input("22. วันที่ได้รับ", key="date_deliv")
    
    st.selectbox("23. Socket Type", ["PTB", "TSB", "KBM", "Quadrilateral", "Ischial Containment", "Other"], key="socket")
    if st.session_state.socket == "Other": 
        st.text_input("ระบุ Socket", key="socket_ot")
    
    st.selectbox("24. Liner", ["None", "Foam", "Silicone", "Gel", "Other"], key="liner")
    if st.session_state.liner == "Other": 
        st.text_input("ระบุ Liner", key="liner_ot")
    
    st.multiselect("25. Suspension", ["Cuff", "Pin Lock", "Suction", "Vacuum", "Belt", "Other"], key="suspension")
    if "Other" in st.session_state.suspension: 
        st.text_input("ระบุ Suspension", key="susp_ot")
    
    st.multiselect("26. Foot", ["SACH", "Single Axis", "Dynamic", "Microprocessor", "Other"], key="foot")
    if "Other" in st.session_state.foot: 
        st.text_input("ระบุ Foot", key="foot_ot")
    
    st.multiselect("27. Knee (สำหรับเหนือเข่า)", ["Single Axis", "Polycentric", "Hydraulic", "Microprocessor", "Other"], key="knee")
    if "Other" in st.session_state.knee: 
        st.text_input("ระบุ Knee", key="knee_ot")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Section 5: Social ---
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">5. สังคมและการใช้งาน</div>', unsafe_allow_html=True)
    st.selectbox("28. อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "ไม้เท้า", "Walker", "Wheelchair", "Other"], key="assist")
    if st.session_state.assist == "Other": 
        st.text_input("ระบุอุปกรณ์", key="assist_ot")
    
    st.selectbox("29.1 เวลายืนต่อวัน", ["ไม่ยืน", "< 1 ชม.", "1-3 ชม.", "3-7 ชม.", "> 8 ชม."], key="stand_hr")
    st.selectbox("29.2 เวลาเดินต่อวัน", ["ไม่เดิน", "< 1 ชม.", "1-3 ชม.", "3-7 ชม.", "> 8 ชม."], key="walk_hr")
    
    st.radio("30. ประวัติล้ม (6 เดือน)", ["ไม่", "มี"], horizontal=True, key="fall")
    if st.session_state.fall == "มี":
        st.selectbox("ความถี่การล้ม", ["< 1 ครั้ง", "1-2 ครั้ง", "3-4 ครั้ง", "> 4 ครั้ง"], key="fall_freq")
        st.radio("บาดเจ็บหรือไม่", ["ไม่", "ใช่"], horizontal=True, key="fall_inj")
    
    st.markdown("---")
    probs = ["ไม่มีปัญหา (0-4%)", "เล็กน้อย (5-24%)", "ปานกลาง (25-49%)", "มาก (50-95%)", "มากที่สุด (96-100%)"]
    st.selectbox("31.1 ปัญหาสังคม (เทียบตนเอง)", probs, key="q31_1")
    st.selectbox("31.2 ปัญหาสังคม (เทียบคนอื่น)", probs, key="q31_2")
    st.selectbox("32.1 ปัญหางาน (เทียบตนเอง)", probs, key="q32_1")
    st.selectbox("32.2 ปัญหางาน (เทียบคนอื่น)", probs, key="q32_2")
    
    st.markdown("---")
    st.radio("33.1 การดูแลจากครอบครัว", ["ใช่", "ไม่ใช่"], horizontal=True, key="supp_fam")
    st.radio("33.2 สนับสนุนจากองค์กร", ["ไม่ใช่", "ใช่"], horizontal=True, key="supp_org")
    if st.session_state.supp_org == "ใช่":
        st.multiselect("ระบุองค์กร", ["รัฐ", "ไม่แสวงหากำไร", "จ่ายเอง", "Other"], key="supp_src")
        if "Other" in st.session_state.supp_src: 
            st.text_input("ระบุองค์กรอื่น", key="supp_src_ot")
    st.markdown('</div>', unsafe_allow_html=True)

# === TAB 2: TUG TEST ===
with tab2:
    st.markdown('<div class="form-card" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align:center; border:none;">⏱️ Timed Up and Go Test</div>', unsafe_allow_html=True)
    
    if st.session_state.tug_running:
        elapsed = time.time() - st.session_state.start_time
        st.markdown(f'<div class="tug-display">{elapsed:.2f} s</div>', unsafe_allow_html=True)
        if st.button("⏹️ STOP", type="primary", use_container_width=True):
            st.session_state.tug_running = False
            fin = elapsed
            if st.session_state.t1 == 0: st.session_state.t1 = fin
            elif st.session_state.t2 == 0: st.session_state.t2 = fin
            elif st.session_state.t3 == 0: st.session_state.t3 = fin
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
    c1, c2, c3 = st.columns(3)
    # FIX: Cleaned up st.number_input to avoid duplicate logic error
    st.number_input("Trial 1", key="t1", on_change=calculate_tug)
    st.number_input("Trial 2", key="t2", on_change=calculate_tug)
    st.number_input("Trial 3", key="t3", on_change=calculate_tug)
    
    st.button("🔄 Reset Timer", on_click=reset_tug, use_container_width=True)
    
    if st.session_state.tug_avg > 0:
        bg = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#27AE60"
        st.markdown(f"""
        <div class="result-box" style="background:{bg};">
            <div>Average Time: {st.session_state.tug_avg:.2f} s</div>
            <div style="font-size:1.5em; margin-top:5px;">{st.session_state.tug_status}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)