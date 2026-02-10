import streamlit as st
import streamlit.components.v1 as components
import time
from datetime import datetime
import io 

# =========================================================
# ⚙️ CONFIG & CSS
# =========================================================
st.set_page_config(page_title="Prosthesis Registry & TUG", page_icon="🦿", layout="wide")

st.markdown("""
    <style>
    div[data-testid="stMetricValue"] {
        font-size: 80px !important;
        font-family: 'Courier New', monospace;
        color: #1F618D;
        font-weight: bold;
    }
    .tug-box {
        border: 2px solid #ddd;
        padding: 20px;
        border-radius: 10px;
        background-color: #f9f9f9;
        text-align: center;
        margin-top: 20px;
    }
    .stButton button {
        height: 3em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 📦 SESSION STATE SETUP
# =========================================================
defaults = {
    'is_running': False, 'start_time': 0.0, 'elapsed_time': 0.0,
    'hn': '', 'fname': '', 'birth_year': 2520, 'gender': 'ชาย', 
    'weight': 0.0, 'height': 0.0, 'nationality': 'ไทย', 'nat_ot': '',
    'country': 'Thailand', 'cnt_ot': '', 'province': 'กรุงเทพมหานคร',
    'comorbidities': [], 'comorb_ot': '', 'cause': 'อุบัติเหตุ', 'cause_ot': '',
    'amp_year': 2566, 'side': 'ขวา', 'amp_level': 'Transtibial', 'level_ot': '',
    'stump_len': 'ปานกลาง', 'stump_shape': 'Cylindrical', 'shape_ot': '',
    'surgery': 'ไม่ใช่', 'surg_details': [], 'surg_ot': '', 'k_level': 'K3',
    'personnel': [], 'pers_ot': '', 'rehab_status': 'ไม่เคย', 'activities': [], 'act_ot': '',
    'service': [], 'serv_ot': '', 'date_cast': datetime.now().date(), 'date_deliv': datetime.now().date(),
    'socket': 'PTB', 'sock_ot': '', 'liner': [], 'liner_ot': '',
    'suspension': [], 'susp_ot': '', 'foot': [], 'foot_ot': '', 'knee': [], 'knee_ot': '',
    'assist': 'ไม่ใช้', 'asst_ot': '', 'stand_hours': '1-3 ชม.', 'walk_hours': '1-3 ชม.',
    'fall_hist': 'ไม่มี', 'fall_freq': '1-2 ครั้ง', 'fall_inj': False,
    'q31_1': 'ไม่มีปัญหา (0-4%)', 'q31_2': 'ไม่มีปัญหา (0-4%)', 
    'q32_1': 'ไม่มีปัญหา (0-4%)', 'q32_2': 'ไม่มีปัญหา (0-4%)',
    'supp_family': 'ใช่', 'supp_org': 'ไม่ใช่', 'supp_sources': [], 'supp_ot': '',
    't1': 0.0, 't2': 0.0, 't3': 0.0, 'tug_avg': 0.0
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

def get_val(key, other_key=None):
    val = st.session_state[key]
    if isinstance(val, list):
        res = ", ".join(val)
        if "Other" in val and other_key and st.session_state[other_key]:
            res += f" ({st.session_state[other_key]})"
        return res if res else "-"
    else:
        if val == "Other" and other_key and st.session_state[other_key]:
            return f"{st.session_state[other_key]} (Other)"
        return str(val)

# =========================================================
# 📄 REPORT GENERATOR
# =========================================================
def create_html_content():
    # Logic
    knee_row = ""
    if st.session_state.amp_level in ["Transfemoral", "Knee Disarticulation", "Other"]:
        knee_row = f"<tr><td><b>Knee (ข้อเข่า):</b></td><td>{get_val('knee', 'knee_ot')}</td></tr>"

    tug_res = "NORMAL" if st.session_state.tug_avg < 13.5 else "HIGH RISK"
    tug_color = "green" if st.session_state.tug_avg < 13.5 else "red"

    html = f"""
    <html>
    <head>
        <title>Report_{st.session_state.hn}</title>
        <style>
            body {{ font-family: 'Sarabun', sans-serif; padding: 20px; }}
            h1 {{ text-align: center; color: #2C3E50; margin-bottom: 10px; }}
            h2 {{ color: #1F618D; border-bottom: 2px solid #ddd; padding-bottom: 5px; margin-top: 20px; font-size: 18px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 5px; font-size: 14px; }}
            td {{ padding: 6px; vertical-align: top; border-bottom: 1px solid #eee; }}
            td:first-child {{ font-weight: bold; width: 35%; color: #555; }}
            .tug-result {{ 
                text-align: center; border: 2px solid {tug_color}; padding: 10px; 
                margin-top: 15px; border-radius: 10px; color: {tug_color};
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
    </head>
    <body>
        <div style="text-align:right; font-size: 0.8em; color: gray;">
            Printed: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
        <h1>📄 รายงานประวัติผู้ใช้ขาเทียม</h1>
        
        <h2>1. ข้อมูลทั่วไป (General)</h2>
        <table>
            <tr><td>HN:</td><td>{st.session_state.hn}</td></tr>
            <tr><td>ชื่อ-สกุล:</td><td>{st.session_state.fname}</td></tr>
            <tr><td>เพศ / อายุ:</td><td>{st.session_state.gender} / {datetime.now().year + 543 - st.session_state.birth_year} ปี</td></tr>
            <tr><td>ที่อยู่:</td><td>{st.session_state.province}, {get_val('country', 'cnt_ot')}</td></tr>
        </table>

        <h2>2. ข้อมูลทางการแพทย์ (Medical)</h2>
        <table>
            <tr><td>โรคประจำตัว:</td><td>{get_val('comorbidities', 'comorb_ot')}</td></tr>
            <tr><td>สาเหตุ/ระดับ:</td><td>{get_val('cause', 'cause_ot')} / {get_val('amp_level', 'level_ot')} ({st.session_state.side})</td></tr>
            <tr><td>ลักษณะตอขา:</td><td>{st.session_state.stump_len}, {get_val('stump_shape', 'shape_ot')}</td></tr>
        </table>

        <h2>3. กายอุปกรณ์ (Prosthesis)</h2>
        <table>
            <tr><td>บริการ:</td><td>{get_val('service', 'serv_ot')}</td></tr>
            <tr><td>วันที่:</td><td>หล่อแบบ: {st.session_state.date_cast} | รับขา: {st.session_state.date_deliv}</td></tr>
            <tr><td>Comp:</td><td>S: {get_val('socket', 'sock_ot')} / L: {get_val('liner', 'liner_ot')}</td></tr>
            <tr><td>Comp:</td><td>Sus: {get_val('suspension', 'susp_ot')} / F: {get_val('foot', 'foot_ot')}</td></tr>
            {knee_row}
        </table>

        <h2>4. ผลการเดิน (TUG Test)</h2>
        <table>
            <tr><td>Trial 1-3:</td><td>{st.session_state.t1}, {st.session_state.t2}, {st.session_state.t3} s</td></tr>
        </table>
        <div class="tug-result">
            <h3>Avg: {st.session_state.tug_avg:.2f} sec | {tug_res}</h3>
        </div>
        
        <script>
            window.print();
        </script>
    </body>
    </html>
    """
    return html

# =========================================================
# 📱 APP UI
# =========================================================

st.sidebar.title("🦿 เมนูหลัก")

# --- ปุ่ม PRINT แบบใหม่ (Preview & Print) ---
st.sidebar.markdown("---")
st.sidebar.header("🖨️ พิมพ์รายงาน")

# วิธีที่ 1: กดปุ่มแล้วแสดงตัวอย่างพร้อมพิมพ์ทันที (แนะนำ!)
if st.sidebar.button("👁️ แสดงตัวอย่าง & สั่งพิมพ์", type="primary"):
    if not st.session_state.hn:
        st.sidebar.error("⚠️ กรุณากรอก HN ก่อน")
    else:
        # สร้าง HTML
        html_code = create_html_content()
        # ใช้ components.html แสดงผลลัพธ์โดยตรง (ตัดปัญหา download error)
        st.markdown("### 📄 ตัวอย่างรายงาน (หน้าต่างพิมพ์จะเด้งขึ้นมาเอง)")
        components.html(html_code, height=800, scrolling=True)

st.sidebar.markdown("---")

# วิธีที่ 2: ดาวน์โหลดไฟล์ (เผื่ออยากเก็บไฟล์) - แก้ BUG แล้ว
if st.sidebar.button("💾 ดาวน์โหลดไฟล์ HTML"):
    if not st.session_state.hn:
        st.sidebar.error("⚠️ กรุณากรอก HN ก่อน")
    else:
        html_code = create_html_content()
        # 🔥 จุดแก้สำคัญ: แปลง String เป็น BytesIO เพื่อป้องกัน Error 'File not available'
        file_buffer = io.BytesIO(html_code.encode('utf-8'))
        st.sidebar.download_button(
            label="⬇️ คลิกเพื่อบันทึกไฟล์",
            data=file_buffer,
            file_name=f"Report_{st.session_state.hn}.html",
            mime="text/html"
        )


# TABS
tab1, tab2 = st.tabs(["📝 กรอกข้อมูล (Registry)", "⏱️ จับเวลา (TUG Test)"])

with tab1:
    st.caption("กรอกข้อมูลให้ครบถ้วนก่อนกดพิมพ์รายงาน")
    with st.expander("1. ข้อมูลทั่วไป", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state.hn = c1.text_input("HN", key="i_hn")
        st.session_state.fname = c1.text_input("ชื่อ-นามสกุล", key="i_fname")
        st.session_state.birth_year = c1.selectbox("ปีเกิด", list(range(2567, 2467, -1)), key="i_byear")
        st.session_state.gender = c2.selectbox("เพศ", ["ชาย", "หญิง"], key="i_gen")
        st.session_state.province = c2.selectbox("จังหวัด", ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "อื่นๆ"], key="i_prov")
        st.session_state.nationality = c2.selectbox("สัญชาติ", ["ไทย", "Other"], key="i_nat")
        if st.session_state.nationality=="Other": st.session_state.nat_ot = c2.text_input("ระบุสัญชาติ", key="i_not")
        st.session_state.weight = c3.number_input("น้ำหนัก (กก.)", 0.0, key="i_wt")
        st.session_state.height = c3.number_input("ส่วนสูง (ซม.)", 0.0, key="i_ht")
        st.session_state.country = c3.selectbox("ประเทศ", ["Thailand", "Other"], key="i_cnt")
        if st.session_state.country=="Other": st.session_state.cnt_ot = c3.text_input("ระบุประเทศ", key="i_cot")

    with st.expander("2. ข้อมูลการแพทย์"):
        c1, c2 = st.columns(2)
        st.session_state.comorbidities = c1.multiselect("โรคประจำตัว", ["เบาหวาน", "ความดัน", "หัวใจ", "ไม่มี", "Other"], key="i_com")
        if "Other" in st.session_state.comorbidities: st.session_state.comorb_ot = c1.text_input("ระบุโรค", key="i_com_ot")
        st.session_state.cause = c1.selectbox("สาเหตุตัดขา", ["อุบัติเหตุ", "เบาหวาน", "มะเร็ง", "Other"], key="i_cau")
        if st.session_state.cause=="Other": st.session_state.cause_ot = c1.text_input("ระบุสาเหตุ", key="i_cau_ot")
        st.session_state.amp_level = c2.selectbox("ระดับการตัด", ["Transtibial", "Transfemoral", "Knee Disarticulation", "Other"], key="i_lvl")
        if st.session_state.amp_level=="Other": st.session_state.level_ot = c2.text_input("ระบุระดับ", key="i_lvl_ot")
        st.session_state.side = c2.radio("ข้าง", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="i_side")
        st.session_state.amp_year = c2.number_input("ปีที่ตัด (พ.ศ.)", 2490, 2600, key="i_ayr")
        st.session_state.k_level = c2.selectbox("K-Level", ["K0", "K1", "K2", "K3", "K4"], key="i_k")
        st.session_state.stump_len = c1.selectbox("ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"], key="i_slen")
        st.session_state.stump_shape = c1.selectbox("รูปทรงตอขา", ["Conical", "Cylindrical", "Bulbous", "Other"], key="i_shp")
        if st.session_state.stump_shape=="Other": st.session_state.shape_ot = c1.text_input("ระบุทรง", key="i_shp_ot")

    with st.expander("3-4. การฟื้นฟู & กายอุปกรณ์"):
        st.session_state.personnel = st.multiselect("บุคลากร", ["นักกายอุปกรณ์", "นักกายภาพ", "แพทย์", "Other"], key="i_per")
        if "Other" in st.session_state.personnel: st.session_state.pers_ot = st.text_input("ระบุบุคลากร", key="i_per_ot")
        st.session_state.service = st.multiselect("บริการ", ["ทำใหม่", "เปลี่ยนเบ้า", "ซ่อม", "Other"], key="i_srv")
        if "Other" in st.session_state.service: st.session_state.serv_ot = st.text_input("ระบุบริการ", key="i_srv_ot")
        c1, c2 = st.columns(2)
        st.session_state.date_cast = c1.date_input("วันหล่อแบบ", key="i_dc")
        st.session_state.date_deliv = c2.date_input("วันรับขา", key="i_dd")
        st.session_state.socket = c1.selectbox("Socket", ["PTB", "TSB", "Ischial", "Other"], key="i_sck")
        if st.session_state.socket=="Other": st.session_state.sock_ot = c1.text_input("ระบุ Socket", key="i_sck_ot")
        st.session_state.liner = c1.multiselect("Liner", ["No liner", "Foam", "Silicone", "Other"], key="i_lin")
        if "Other" in st.session_state.liner: st.session_state.liner_ot = c1.text_input("ระบุ Liner", key="i_lin_ot")
        st.session_state.suspension = c2.multiselect("Suspension", ["Suction", "Pin lock", "Belt", "Other"], key="i_sus")
        if "Other" in st.session_state.suspension: st.session_state.susp_ot = c2.text_input("ระบุ Susp", key="i_sus_ot")
        st.session_state.foot = c2.multiselect("Foot", ["SACH", "Single axis", "Dynamic", "Other"], key="i_ft")
        if "Other" in st.session_state.foot: st.session_state.foot_ot = c2.text_input("ระบุ Foot", key="i_ft_ot")

        if st.session_state.amp_level in ["Transfemoral", "Knee Disarticulation", "Other"]:
            st.info("🦵 ส่วนนี้สำหรับระดับเหนือเข่า")
            st.session_state.knee = st.multiselect("เลือก Knee", ["Single axis", "Polycentric", "Hydraulic", "Other"], key="i_kn")
            if "Other" in st.session_state.knee: st.session_state.knee_ot = st.text_input("ระบุ Knee", key="i_kn_ot")

    with st.expander("5. สังคม & การใช้งาน"):
        c1, c2 = st.columns(2)
        st.session_state.assist = c1.selectbox("อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "ไม้เท้า", "Walker", "Other"], key="i_ast")
        if st.session_state.assist=="Other": st.session_state.asst_ot = c1.text_input("ระบุอุปกรณ์", key="i_ast_ot")
        st.session_state.stand_hours = c1.selectbox("ยืน/วัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="i_std")
        st.session_state.walk_hours = c2.selectbox("เดิน/วัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="i_wlk")
        st.session_state.fall_hist = st.radio("ประวัติล้ม (6ด.)", ["ไม่มี", "มี"], horizontal=True, key="i_fall")
        if st.session_state.fall_hist=="มี":
            c1, c2 = st.columns(2)
            st.session_state.fall_freq = c1.selectbox("ความถี่การล้ม", ["1-2 ครั้ง", "> 2 ครั้ง"], key="i_ffrq")
            st.session_state.fall_inj = c2.checkbox("มีการบาดเจ็บ", key="i_finj")
        st.markdown("---")
        st.write("การประเมินตนเอง & สนับสนุน")
        st.session_state.q31_1 = c1.selectbox("31.1 สังคม (ตนเอง)", ["ไม่มีปัญหา", "มีปัญหา"], key="i_q311")
        st.session_state.q31_2 = c2.selectbox("31.2 สังคม (เทียบคนอื่น)", ["ไม่มีปัญหา", "มีปัญหา"], key="i_q312")
        st.session_state.supp_family = st.radio("ครอบครัวดูแล", ["ใช่", "ไม่ใช่"], horizontal=True, key="i_sfam")

with tab2:
    st.header("⏱️ Timed Up and Go (TUG)")
    
    col_clock, col_btns = st.columns([2, 1])
    with col_clock:
        clock_container = st.empty()
        if st.session_state.is_running:
            elapsed = time.time() - st.session_state.start_time
            clock_container.metric(label="Time", value=f"{elapsed:.2f} s")
            time.sleep(0.1) 
            st.rerun()
        else:
            clock_container.metric(label="Time", value=f"{st.session_state.elapsed_time:.2f} s")

    with col_btns:
        if st.button("▶️ START", type="primary", use_container_width=True, disabled=st.session_state.is_running):
            st.session_state.is_running = True
            st.session_state.start_time = time.time()
            st.rerun()
        if st.button("⏹️ STOP", type="secondary", use_container_width=True, disabled=not st.session_state.is_running):
            st.session_state.is_running = False
            st.session_state.elapsed_time = time.time() - st.session_state.start_time
            st.rerun()
        if st.button("🔄 RESET", use_container_width=True):
            st.session_state.is_running = False
            st.session_state.elapsed_time = 0.0
            st.rerun()

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    st.session_state.t1 = c1.number_input("Trial 1", 0.0, key="v_t1")
    st.session_state.t2 = c2.number_input("Trial 2", 0.0, key="v_t2")
    st.session_state.t3 = c3.number_input("Trial 3", 0.0, key="v_t3")

    valid_times = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0]
    if valid_times:
        st.session_state.tug_avg = sum(valid_times) / len(valid_times)
        status = "High Fall Risk (เสี่ยงล้มสูง)" if st.session_state.tug_avg >= 13.5 else "Normal Mobility (ปกติ)"
        color = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#28B463"
        st.markdown(f"""<div class="tug-box" style="border-color: {color}; color: {color};"><h3>Avg: {st.session_state.tug_avg:.2f} s</h3><h1>{status}</h1></div>""", unsafe_allow_html=True)