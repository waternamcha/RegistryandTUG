import streamlit as st
import time
import io
import pandas as pd
import os
from datetime import datetime, date

# ---------------------------------------------------------
# 1. SETUP & STYLE
# ---------------------------------------------------------
st.set_page_config(page_title="Prosthesis Registry", layout="wide", page_icon="🦿")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    
    .main-title { text-align: center; font-size: 2.2em; font-weight: 700; color: #154360; margin-bottom: 5px; }
    .sub-title { text-align: center; font-size: 1.0em; color: #5D6D7E; margin-bottom: 20px; }
    
    /* TUG Timer */
    .tug-display { 
        font-size: 80px; font-weight: 700; color: #2E86C1; 
        text-align: center; background-color: #f4f6f7; 
        padding: 30px; border-radius: 20px; margin-bottom: 20px;
        border: 3px solid #d6eaf8;
    }
    
    /* Result Box */
    .result-box {
        padding: 20px; border-radius: 15px; text-align: center; 
        color: white; font-weight: bold; font-size: 1.3em;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-top: 15px;
    }
    
    /* Mobile Fixes */
    @media (max-width: 600px) {
        .main-title { font-size: 1.5em; }
        .tug-display { font-size: 50px; padding: 15px; }
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS & STATE
# ---------------------------------------------------------
if 'init' not in st.session_state:
    # กำหนดค่าเริ่มต้นให้ตัวแปรทั้งหมด
    defaults = {
        # 1. General
        'hn': '', 'fname': '', 'dob': date(1980, 1, 1), 
        'gender': 'ชาย', 'country': 'Thailand', 'country_ot': '',
        'province': 'กรุงเทพมหานคร', 'province_ot': '',
        'nationality': 'ไทย', 'nationality_ot': '',
        'weight': 0.0, 'height': 0.0,
        # 2. Medical
        'comorbidities': [], 'comorb_ot': '',
        'cause': 'อุบัติเหตุ', 'cause_ot': '',
        'amp_year': 2560, 'side': 'ขวา', 
        'level': 'Transtibial', 'level_ot': '',
        'stump_len': 'ปานกลาง', 'stump_shape': 'Cylindrical', 'shape_ot': '',
        'surgery': 'ไม่ใช่', 'surg_details': [], 'k_level': 'K1',
        # 3. Rehab
        'personnel': [], 'personnel_ot': '',
        'rehab': 'ไม่เคย', 'rehab_act': [], 'rehab_act_ot': '',
        # 4. Prosthesis
        'service': [], 'service_ot': '',
        'date_cast': date.today(), 'date_deliv': date.today(),
        'socket': 'PTB', 'socket_ot': '',
        'liner': 'None', 'liner_ot': '',
        'suspension': [], 'susp_ot': '',
        'foot': [], 'foot_ot': '',
        'knee': [], 'knee_ot': '', 
        # 5. Social
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
    st.session_state.init = True

# ฟังก์ชันแปลงค่าสำหรับใส่ใน CSV/Report (แก้ปัญหา [])
def fmt_report(key, ot_key=None):
    val = st.session_state.get(key, '-')
    
    # กรณีเป็น List (Multiselect)
    if isinstance(val, list):
        if not val: return "-"
        text = ", ".join(val)
        if ot_key and ("Other" in val or "อื่นๆ" in val):
            other_txt = st.session_state.get(ot_key, '')
            text += f" ({other_txt})"
        return text
    
    # กรณีเป็น String ทั่วไป
    if ot_key and (val == "Other" or val == "อื่นๆ"):
        other_txt = st.session_state.get(ot_key, '')
        return f"{val} ({other_txt})"
    
    return str(val) if val else "-"

# คำนวณ TUG
def calculate_tug():
    times = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0]
    if times:
        avg = sum(times) / len(times)
        st.session_state.tug_avg = avg
        st.session_state.tug_status = "⚠️ High Fall Risk" if avg >= 13.5 else "✅ Normal Mobility"
    else:
        st.session_state.tug_avg = 0.0
        st.session_state.tug_status = "-"

# รีเซ็ต TUG
def reset_tug():
    st.session_state.t1 = 0.0
    st.session_state.t2 = 0.0
    st.session_state.t3 = 0.0
    st.session_state.tug_avg = 0.0
    st.session_state.tug_status = "-"
    st.session_state.tug_running = False

# ---------------------------------------------------------
# 3. HTML REPORT GENERATION (FULL VERSION)
# ---------------------------------------------------------
def create_html():
    dob = st.session_state.dob.strftime('%d/%m/%Y')
    age = date.today().year - st.session_state.dob.year
    date_cast = st.session_state.date_cast.strftime('%d/%m/%Y')
    date_deliv = st.session_state.date_deliv.strftime('%d/%m/%Y')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Report_{st.session_state.hn}</title>
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Sarabun', sans-serif; padding: 20px; color: #333; }}
            h1 {{ text-align: center; color: #1F618D; font-size: 1.4em; margin-bottom: 5px; }}
            .sub {{ text-align: center; color: #777; font-size: 0.9em; margin-bottom: 20px; }}
            .section {{ margin-top: 15px; background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
            .sec-head {{ background: #154360; color: white; padding: 8px; font-weight: bold; border-radius: 4px; font-size: 1em; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 5px; }}
            td {{ padding: 5px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 0.9em; }}
            .lbl {{ font-weight: bold; width: 40%; color: #444; }}
            .val {{ color: #000; }}
            .tug-box {{ text-align: center; border: 2px solid #1F618D; padding: 10px; margin-top: 15px; border-radius: 8px; background: #f4f6f7; }}
        </style>
    </head>
    <body>
        <h1>แบบบันทึกข้อมูลกายอุปกรณ์ (Prosthesis Registry)</h1>
        <div class="sub">พิมพ์เมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>

        <div class="section">
            <div class="sec-head">1. ข้อมูลทั่วไป</div>
            <table>
                <tr><td class="lbl">HN:</td><td class="val">{st.session_state.hn}</td></tr>
                <tr><td class="lbl">ชื่อ-นามสกุล:</td><td class="val">{st.session_state.fname}</td></tr>
                <tr><td class="lbl">วันเกิด (อายุ):</td><td class="val">{dob} ({age} ปี)</td></tr>
                <tr><td class="lbl">เพศ:</td><td class="val">{st.session_state.gender}</td></tr>
                <tr><td class="lbl">ที่อยู่ (จังหวัด/ปท.):</td><td class="val">{fmt_report('province', 'province_ot')} / {fmt_report('country', 'country_ot')}</td></tr>
                <tr><td class="lbl">สัญชาติ:</td><td class="val">{fmt_report('nationality', 'nationality_ot')}</td></tr>
                <tr><td class="lbl">น้ำหนัก/ส่วนสูง:</td><td class="val">{st.session_state.weight} กก. / {st.session_state.height} ซม.</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">2. ข้อมูลการตัดขาและสุขภาพ</div>
            <table>
                <tr><td class="lbl">โรคประจำตัว:</td><td class="val">{fmt_report('comorbidities', 'comorb_ot')}</td></tr>
                <tr><td class="lbl">สาเหตุการตัดขา:</td><td class="val">{fmt_report('cause', 'cause_ot')}</td></tr>
                <tr><td class="lbl">ปีที่ตัด/ข้าง:</td><td class="val">{st.session_state.amp_year} / {st.session_state.side}</td></tr>
                <tr><td class="lbl">ระดับการตัดขา:</td><td class="val">{fmt_report('level', 'level_ot')}</td></tr>
                <tr><td class="lbl">ลักษณะตอขา (ยาว/รูปทรง):</td><td class="val">{st.session_state.stump_len} / {fmt_report('stump_shape', 'shape_ot')}</td></tr>
                <tr><td class="lbl">ประวัติผ่าตัดเพิ่มเติม:</td><td class="val">{st.session_state.surgery} {fmt_report('surg_details') if st.session_state.surgery=='ใช่' else ''}</td></tr>
                <tr><td class="lbl">K-Level (ก่อนตัด):</td><td class="val">{st.session_state.k_level}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">3. การฟื้นฟู (Rehab)</div>
            <table>
                <tr><td class="lbl">บุคลากรที่ดูแล:</td><td class="val">{fmt_report('personnel', 'personnel_ot')}</td></tr>
                <tr><td class="lbl">ประวัติการฟื้นฟู:</td><td class="val">{st.session_state.rehab}</td></tr>
                <tr><td class="lbl">กิจกรรมที่ทำ:</td><td class="val">{fmt_report('rehab_act', 'rehab_act_ot')}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">4. ข้อมูลกายอุปกรณ์</div>
            <table>
                <tr><td class="lbl">บริการครั้งนี้:</td><td class="val">{fmt_report('service', 'service_ot')}</td></tr>
                <tr><td class="lbl">วันที่ หล่อ/รับ:</td><td class="val">{date_cast} - {date_deliv}</td></tr>
                <tr><td class="lbl">Socket:</td><td class="val">{fmt_report('socket', 'socket_ot')}</td></tr>
                <tr><td class="lbl">Liner:</td><td class="val">{fmt_report('liner', 'liner_ot')}</td></tr>
                <tr><td class="lbl">Suspension:</td><td class="val">{fmt_report('suspension', 'susp_ot')}</td></tr>
                <tr><td class="lbl">Foot:</td><td class="val">{fmt_report('foot', 'foot_ot')}</td></tr>
                <tr><td class="lbl">Knee (ถ้ามี):</td><td class="val">{fmt_report('knee', 'knee_ot')}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">5. สังคมและการใช้งาน</div>
            <table>
                <tr><td class="lbl">อุปกรณ์ช่วยเดิน:</td><td class="val">{fmt_report('assist', 'assist_ot')}</td></tr>
                <tr><td class="lbl">เวลายืน/เดิน (ต่อวัน):</td><td class="val">{st.session_state.stand_hr} / {st.session_state.walk_hr}</td></tr>
                <tr><td class="lbl">ประวัติล้ม (6 เดือน):</td><td class="val">{st.session_state.fall} {f"(ความถี่: {st.session_state.fall_freq}, บาดเจ็บ: {st.session_state.fall_inj})" if st.session_state.fall=='มี' else ''}</td></tr>
                <tr><td class="lbl">ปัญหาสังคม (ตนเอง/คนอื่น):</td><td class="val">{st.session_state.q31_1} / {st.session_state.q31_2}</td></tr>
                <tr><td class="lbl">ปัญหางาน (ตนเอง/คนอื่น):</td><td class="val">{st.session_state.q32_1} / {st.session_state.q32_2}</td></tr>
                <tr><td class="lbl">การสนับสนุน:</td><td class="val">ครอบครัว: {st.session_state.supp_fam} / องค์กร: {st.session_state.supp_org}</td></tr>
                 <tr><td class="lbl">แหล่งทุน (ถ้ามี):</td><td class="val">{fmt_report('supp_src', 'supp_src_ot')}</td></tr>
            </table>
        </div>

        <div class="tug-box">
            <h3>ผลทดสอบ TUG Test</h3>
            <h1 style="font-size:2.5em; margin:0;">{st.session_state.tug_avg:.2f} s</h1>
            <h3 style="margin:5px 0;">{st.session_state.tug_status}</h3>
            <p style="font-size:0.8em; color:#666;">(1: {st.session_state.t1:.2f}s, 2: {st.session_state.t2:.2f}s, 3: {st.session_state.t3:.2f}s)</p>
        </div>
    </body>
    </html>
    """
    return html

def save_to_csv():
    if st.session_state.hn == "":
        st.toast('⚠️ ไม่ได้บันทึก: กรุณากรอก HN ก่อน', icon='⚠️')
        return

    # ใช้ฟังก์ชัน fmt_report ช่วย clean data ให้ CSV อ่านง่าย
    data = {
        'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'HN': [st.session_state.hn], 'Name': [st.session_state.fname],
        'Gender': [st.session_state.gender], 'Age': [date.today().year - st.session_state.dob.year],
        'Diagnosis': [fmt_report('cause', 'cause_ot')],
        'Amp_Level': [fmt_report('level', 'level_ot')],
        'K_Level': [st.session_state.k_level],
        'Socket': [fmt_report('socket', 'socket_ot')],
        'Foot': [fmt_report('foot', 'foot_ot')],
        'TUG_Avg': [st.session_state.tug_avg],
        'TUG_Status': [st.session_state.tug_status],
        # ใส่ Field อื่นๆ ที่เหลือตามต้องการได้ตรงนี้...
    }
    
    df = pd.DataFrame(data)
    file_path = 'prosthesis_database.csv'
    
    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    else:
        try:
            df.to_csv(file_path, mode='a', header=False, index=False, encoding='utf-8-sig')
        except:
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    st.toast(f'✅ บันทึก HN: {st.session_state.hn} เรียบร้อย!', icon='💾')

# ---------------------------------------------------------
# 4. MAIN LAYOUT
# ---------------------------------------------------------
html_data = create_html()

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-title">🏥 Digital Prosthesis Registry</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">ระบบบันทึกข้อมูลกายอุปกรณ์และทดสอบการเดิน</div>', unsafe_allow_html=True)

with col2:
    st.write("")
    st.write("")
    st.download_button("📥 Download Report", data=html_data, file_name=f"Report_{st.session_state.hn}.html", mime="text/html", type="primary", use_container_width=True, on_click=save_to_csv)

st.sidebar.title("เมนูหลัก")
st.sidebar.download_button("📊 Download Database (CSV)", data=pd.read_csv('prosthesis_database.csv').to_csv(index=False).encode('utf-8-sig') if os.path.exists('prosthesis_database.csv') else "", file_name="prosthesis_database.csv", mime="text/csv", disabled=not os.path.exists('prosthesis_database.csv'))

# --- Tabs ---
tab1, tab2 = st.tabs(["📝 แบบฟอร์มบันทึก", "⏱️ TUG Test"])

with tab1:
    with st.expander("1. ข้อมูลทั่วไป", expanded=True):
        c1, c2 = st.columns(2)
        with c1: st.text_input("HN", key="hn")
        with c2: st.text_input("ชื่อ-นามสกุล", key="fname")
        st.date_input("วันเกิด", key="dob")
        st.radio("เพศ", ["ชาย", "หญิง"], horizontal=True, key="gender")
        st.selectbox("จังหวัด", ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "Other"], key="province")
        if st.session_state.province == "Other": st.text_input("ระบุจังหวัด", key="province_ot")
        st.number_input("น้ำหนัก (kg)", 0.0, key="weight")
        st.number_input("ส่วนสูง (cm)", 0.0, key="height")

    with st.expander("2. ข้อมูลการตัดขาและสุขภาพ"):
        st.multiselect("โรคประจำตัว", ["เบาหวาน", "ความดัน", "หัวใจ", "ไม่มี", "Other"], key="comorbidities")
        if "Other" in st.session_state.comorbidities: st.text_input("ระบุโรค", key="comorb_ot")
        st.selectbox("สาเหตุ", ["อุบัติเหตุ", "เบาหวาน", "มะเร็ง", "Other"], key="cause")
        if st.session_state.cause == "Other": st.text_input("ระบุสาเหตุ", key="cause_ot")
        st.number_input("ปีที่ตัดขา (พ.ศ.)", 2490, 2600, key="amp_year")
        st.radio("ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="side")
        st.selectbox("ระดับ", ["Transtibial", "Transfemoral", "Knee Disarticulation", "Other"], key="level")
        if st.session_state.level == "Other": st.text_input("ระบุระดับ", key="level_ot")
        st.selectbox("ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"], key="stump_len")
        st.selectbox("รูปทรง", ["Cylindrical", "Conical", "Bulbous", "Other"], key="stump_shape")
        if st.session_state.stump_shape == "Other": st.text_input("ระบุรูปทรง", key="shape_ot")
        st.radio("ผ่าตัดเพิ่มเติม", ["ไม่ใช่", "ใช่"], horizontal=True, key="surgery")
        if st.session_state.surgery == "ใช่": st.multiselect("รายละเอียด", ["ตัดกระดูก", "ตัดผิวหนัง"], key="surg_details")
        st.selectbox("K-Level", ["K0", "K1", "K2", "K3", "K4"], key="k_level")

    with st.expander("3. การฟื้นฟู (Rehab)"):
        st.multiselect("บุคลากร", ["นักกายอุปกรณ์", "นักกายภาพ", "แพทย์", "Other"], key="personnel")
        if "Other" in st.session_state.personnel: st.text_input("ระบุบุคลากร", key="personnel_ot")
        st.radio("เคยฟื้นฟูหรือไม่", ["ไม่เคย", "เคย"], horizontal=True, key="rehab")
        if st.session_state.rehab == "เคย":
            st.multiselect("กิจกรรม", ["ถุงลดบวม", "ผ้ายืด", "ฝึกเดิน", "Other"], key="rehab_act")
            if "Other" in st.session_state.rehab_act: st.text_input("ระบุกิจกรรม", key="rehab_act_ot")

    with st.expander("4. กายอุปกรณ์"):
        st.multiselect("บริการ", ["ทำใหม่", "ซ่อม", "เปลี่ยนอะไหล่", "Other"], key="service")
        if "Other" in st.session_state.service: st.text_input("ระบุบริการ", key="service_ot")
        c1, c2 = st.columns(2)
        with c1: st.date_input("วันที่หล่อ", key="date_cast")
        with c2: st.date_input("วันที่รับ", key="date_deliv")
        st.selectbox("Socket", ["PTB", "TSB", "Other"], key="socket")
        if st.session_state.socket == "Other": st.text_input("ระบุ Socket", key="socket_ot")
        st.selectbox("Liner", ["None", "Foam", "Silicone", "Other"], key="liner")
        if st.session_state.liner == "Other": st.text_input("ระบุ Liner", key="liner_ot")
        st.multiselect("Suspension", ["Cuff", "Pin Lock", "Suction", "Other"], key="suspension")
        if "Other" in st.session_state.suspension: st.text_input("ระบุ Suspension", key="susp_ot")
        st.multiselect("Foot", ["SACH", "Single Axis", "Dynamic", "Other"], key="foot")
        if "Other" in st.session_state.foot: st.text_input("ระบุ Foot", key="foot_ot")
        st.multiselect("Knee (ถ้ามี)", ["Single Axis", "Polycentric", "Hydraulic", "Other"], key="knee")
        if "Other" in st.session_state.knee: st.text_input("ระบุ Knee", key="knee_ot")

    with st.expander("5. สังคมและการใช้งาน"):
        st.selectbox("อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "ไม้เท้า", "Walker", "Wheelchair", "Other"], key="assist")
        if st.session_state.assist == "Other": st.text_input("ระบุอุปกรณ์", key="assist_ot")
        st.selectbox("เวลายืนต่อวัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="stand_hr")
        st.selectbox("เวลาเดินต่อวัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="walk_hr")
        st.radio("ประวัติล้ม (6 เดือน)", ["ไม่", "มี"], horizontal=True, key="fall")
        if st.session_state.fall == "มี":
            st.selectbox("ความถี่", ["1-2 ครั้ง", "> 2 ครั้ง"], key="fall_freq")
            st.radio("บาดเจ็บ", ["ไม่", "ใช่"], horizontal=True, key="fall_inj")
        st.markdown("---")
        probs = ["ไม่มี (0-4%)", "เล็กน้อย (5-24%)", "ปานกลาง (25-49%)", "มาก (50-95%)", "มากที่สุด (96-100%)"]
        st.selectbox("ปัญหาสังคม (ตนเอง)", probs, key="q31_1")
        st.selectbox("ปัญหาสังคม (เทียบคนอื่น)", probs, key="q31_2")
        st.selectbox("ปัญหางาน (ตนเอง)", probs, key="q32_1")
        st.selectbox("ปัญหางาน (เทียบคนอื่น)", probs, key="q32_2")
        st.markdown("---")
        st.radio("ครอบครัวดูแล", ["ใช่", "ไม่ใช่"], horizontal=True, key="supp_fam")
        st.radio("องค์กรสนับสนุน", ["ไม่ใช่", "ใช่"], horizontal=True, key="supp_org")
        if st.session_state.supp_org == "ใช่":
            st.multiselect("แหล่งทุน", ["รัฐ", "เอกชน", "จ่ายเอง", "Other"], key="supp_src")
            if "Other" in st.session_state.supp_src: st.text_input("ระบุแหล่งทุน", key="supp_src_ot")

with tab2:
    st.markdown('<div class="main-title">⏱️ TUG Test</div>', unsafe_allow_html=True)
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
    st.number_input("ครั้งที่ 1 (วินาที)", key="t1", on_change=calculate_tug)
    st.number_input("ครั้งที่ 2 (วินาที)", key="t2", on_change=calculate_tug)
    st.number_input("ครั้งที่ 3 (วินาที)", key="t3", on_change=calculate_tug)
    
    st.button("🔄 ล้างค่าเวลาทั้งหมด", on_click=reset_tug, use_container_width=True)

    if st.session_state.tug_avg > 0:
        bg = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#27AE60"
        st.markdown(f"""
        <div class="result-box" style="background:{bg};">
            <div>เฉลี่ย: {st.session_state.tug_avg:.2f} วินาที</div>
            <div style="font-size:1.5em; margin-top:5px;">{st.session_state.tug_status}</div>
        </div>
        """, unsafe_allow_html=True)