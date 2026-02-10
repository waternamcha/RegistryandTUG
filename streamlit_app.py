import streamlit as st
import time
import pandas as pd
import os
from datetime import datetime, date

# ---------------------------------------------------------
# 1. SETUP & INITIALIZATION (ต้องอยู่บนสุด!)
# ---------------------------------------------------------
st.set_page_config(page_title="Prosthesis Registry", layout="wide", page_icon="🦿")

# ฟังก์ชันตั้งค่าเริ่มต้นตัวแปร (ป้องกัน Error จอแดง)
def init_state():
    defaults = {
        # 1. General
        'hn': '', 'fname': '', 'dob': date(1980, 1, 1), 
        'gender': 'ชาย', 
        'country': 'Thailand', 'country_ot': '',
        'province': 'กรุงเทพมหานคร', 'province_ot': '',
        'nationality': 'ไทย', 'nationality_ot': '',
        'weight': 0.0, 'height': 0.0,
        
        # 2. Medical
        'comorbidities': [], 'comorb_ot': '',
        'cause': 'อุบัติเหตุ', 'cause_ot': '',
        'amp_year': 2560, 'side': 'ขวา', 
        'level': 'Transtibial', 'level_ot': '',
        'stump_len': 'ปานกลาง', 
        'stump_shape': 'Cylindrical', 'shape_ot': '',
        'surgery': 'ไม่ใช่', 'surg_details': [],
        'k_level': 'K1',
        
        # 3. Rehab
        'personnel': [], 'personnel_ot': '',
        'rehab': 'ไม่เคย', 
        'rehab_act': [], 'rehab_act_ot': '',
        
        # 4. Prosthesis
        'service': [], 'service_ot': '',
        'date_cast': date.today(), 'date_deliv': date.today(),
        # Detailed components per PDF
        'socket_type': [], 'socket_ot': '',
        'liner': [], 'liner_ot': '',
        'suspension': [], 'susp_ot': '',
        'foot': [], 'foot_ot': '',
        'knee': [], 'knee_ot': '', # For TF/KD
        
        # 5. Social & Usage
        'assist': 'ไม่ใช้', 'assist_ot': '',
        'stand_hr': '1-3 ชั่วโมง', 'walk_hr': '1-3 ชั่วโมง',
        'fall': 'ไม่', 'fall_freq': '', 'fall_inj': 'ไม่', 'fall_inj_desc': '',
        
        # Q31-Q33 (Social/Work/Support)
        'q31_1': 'ไม่มีปัญหา (0-4%)', # Social Self
        'q31_2': 'ไม่มีปัญหา (0-4%)', # Social vs Others
        'q32_1': 'ไม่มีปัญหา (0-4%)', # Work Self
        'q32_2': 'ไม่มีปัญหา (0-4%)', # Work vs Others
        
        'supp_fam_access': 'ไม่ใช่', 'supp_fam_need_care': 'ไม่ใช่', # Q33.1
        'supp_org_access': 'ไม่ใช่', 'supp_org_type': [], 'supp_org_ot': '', # Q33.2

        # TUG
        'tug_running': False, 'start_time': None,
        't1': 0.0, 't2': 0.0, 't3': 0.0, 'tug_avg': 0.0, 'tug_status': '-'
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# เรียกใช้ฟังก์ชัน init ทันที
init_state()

# ---------------------------------------------------------
# 2. STYLES & HELPER FUNCTIONS
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    .main-title { text-align: center; font-size: 2.2em; font-weight: 700; color: #154360; margin-bottom: 5px; }
    .tug-display { 
        font-size: 80px; font-weight: 700; color: #2E86C1; 
        text-align: center; background-color: #f4f6f7; 
        padding: 30px; border-radius: 20px; margin-bottom: 20px;
        border: 3px solid #d6eaf8;
    }
    .result-box {
        padding: 20px; border-radius: 15px; text-align: center; 
        color: white; font-weight: bold; font-size: 1.3em; margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ฟังก์ชันแปลงค่าสำหรับ Report (แก้ปัญหา [])
def fmt_report(key, ot_key=None):
    val = st.session_state.get(key, '-')
    if isinstance(val, list):
        if not val: return "-"
        text = ", ".join(val)
        if ot_key and ("Other" in val or "อื่นๆ" in val):
            other_txt = st.session_state.get(ot_key, '')
            text += f" ({other_txt})"
        return text
    
    if ot_key and (val == "Other" or val == "อื่นๆ" or val == "Other (ระบุ)"):
        other_txt = st.session_state.get(ot_key, '')
        return f"{val} ({other_txt})"
    
    return str(val) if val else "-"

# TUG Functions
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
# 3. HTML GENERATION (UPDATED PER PDF)
# ---------------------------------------------------------
def create_html():
    dob_str = st.session_state.dob.strftime('%d/%m/%Y')
    age = date.today().year - st.session_state.dob.year
    
    html = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Sarabun', sans-serif; padding: 20px; color: #333; }}
            h1 {{ text-align: center; color: #1F618D; margin-bottom: 5px; }}
            .sec-head {{ background: #154360; color: white; padding: 8px; font-weight: bold; margin-top: 15px; border-radius: 4px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 5px; }}
            td {{ padding: 5px; border-bottom: 1px solid #eee; vertical-align: top; }}
            .lbl {{ font-weight: bold; width: 35%; color: #444; }}
        </style>
    </head>
    <body>
        <h1>Prosthesis Registry Report</h1>
        <div style="text-align:center; font-size:0.9em; color:#777;">HN: {st.session_state.hn} | Date: {datetime.now().strftime('%d/%m/%Y')}</div>

        <div class="sec-head">1. ข้อมูลทั่วไป (General)</div>
        <table>
            <tr><td class="lbl">ชื่อ-สกุล:</td><td>{st.session_state.fname}</td></tr>
            <tr><td class="lbl">วันเกิด (อายุ):</td><td>{dob_str} ({age} ปี)</td></tr>
            <tr><td class="lbl">เพศ:</td><td>{st.session_state.gender}</td></tr>
            <tr><td class="lbl">ที่อยู่:</td><td>{fmt_report('province', 'province_ot')}, {fmt_report('country', 'country_ot')}</td></tr>
            <tr><td class="lbl">น้ำหนัก/ส่วนสูง:</td><td>{st.session_state.weight} กก. / {st.session_state.height} ซม.</td></tr>
        </table>

        <div class="sec-head">2. ข้อมูลทางการแพทย์ (Medical)</div>
        <table>
            <tr><td class="lbl">โรคประจำตัว:</td><td>{fmt_report('comorbidities', 'comorb_ot')}</td></tr>
            <tr><td class="lbl">สาเหตุการตัดขา:</td><td>{fmt_report('cause', 'cause_ot')}</td></tr>
            <tr><td class="lbl">ปีที่ตัด / ข้าง:</td><td>{st.session_state.amp_year} / {st.session_state.side}</td></tr>
            <tr><td class="lbl">ระดับการตัดขา:</td><td>{fmt_report('level', 'level_ot')}</td></tr>
            <tr><td class="lbl">ลักษณะตอขา:</td><td>{st.session_state.stump_len} / {fmt_report('stump_shape', 'shape_ot')}</td></tr>
            <tr><td class="lbl">ประวัติผ่าตัดเพิ่ม:</td><td>{st.session_state.surgery} {fmt_report('surg_details') if st.session_state.surgery=='ใช่' else ''}</td></tr>
            <tr><td class="lbl">K-Level ก่อนตัด:</td><td>{st.session_state.k_level}</td></tr>
        </table>

        <div class="sec-head">3. การฟื้นฟู (Rehab)</div>
        <table>
            <tr><td class="lbl">บุคลากรที่ดูแล:</td><td>{fmt_report('personnel', 'personnel_ot')}</td></tr>
            <tr><td class="lbl">ประวัติฟื้นฟู:</td><td>{st.session_state.rehab}</td></tr>
            <tr><td class="lbl">กิจกรรมฟื้นฟู:</td><td>{fmt_report('rehab_act', 'rehab_act_ot')}</td></tr>
        </table>

        <div class="sec-head">4. ข้อมูลกายอุปกรณ์ (Prosthesis)</div>
        <table>
            <tr><td class="lbl">บริการครั้งนี้:</td><td>{fmt_report('service', 'service_ot')}</td></tr>
            <tr><td class="lbl">วันที่ (หล่อ-รับ):</td><td>{st.session_state.date_cast.strftime('%d/%m/%Y')} - {st.session_state.date_deliv.strftime('%d/%m/%Y')}</td></tr>
            <tr><td class="lbl">Socket Type:</td><td>{fmt_report('socket_type', 'socket_ot')}</td></tr>
            <tr><td class="lbl">Liner:</td><td>{fmt_report('liner', 'liner_ot')}</td></tr>
            <tr><td class="lbl">Suspension:</td><td>{fmt_report('suspension', 'susp_ot')}</td></tr>
            <tr><td class="lbl">Foot:</td><td>{fmt_report('foot', 'foot_ot')}</td></tr>
            <tr><td class="lbl">Knee:</td><td>{fmt_report('knee', 'knee_ot')}</td></tr>
        </table>

        <div class="sec-head">5. สังคมและการใช้งาน (Social & Usage)</div>
        <table>
            <tr><td class="lbl">อุปกรณ์ช่วยเดิน:</td><td>{fmt_report('assist', 'assist_ot')}</td></tr>
            <tr><td class="lbl">ยืน/เดิน (ต่อวัน):</td><td>ยืน: {st.session_state.stand_hr} | เดิน: {st.session_state.walk_hr}</td></tr>
            <tr><td class="lbl">ประวัติล้ม (6ด.):</td><td>{st.session_state.fall} {f"(ความถี่: {st.session_state.fall_freq})" if st.session_state.fall=='มี' else ''}</td></tr>
            <tr><td class="lbl">ปัญหาสังคม (ตนเอง/คนอื่น):</td><td>{st.session_state.q31_1} / {st.session_state.q31_2}</td></tr>
            <tr><td class="lbl">ปัญหางาน (ตนเอง/คนอื่น):</td><td>{st.session_state.q32_1} / {st.session_state.q32_2}</td></tr>
            <tr><td class="lbl">การสนับสนุนครอบครัว:</td><td>เข้าถึง: {st.session_state.supp_fam_access} (ต้องการคนดูแล: {st.session_state.supp_fam_need_care})</td></tr>
            <tr><td class="lbl">การสนับสนุนองค์กร:</td><td>เข้าถึง: {st.session_state.supp_org_access} -> {fmt_report('supp_org_type', 'supp_org_ot')}</td></tr>
        </table>

        <div style="margin-top:20px; padding:15px; background:#f4f6f7; border:2px solid #1F618D; text-align:center; border-radius:10px;">
            <h3>TUG Test Result</h3>
            <h1 style="margin:0; font-size:2.5em;">{st.session_state.tug_avg:.2f} s</h1>
            <h3 style="margin:5px 0;">{st.session_state.tug_status}</h3>
            <small>(Trial 1: {st.session_state.t1:.2f}s, Trial 2: {st.session_state.t2:.2f}s, Trial 3: {st.session_state.t3:.2f}s)</small>
        </div>
    </body>
    </html>
    """
    return html

def save_csv():
    if not st.session_state.hn:
        st.toast("⚠️ กรุณากรอก HN", icon="⚠️")
        return
    
    row = {
        'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'HN': [st.session_state.hn], 'Name': [st.session_state.fname],
        'Diagnosis': [fmt_report('cause')], 'Level': [fmt_report('level')],
        'Socket': [fmt_report('socket_type')], 'Foot': [fmt_report('foot')],
        'TUG_Avg': [st.session_state.tug_avg], 'TUG_Status': [st.session_state.tug_status]
    }
    df = pd.DataFrame(row)
    f = 'prosthesis_db.csv'
    if not os.path.exists(f): df.to_csv(f, index=False, encoding='utf-8-sig')
    else: df.to_csv(f, mode='a', header=False, index=False, encoding='utf-8-sig')
    st.toast("✅ บันทึกสำเร็จ!", icon="💾")

# ---------------------------------------------------------
# 4. MAIN UI
# ---------------------------------------------------------
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-title">🏥 Prosthesis Registry System</div>', unsafe_allow_html=True)
with col2:
    st.write("")
    st.write("")
    html_data = create_html() # เรียกตรงนี้ปลอดภัยแล้ว เพราะ init_state ทำงานแล้ว
    st.download_button("📥 Report (HTML)", html_data, f"Report_{st.session_state.hn}.html", "text/html", type="primary", on_click=save_csv)

tab1, tab2 = st.tabs(["📝 แบบบันทึกข้อมูล", "⏱️ TUG Test"])

with tab1:
    # --- 1. General ---
    with st.expander("1. ข้อมูลทั่วไป", expanded=True):
        c1, c2 = st.columns(2)
        c1.text_input("HN", key="hn")
        c2.text_input("ชื่อ-สกุล", key="fname")
        c1, c2 = st.columns(2)
        c1.date_input("วันเกิด", key="dob")
        c2.radio("เพศ", ["ชาย", "หญิง"], horizontal=True, key="gender")
        c1, c2 = st.columns(2)
        c1.selectbox("จังหวัด", ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "Other"], key="province")
        if st.session_state.province=="Other": c1.text_input("ระบุจังหวัด", key="province_ot")
        c2.selectbox("ประเทศ", ["Thailand", "Other"], key="country")
        st.number_input("น้ำหนัก (kg)", 0.0, key="weight")
        st.number_input("ส่วนสูง (cm)", 0.0, key="height")

    # --- 2. Medical ---
    with st.expander("2. ข้อมูลการตัดขาและสุขภาพ"):
        st.multiselect("โรคประจำตัว", ["เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "มะเร็ง", "การติดเชื้อ", "พิการแต่กำเนิด", "ไม่มี", "Other"], key="comorbidities")
        if "Other" in st.session_state.comorbidities: st.text_input("ระบุโรค", key="comorb_ot")
        
        st.selectbox("สาเหตุการตัดขา", ["อุบัติเหตุ", "โรคเบาหวาน", "โรคหลอดเลือด", "มะเร็ง", "การติดเชื้อ", "พิการแต่กำเนิด", "Other"], key="cause")
        if st.session_state.cause == "Other": st.text_input("ระบุสาเหตุ", key="cause_ot")
        
        c1, c2 = st.columns(2)
        c1.number_input("ปีที่ตัดขา (พ.ศ.)", 2490, 2600, key="amp_year")
        c2.radio("ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="side")
        
        st.selectbox("ระดับการตัดขา", ["Ankle disarticulation", "Transtibial", "Knee disarticulation", "Transfemoral", "Other"], key="level")
        
        c1, c2 = st.columns(2)
        c1.selectbox("ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"], key="stump_len")
        c2.selectbox("รูปทรงตอขา", ["Cylindrical", "Conical", "Bulbous", "Other"], key="stump_shape")
        
        st.radio("เคยผ่าตัดเพิ่มเติม", ["ไม่ใช่", "ใช่"], horizontal=True, key="surgery")
        if st.session_state.surgery == "ใช่":
            st.multiselect("รายละเอียดผ่าตัด", ["ตัดแต่งกระดูก", "ตัดแต่งผิวหนัง", "ตัดแต่งระดับสูงขึ้น"], key="surg_details")
        
        st.selectbox("K-Level ก่อนตัด", ["K0", "K1", "K2", "K3", "K4"], key="k_level")

    # --- 3. Rehab ---
    with st.expander("3. การฟื้นฟู (Rehab)"):
        personnel_opts = ["นักกายอุปกรณ์", "นักกายภาพบำบัด", "นักกิจกรรมบำบัด", "นักสังคมสงเคราะห์", "นักจิตวิทยา", "แพทย์เวชศาสตร์ฟื้นฟู", "พยาบาล", "นักสาธารณสุขชุมชน", "Other"]
        st.multiselect("บุคลากรที่เคยดูแล", personnel_opts, key="personnel")
        if "Other" in st.session_state.personnel: st.text_input("ระบุบุคลากร", key="personnel_ot")
        
        st.radio("เคยรับการฟื้นฟู", ["ไม่เคย", "เคย"], horizontal=True, key="rehab")
        if st.session_state.rehab == "เคย":
            act_opts = ["ถุงลดบวม", "ผ้ายืดรัดตอขา", "เบ้าอ่อนซิลิโคน", "เฝือกแข็งถอดได้", "ฝึกเดิน", "กีฬา/ออกกำลังกาย", "Other"]
            st.multiselect("กิจกรรมที่ทำ", act_opts, key="rehab_act")

    # --- 4. Prosthesis ---
    with st.expander("4. ข้อมูลกายอุปกรณ์"):
        svc_opts = ["ทำใหม่", "เปลี่ยนเบ้า", "ซ่อม/ปรับ", "เปลี่ยนเท้า", "เปลี่ยนเบ้าอ่อน (Liner)", "เปลี่ยนระบบยึด", "เปลี่ยนอะไหล่อื่นๆ", "Other"]
        st.multiselect("บริการครั้งนี้", svc_opts, key="service")
        
        c1, c2 = st.columns(2)
        c1.date_input("วันที่หล่อ/ปรึกษา", key="date_cast")
        c2.date_input("วันที่รับอุปกรณ์", key="date_deliv")
        
        st.subheader("ส่วนประกอบ (Components)")
        # Socket options from PDF Page 5
        socket_opts = [
            "Ankle: Push fit", "Ankle: Window opening", "Ankle: Distal end bearing",
            "TT: PTB", "TT: TSB", "TT: Osseointegration", 
            "KD: Push fit", "KD: Window opening", "KD: Ischial bearing",
            "TF: Quadrilateral", "TF: Ischial Containment", "TF: Sub Ischial", "TF: Osseointegration",
            "Other"
        ]
        st.multiselect("Socket Type", socket_opts, key="socket_type")
        if "Other" in st.session_state.socket_type: st.text_input("ระบุ Socket", key="socket_ot")
        
        liner_opts = ["No liner", "Foam/Pelite", "Silicone Liner", "Polyurethane Liner", "Gel Liner (TPE)", "Socks", "Other"]
        st.multiselect("Liner Type", liner_opts, key="liner")
        
        susp_opts = ["Self-suspension", "Cuff/strap", "Pin lock", "Lanyard", "Sleeve", "Expulsion valve", "Silesian belt", "TES belt", "Pelvic band", "Other"]
        st.multiselect("Suspension", susp_opts, key="suspension")
        
        foot_opts = ["Microprocessor", "Hydraulic ankle", "Special activity", "Dynamic response", "Multiaxial", "Single axis", "SACH", "Other"]
        st.multiselect("Foot Type", foot_opts, key="foot")
        
        knee_opts = ["No Knee (TT)", "Single axis", "Polycentric", "Manual lock", "Weight-activated", "Hydraulic", "Microprocessor", "Pneumatic", "Other"]
        st.multiselect("Knee Type (ถ้ามี)", knee_opts, key="knee")

    # --- 5. Social ---
    with st.expander("5. สังคมและการใช้งาน"):
        st.selectbox("อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "Cane (ไม้เท้า)", "Crutch (ไม้ค้ำยัน)", "Walker", "Wheelchair", "Other"], key="assist")
        c1, c2 = st.columns(2)
        c1.selectbox("เวลายืนต่อวัน", ["ไม่ยืนเลย", "< 1 ชม.", "1-3 ชม.", "3-7 ชม.", "> 8 ชม."], key="stand_hr")
        c2.selectbox("เวลาเดินต่อวัน", ["ไม่เดินเลย", "< 1 ชม.", "1-3 ชม.", "3-7 ชม.", "> 8 ชม."], key="walk_hr")
        
        st.radio("ประวัติล้ม (ใน 6 เดือน)", ["ไม่", "มี"], horizontal=True, key="fall")
        if st.session_state.fall == "มี":
            st.selectbox("ความถี่การล้ม", ["< 1 ครั้ง", "1-2 ครั้ง", "3-4 ครั้ง", "> 4 ครั้ง"], key="fall_freq")
            st.radio("ได้รับบาดเจ็บ", ["ไม่", "ใช่"], horizontal=True, key="fall_inj")
        
        st.markdown("---")
        st.markdown("**การมีส่วนร่วมในสังคม (Social Participation)**")
        probs = ["ไม่มีปัญหา (0-4%)", "เล็กน้อย (5-24%)", "ปานกลาง (25-49%)", "มาก (50-95%)", "มากที่สุด (96-100%)"]
        st.selectbox("31.1 ปัญหาการเข้าสังคม (เทียบความคาดหวังตนเอง)", probs, key="q31_1")
        st.selectbox("31.2 ปัญหาการเข้าสังคม (เทียบกับคนปกติ)", probs, key="q31_2")
        
        st.markdown("**การทำงาน (Work)**")
        st.selectbox("32.1 ปัญหาการทำงาน (เทียบความคาดหวังตนเอง)", probs, key="q32_1")
        st.selectbox("32.2 ปัญหาการทำงาน (เทียบกับคนปกติ)", probs, key="q32_2")
        
        st.markdown("---")
        st.markdown("**การสนับสนุน (Support)**")
        st.radio("33.1 เข้าถึงการดูแลจากครอบครัว", ["ใช่", "ไม่ใช่"], horizontal=True, key="supp_fam_access")
        if st.session_state.supp_fam_access == "ใช่":
            st.radio("   - จำเป็นต้องมีผู้ดูแล (Caregiver)", ["ใช่", "ไม่ใช่"], horizontal=True, key="supp_fam_need_care")
            
        st.radio("33.2 เข้าถึงสวัสดิการ/องค์กร", ["ใช่", "ไม่ใช่"], horizontal=True, key="supp_org_access")
        if st.session_state.supp_org_access == "ใช่":
            st.multiselect("   - แหล่งทุน", ["รัฐ (สปสช/กรมบัญชีกลาง)", "ประกันสังคม", "องค์กรไม่แสวงหาผลกำไร", "จ่ายเอง", "Other"], key="supp_org_type")

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
    st.number_input("Trial 1 (s)", key="t1", on_change=calculate_tug)
    st.number_input("Trial 2 (s)", key="t2", on_change=calculate_tug)
    st.number_input("Trial 3 (s)", key="t3", on_change=calculate_tug)
    
    st.button("🔄 Reset Timer", on_click=reset_tug, use_container_width=True)

    if st.session_state.tug_avg > 0:
        bg = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#27AE60"
        st.markdown(f"""
        <div class="result-box" style="background:{bg};">
            <div>Average: {st.session_state.tug_avg:.2f} sec</div>
            <div style="font-size:1.5em; margin-top:5px;">{st.session_state.tug_status}</div>
        </div>
        """, unsafe_allow_html=True)