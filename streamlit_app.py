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
if 'init' not in st.session_state:
    defaults = {
        # 1. General
        'hn': '', 'fname': '', 'dob': date(1980, 1, 1), 'age': 0, 'gender': 'ชาย', 
        'country': 'Thailand', 'country_ot': '',
        'province': 'กรุงเทพมหานคร', 'province_ot': '',
        'nationality': 'ไทย', 'nationality_ot': '',
        'weight': 0.0, 'height': 0.0,
        # 2. Medical
        'comorbidities': [], 'comorb_ot': '',
        'cause': 'อุบัติเหตุ', 'cause_ot': '',
        'amp_year': 2560, 'side': 'ขวา', 'level': 'Transtibial', 'level_ot': '',
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

# Helper Functions
def get_txt(val, ot_key):
    # Helper to handle "Other" and List types safely
    if isinstance(val, list):
        text = ", ".join(val)
        if ("Other" in val or "อื่นๆ" in val) and ot_key in st.session_state:
            text += f" ({st.session_state[ot_key]})"
        return text if text else "-"
    
    if (val == "Other" or val == "อื่นๆ") and ot_key in st.session_state:
        return f"{val} ({st.session_state[ot_key]})"
    return str(val) if val else "-"

def calculate_tug():
    # Filter only valid times > 0
    times = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0.001]
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
# 3. HTML REPORT (COMPLETED VERSION)
# ---------------------------------------------------------
def create_html():
    dob = st.session_state.dob.strftime('%d/%m/%Y')
    age_calc = date.today().year - st.session_state.dob.year
    date_cast_str = st.session_state.date_cast.strftime('%d/%m/%Y')
    date_deliv_str = st.session_state.date_deliv.strftime('%d/%m/%Y')

    html = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Report_{st.session_state.hn}</title>
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Sarabun', sans-serif; padding: 20px; color: #333; line-height: 1.5; font-size: 14px; }}
            h1 {{ text-align: center; border-bottom: 2px solid #1F618D; padding-bottom: 10px; color: #1F618D; font-size: 1.6em; }}
            .section {{ margin-top: 15px; background: #fff; padding: 10px; border-radius: 8px; border: 1px solid #ddd; page-break-inside: avoid; }}
            .sec-head {{ color: #154360; font-weight: bold; font-size: 1.1em; margin-bottom: 8px; border-left: 5px solid #154360; padding-left: 10px; background-color: #f4f6f7; padding-top:5px; padding-bottom:5px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 5px; border-bottom: 1px solid #eee; vertical-align: top; }}
            .lbl {{ font-weight: bold; width: 35%; color: #555; }}
            .tug-box {{ text-align: center; border: 2px solid #1F618D; padding: 10px; margin-top: 15px; border-radius: 10px; background: #f0f8ff; }}
            .value {{ color: #000; }}
            @media print {{ body {{ padding: 0; }} .section {{ break-inside: avoid; }} button {{ display: none; }} }}
        </style>
    </head>
    <body>
        <div style="text-align:right; font-size:0.8em; color:gray;">Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        <h1>Prosthesis Registry Report</h1>
        
        <div class="section">
            <div class="sec-head">1. ข้อมูลทั่วไป (General)</div>
            <table>
                <tr><td class="lbl">HN:</td><td class="value">{st.session_state.hn}</td></tr>
                <tr><td class="lbl">ชื่อ-สกุล:</td><td class="value">{st.session_state.fname}</td></tr>
                <tr><td class="lbl">วันเกิด (อายุ):</td><td class="value">{dob} ({age_calc} ปี)</td></tr>
                <tr><td class="lbl">เพศ:</td><td class="value">{st.session_state.gender}</td></tr>
                <tr><td class="lbl">ที่อยู่:</td><td class="value">{get_txt(st.session_state.province, 'province_ot')}, {get_txt(st.session_state.country, 'country_ot')}</td></tr>
                <tr><td class="lbl">สัญชาติ:</td><td class="value">{get_txt(st.session_state.nationality, 'nationality_ot')}</td></tr>
                <tr><td class="lbl">น้ำหนัก/ส่วนสูง:</td><td class="value">{st.session_state.weight} kg / {st.session_state.height} cm</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">2. ข้อมูลทางการแพทย์ (Medical)</div>
            <table>
                <tr><td class="lbl">โรคประจำตัว:</td><td class="value">{get_txt(st.session_state.comorbidities, 'comorb_ot')}</td></tr>
                <tr><td class="lbl">สาเหตุการตัดขา:</td><td class="value">{get_txt(st.session_state.cause, 'cause_ot')}</td></tr>
                <tr><td class="lbl">ปีที่ตัด / ข้าง:</td><td class="value">{st.session_state.amp_year} / {st.session_state.side}</td></tr>
                <tr><td class="lbl">ระดับการตัดขา:</td><td class="value">{get_txt(st.session_state.level, 'level_ot')}</td></tr>
                <tr><td class="lbl">ลักษณะตอขา:</td><td class="value">{st.session_state.stump_len} / {get_txt(st.session_state.stump_shape, 'shape_ot')}</td></tr>
                <tr><td class="lbl">การผ่าตัดเพิ่มเติม:</td><td class="value">{st.session_state.surgery} {f"({', '.join(st.session_state.surg_details)})" if st.session_state.surgery=='ใช่' else ''}</td></tr>
                <tr><td class="lbl">K-Level (ก่อนตัด):</td><td class="value">{st.session_state.k_level}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">3. การฟื้นฟู (Rehab)</div>
            <table>
                <tr><td class="lbl">บุคลากรที่ดูแล:</td><td class="value">{get_txt(st.session_state.personnel, 'personnel_ot')}</td></tr>
                <tr><td class="lbl">ประวัติการฟื้นฟู:</td><td class="value">{st.session_state.rehab}</td></tr>
                <tr><td class="lbl">กิจกรรมฟื้นฟู:</td><td class="value">{get_txt(st.session_state.rehab_act, 'rehab_act_ot')}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">4. กายอุปกรณ์ (Prosthesis)</div>
            <table>
                <tr><td class="lbl">บริการครั้งนี้:</td><td class="value">{get_txt(st.session_state.service, 'service_ot')}</td></tr>
                <tr><td class="lbl">วันที่หล่อ / รับ:</td><td class="value">{date_cast_str} / {date_deliv_str}</td></tr>
                <tr><td class="lbl">Socket:</td><td class="value">{get_txt(st.session_state.socket, 'socket_ot')}</td></tr>
                <tr><td class="lbl">Liner:</td><td class="value">{get_txt(st.session_state.liner, 'liner_ot')}</td></tr>
                <tr><td class="lbl">Suspension:</td><td class="value">{get_txt(st.session_state.suspension, 'susp_ot')}</td></tr>
                <tr><td class="lbl">Foot:</td><td class="value">{get_txt(st.session_state.foot, 'foot_ot')}</td></tr>
                <tr><td class="lbl">Knee:</td><td class="value">{get_txt(st.session_state.knee, 'knee_ot')}</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="sec-head">5. สังคมและการใช้งาน (Social & Usage)</div>
            <table>
                <tr><td class="lbl">อุปกรณ์ช่วยเดิน:</td><td class="value">{get_txt(st.session_state.assist, 'assist_ot')}</td></tr>
                <tr><td class="lbl">ยืน / เดิน (ต่อวัน):</td><td class="value">ยืน: {st.session_state.stand_hr} | เดิน: {st.session_state.walk_hr}</td></tr>
                <tr><td class="lbl">ประวัติล้ม (6ด.):</td><td class="value">{st.session_state.fall} {f"(ความถี่: {st.session_state.fall_freq}, บาดเจ็บ: {st.session_state.fall_inj})" if st.session_state.fall=='มี' else ''}</td></tr>
                <tr><td class="lbl">ปัญหาสังคม:</td><td class="value">ตนเอง: {st.session_state.q31_1}<br>คนอื่น: {st.session_state.q31_2}</td></tr>
                <tr><td class="lbl">ปัญหางาน:</td><td class="value">ตนเอง: {st.session_state.q32_1}<br>คนอื่น: {st.session_state.q32_2}</td></tr>
                <tr><td class="lbl">การสนับสนุน:</td><td class="value">ครอบครัว: {st.session_state.supp_fam}<br>องค์กร: {st.session_state.supp_org} {f"({get_txt(st.session_state.supp_src, 'supp_src_ot')})" if st.session_state.supp_org=='ใช่' else ''}</td></tr>
            </table>
        </div>

        <div class="tug-box">
            <h3 style="margin:0;">TUG Test Result</h3>
            <h1 style="margin:5px 0; font-size:2em;">{st.session_state.tug_avg:.2f} s</h1>
            <h3 style="color:{'#C0392B' if st.session_state.tug_avg >= 13.5 else '#27AE60'}; margin:0;">{st.session_state.tug_status}</h3>
            <p style="font-size:0.9em; margin-top:5px; color:#666;">(Trial 1: {st.session_state.t1:.2f} | Trial 2: {st.session_state.t2:.2f} | Trial 3: {st.session_state.t3:.2f})</p>
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

    def clean_list(val):
        if isinstance(val, list): return ", ".join(val)
        return str(val)

    data = {
        'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        # 1. General
        'HN': [st.session_state.hn], 'Name': [st.session_state.fname],
        'DOB': [st.session_state.dob], 'Age': [date.today().year - st.session_state.dob.year],
        'Gender': [st.session_state.gender], 'Nationality': [get_txt(st.session_state.nationality, 'nationality_ot')],
        'Country': [get_txt(st.session_state.country, 'country_ot')], 'Province': [get_txt(st.session_state.province, 'province_ot')],
        'Weight': [st.session_state.weight], 'Height': [st.session_state.height],
        # 2. Medical
        'Comorbidities': [get_txt(st.session_state.comorbidities, 'comorb_ot')],
        'Cause': [get_txt(st.session_state.cause, 'cause_ot')],
        'Amp_Year': [st.session_state.amp_year], 'Side': [st.session_state.side],
        'Level': [get_txt(st.session_state.level, 'level_ot')],
        'Stump_Len': [st.session_state.stump_len], 'Stump_Shape': [get_txt(st.session_state.stump_shape, 'shape_ot')],
        'Surgery': [st.session_state.surgery], 'Surgery_Details': [clean_list(st.session_state.surg_details)],
        'K_Level': [st.session_state.k_level],
        # 3. Rehab
        'Rehab_Personnel': [get_txt(st.session_state.personnel, 'personnel_ot')],
        'Rehab_History': [st.session_state.rehab], 'Rehab_Activity': [get_txt(st.session_state.rehab_act, 'rehab_act_ot')],
        # 4. Prosthesis
        'Service': [get_txt(st.session_state.service, 'service_ot')],
        'Date_Cast': [st.session_state.date_cast], 'Date_Deliv': [st.session_state.date_deliv],
        'Socket': [get_txt(st.session_state.socket, 'socket_ot')], 'Liner': [get_txt(st.session_state.liner, 'liner_ot')],
        'Suspension': [get_txt(st.session_state.suspension, 'susp_ot')],
        'Foot': [get_txt(st.session_state.foot, 'foot_ot')], 'Knee': [get_txt(st.session_state.knee, 'knee_ot')],
        # 5. Social
        'Assist_Device': [get_txt(st.session_state.assist, 'assist_ot')],
        'Stand_Hr': [st.session_state.stand_hr], 'Walk_Hr': [st.session_state.walk_hr],
        'Fall_History': [st.session_state.fall], 'Fall_Freq': [st.session_state.fall_freq], 'Fall_Injury': [st.session_state.fall_inj],
        'Social_Self': [st.session_state.q31_1], 'Social_Others': [st.session_state.q31_2],
        'Work_Self': [st.session_state.q32_1], 'Work_Others': [st.session_state.q32_2],
        'Fam_Support': [st.session_state.supp_fam],
        'Org_Support': [st.session_state.supp_org], 'Org_Source': [get_txt(st.session_state.supp_src, 'supp_src_ot')],
        # TUG
        'TUG_1': [st.session_state.t1], 'TUG_2': [st.session_state.t2], 'TUG_3': [st.session_state.t3],
        'TUG_Avg': [st.session_state.tug_avg], 'TUG_Status': [st.session_state.tug_status]
    }
    
    df = pd.DataFrame(data)
    file_path = 'prosthesis_database.csv'
    
    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    else:
        try:
            existing_df = pd.read_csv(file_path)
            if len(existing_df.columns) != len(df.columns):
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                df.to_csv(file_path, mode='a', header=False, index=False, encoding='utf-8-sig')
        except:
             df.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    st.toast(f'✅ บันทึก HN: {st.session_state.hn} เรียบร้อย!', icon='💾')

html_data = create_html()

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="main-title">🏥 Digital Prosthesis Registry</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">ระบบบันทึกข้อมูลกายอุปกรณ์และทดสอบการเดิน (OM Platform)</div>', unsafe_allow_html=True)

with col_h2:
    st.write("") 
    st.write("") 
    st.download_button(
        "📥 Download & Auto-Save",
        data=io.BytesIO(html_data.encode('utf-8')),
        file_name=f"Report_{st.session_state.hn}.html",
        mime="text/html",
        type="primary",
        use_container_width=True,
        on_click=save_to_csv
    )

st.sidebar.markdown("### 📥 Report Management")
st.sidebar.info("การกดปุ่ม Download จะทำการบันทึกข้อมูลลงฐานข้อมูล (CSV) โดยอัตโนมัติ")

st.sidebar.download_button(
    "📄 Download HTML Report",
    data=io.BytesIO(html_data.encode('utf-8')),
    file_name=f"Report_{st.session_state.hn}.html",
    mime="text/html",
    use_container_width=True,
    on_click=save_to_csv
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Database Management")

if os.path.exists('prosthesis_database.csv'):
    df_db = pd.read_csv('prosthesis_database.csv')
    csv_data = df_db.to_csv(index=False).encode('utf-8-sig')
    
    st.sidebar.download_button(
        label="📊 Download Database (CSV)",
        data=csv_data,
        file_name="prosthesis_database.csv",
        mime="text/csv",
        use_container_width=True,
        type="secondary"
    )
    
    with st.sidebar.expander("👀 ดูตัวอย่างข้อมูล"):
        st.dataframe(df_db)
else:
    st.sidebar.warning("ยังไม่มีไฟล์ Database")

# --- TABS ---
tab1, tab2 = st.tabs(["📝 Registry Form", "⏱️ TUG Test"])

with tab1:
    with st.expander("1. ข้อมูลทั่วไป (General Info)", expanded=True):
        st.date_input("1. วัน/เดือน/ปีเกิด (Date of Birth)", key="dob")
        st.caption(f"อายุปัจจุบัน: {date.today().year - st.session_state.dob.year} ปี")
        st.selectbox("2. เพศ (Gender)", ["ชาย", "หญิง"], key="gender")
        
        st.selectbox("3. ประเทศที่อยู่อาศัย", ["Thailand", "Other"], key="country")
        if st.session_state.country == "Other": st.text_input("ระบุประเทศ", key="country_ot")
        
        st.selectbox("4. จังหวัดที่อยู่อาศัย", ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "ภูเก็ต", "Other"], key="province")
        if st.session_state.province == "Other": st.text_input("ระบุจังหวัด", key="province_ot")
        
        st.selectbox("5. สัญชาติ", ["ไทย", "Other"], key="nationality")
        if st.session_state.nationality == "Other": st.text_input("ระบุสัญชาติ", key="nationality_ot")
        
        st.text_input("6. เลขประจำตัวผู้ป่วย (HN)", key="hn")
        st.text_input("ชื่อ-นามสกุล (Name)", key="fname")
        st.number_input("7. น้ำหนัก (kg)", 0.0, step=0.1, key="weight")
        st.number_input("8. ส่วนสูง (cm)", 0.0, step=1.0, key="height")

    with st.expander("2. ข้อมูลการตัดขาและสุขภาพ", expanded=False):
        st.multiselect("9. โรคประจำตัว", ["เบาหวาน", "ความดัน", "หัวใจ", "มะเร็ง", "ติดเชื้อ", "ไม่มี", "Other"], key="comorbidities")
        if "Other" in st.session_state.comorbidities: st.text_input("ระบุโรค", key="comorb_ot")
        st.selectbox("10. สาเหตุการตัดขา", ["อุบัติเหตุ", "เบาหวาน", "หลอดเลือด", "มะเร็ง", "ติดเชื้อ", "พิการแต่กำเนิด", "Other"], key="cause")
        if st.session_state.cause == "Other": st.text_input("ระบุสาเหตุ", key="cause_ot")
        st.number_input("11. ปีที่ตัดขา (พ.ศ.)", 2490, 2600, key="amp_year")
        st.radio("12. ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="side")
        st.selectbox("13. ระดับการตัดขา", ["Ankle disarticulation", "Transtibial", "Knee disarticulation", "Transfemoral", "Other"], key="level")
        if st.session_state.level == "Other": st.text_input("ระบุระดับ", key="level_ot")
        st.selectbox("14. ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"], key="stump_len")
        st.selectbox("15. รูปทรงตอขา", ["Conical", "Cylindrical", "Bulbous", "Other"], key="stump_shape")
        if st.session_state.stump_shape == "Other": st.text_input("ระบุรูปทรง", key="shape_ot")
        st.radio("16. ผ่าตัดเพิ่มเติม", ["ไม่ใช่", "ใช่"], horizontal=True, key="surgery")
        if st.session_state.surgery == "ใช่": st.multiselect("รายละเอียดการผ่าตัด", ["ตัดกระดูก", "ตัดผิวหนัง", "ตัดระดับสูงขึ้น"], key="surg_details")
        st.selectbox("17. K-Level ก่อนตัด", ["K0", "K1", "K2", "K3", "K4"], key="k_level")

    with st.expander("3. การฟื้นฟู (Rehab)", expanded=False):
        st.multiselect("18. บุคลากรที่ดูแล", ["นักกายอุปกรณ์", "นักกายภาพ", "แพทย์", "พยาบาล", "Other"], key="personnel")
        if "Other" in st.session_state.personnel: st.text_input("ระบุบุคลากร", key="personnel_ot")
        st.radio("19. เคยฟื้นฟูหรือไม่", ["ไม่เคย", "เคย"], horizontal=True, key="rehab")
        if st.session_state.rehab == "เคย":
            st.multiselect("กิจกรรม", ["ถุงลดบวม", "ผ้ายืด", "เบ้าซิลิโคน", "ฝึกเดิน", "Other"], key="rehab_act")
            if "Other" in st.session_state.rehab_act: st.text_input("ระบุกิจกรรม", key="rehab_act_ot")

    with st.expander("4. กายอุปกรณ์ (Prosthesis)", expanded=False):
        st.multiselect("20. การบริการครั้งนี้", ["ทำใหม่", "เปลี่ยนเบ้า", "ซ่อม", "Other"], key="service")
        if "Other" in st.session_state.service: st.text_input("ระบุบริการ", key="service_ot")
        c1, c2 = st.columns(2)
        with c1: st.date_input("21. วันที่หล่อแบบ", key="date_cast")
        with c2: st.date_input("22. วันที่ได้รับ", key="date_deliv")
        st.selectbox("23. Socket Type", ["PTB", "TSB", "KBM", "Quadrilateral", "Ischial Containment", "Other"], key="socket")
        if st.session_state.socket == "Other": st.text_input("ระบุ Socket", key="socket_ot")
        st.selectbox("24. Liner", ["None", "Foam", "Silicone", "Gel", "Other"], key="liner")
        if st.session_state.liner == "Other": st.text_input("ระบุ Liner", key="liner_ot")
        st.multiselect("25. Suspension", ["Cuff", "Pin Lock", "Suction", "Vacuum", "Belt", "Other"], key="suspension")
        if "Other" in st.session_state.suspension: st.text_input("ระบุ Suspension", key="susp_ot")
        st.multiselect("26. Foot", ["SACH", "Single Axis", "Dynamic", "Microprocessor", "Other"], key="foot")
        if "Other" in st.session_state.foot: st.text_input("ระบุ Foot", key="foot_ot")
        st.multiselect("27. Knee (สำหรับเหนือเข่า)", ["Single Axis", "Polycentric", "Hydraulic", "Microprocessor", "Other"], key="knee")
        if "Other" in st.session_state.knee: st.text_input("ระบุ Knee", key="knee_ot")

    with st.expander("5. สังคมและการใช้งาน", expanded=False):
        st.selectbox("28. อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "ไม้เท้า", "Walker", "Wheelchair", "Other"], key="assist")
        if st.session_state.assist == "Other": st.text_input("ระบุอุปกรณ์", key="assist_ot")
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
            if "Other" in st.session_state.supp_src: st.text_input("ระบุองค์กรอื่น", key="supp_src_ot")

with tab2:
    st.markdown('<div class="section-title" style="text-align:center; border:none; margin-top:20px;">⏱️ Timed Up and Go Test</div>', unsafe_allow_html=True)
    if st.session_state.tug_running:
        elapsed = time.time() - st.session_state.start_time
        st.markdown(f'<div class="tug-display">{elapsed:.2f} s</div>', unsafe_allow_html=True)
        if st.button("⏹️ STOP", type="primary", use_container_width=True):
            st.session_state.tug_running = False
            fin = round(elapsed, 2) # ปัดเศษ 2 ตำแหน่ง
            if st.session_state.t1 <= 0.01: st.session_state.t1 = fin
            elif st.session_state.t2 <= 0.01: st.session_state.t2 = fin
            elif st.session_state.t3 <= 0.01: st.session_state.t3 = fin
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
    
    # [FIX] เพิ่ม step=0.01 เพื่อรองรับทศนิยม ไม่งั้นค่าจะหาย
    c1, c2, c3 = st.columns(3)
    st.number_input("Trial 1", key="t1", on_change=calculate_tug, step=0.01, format="%.2f")
    st.number_input("Trial 2", key="t2", on_change=calculate_tug, step=0.01, format="%.2f")
    st.number_input("Trial 3", key="t3", on_change=calculate_tug, step=0.01, format="%.2f")
    
    st.button("🔄 Reset Timer", on_click=reset_tug, use_container_width=True)
    if st.session_state.tug_avg > 0:
        bg = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#27AE60"
        st.markdown(f"""
        <div class="result-box" style="background:{bg};">
            <div>Average Time: {st.session_state.tug_avg:.2f} s</div>
            <div style="font-size:1.5em; margin-top:5px;">{st.session_state.tug_status}</div>
        </div>
        """, unsafe_allow_html=True)