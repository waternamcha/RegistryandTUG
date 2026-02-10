import streamlit as st
import time
from datetime import datetime

# =========================================================
# ⚙️ CONFIG & CSS
# =========================================================
st.set_page_config(page_title="Prosthesis Registry & OM", page_icon="🦿", layout="wide")

# CSS สำหรับหน้าจอปกติ และ การพิมพ์ (Print)
st.markdown("""
    <style>
    /* ซ่อน Elements กวนใจเวลาพิมพ์ */
    @media print {
        .stButton, button, .stAppHeader, footer, [data-testid="stSidebar"], .stDeployButton, header { 
            display: none !important; 
        }
        .block-container {
            padding: 0 !important; margin: 0 !important;
            max-width: 100% !important;
        }
        @page { size: A4; margin: 1.5cm; }
    }
    
    /* Style สำหรับนาฬิกา TUG */
    div[data-testid="stMetricValue"] {
        font-size: 60px !important;
        font-family: 'Courier New', monospace;
        color: #1F618D;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 📦 SESSION STATE (เก็บตัวแปรให้ครบ 33 ข้อ)
# =========================================================
defaults = {
    'print_mode': False, 'is_running': False, 'start_time': None, 'stopwatch_value': 0.0,
    # 1. General
    'hn': '', 'fname': '', 'birth_year': 2520, 'gender': 'ชาย', 
    'weight': 0.0, 'height': 0.0, 'nationality': 'ไทย', 'country': 'Thailand', 'province': 'กรุงเทพมหานคร',
    # 2. Medical
    'comorbidities': [], 'cause': 'อุบัติเหตุ', 'amp_year': 2566, 'side': 'ขวา',
    'amp_level': 'Transtibial', 'stump_len': 'ปานกลาง', 'stump_shape': 'Cylindrical',
    'surgery': 'ไม่ใช่', 'surg_details': [], 'k_level': 'K3',
    # 3. Rehab
    'personnel': [], 'rehab_status': 'ไม่เคย', 'activities': [],
    # 4. Prosthesis
    'service': [], 'date_cast': datetime.now().date(), 'date_deliv': datetime.now().date(),
    'socket': 'PTB', 'liner': [], 'suspension': [], 'foot': [], 'knee': [],
    # 5. Social
    'assist': 'ไม่ใช้', 'stand_hours': '1-3 ชม.', 'walk_hours': '1-3 ชม.',
    'fall_hist': 'ไม่มี', 'fall_freq': '', 'fall_inj': False,
    'q31_1': '-', 'q31_2': '-', 'q32_1': '-', 'q32_2': '-',
    'supp_family': 'ใช่', 'supp_org': 'ไม่ใช่', 'supp_sources': [],
    # TUG
    't1': 0.0, 't2': 0.0, 't3': 0.0, 'tug_avg': 0.0
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ข้อมูลตัวเลือก
YEARS_LIST = list(range(datetime.now().year + 543, datetime.now().year + 543 - 100, -1))
PROBLEM_LEVELS = ["ไม่มีปัญหา (0-4%)", "มีปัญหาเล็กน้อย (5-24%)", "มีปัญหาปานกลาง (25-49%)", "มีปัญหามาก (50-95%)", "มีปัญหามากที่สุด (96-100%)"]

# =========================================================
# 📝 PART A: INPUT FORM (หน้ากรอกข้อมูล)
# =========================================================
def show_input_form():
    st.title("🦿 Digital Prosthesis Registry")
    
    col_top1, col_top2 = st.columns([3, 1])
    with col_top2:
        if st.button("📄 พิมพ์รายงาน (Print Report)", type="primary", use_container_width=True):
            st.session_state.print_mode = True
            st.rerun()

    tab1, tab2 = st.tabs(["📋 กรอกข้อมูล (Registry)", "⏱️ จับเวลา (TUG Test)"])

    with tab1:
        # --- SECTION 1 ---
        st.subheader("ส่วนที่ 1: ข้อมูลทั่วไป (General Info)")
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state.hn = st.text_input("HN", key="i_hn")
                st.session_state.fname = st.text_input("ชื่อ-นามสกุล", key="i_fname")
                st.session_state.birth_year = st.selectbox("ปีเกิด (พ.ศ.)", YEARS_LIST, key="i_byear")
            with c2:
                st.session_state.gender = st.selectbox("เพศ", ["ชาย", "หญิง"], key="i_gen")
                st.session_state.nationality = st.selectbox("สัญชาติ", ["ไทย", "Other"], key="i_nat")
                if st.session_state.nationality == "Other": st.text_input("ระบุสัญชาติ", key="nat_ot")
                st.session_state.province = st.selectbox("จังหวัด", ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "สงขลา", "อื่นๆ"], key="i_prov")
            with c3:
                st.session_state.country = st.selectbox("ประเทศ", ["Thailand", "Other"], key="i_cnt")
                st.session_state.weight = st.number_input("น้ำหนัก (กก.)", 0.0, key="i_wt")
                st.session_state.height = st.number_input("ส่วนสูง (ซม.)", 0.0, key="i_ht")

        # --- SECTION 2 ---
        st.subheader("ส่วนที่ 2: ข้อมูลการแพทย์ (Medical)")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.comorbidities = st.multiselect("โรคประจำตัว", ["เบาหวาน", "ความดัน", "หัวใจ", "ไม่มี", "Other"], key="i_comorb")
                if "Other" in st.session_state.comorbidities: st.text_input("ระบุโรคอื่น", key="comorb_ot")
                st.session_state.cause = st.selectbox("สาเหตุ", ["อุบัติเหตุ", "เบาหวาน", "มะเร็ง", "Other"], key="i_cause")
                st.session_state.amp_year = st.number_input("ปีที่ตัดขา (พ.ศ.)", 2490, 2600, key="i_ayear")
                st.session_state.side = st.radio("ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="i_side")
            with c2:
                st.session_state.amp_level = st.selectbox("ระดับ", ["Transtibial", "Transfemoral", "Knee Disarticulation", "Other"], key="i_lvl")
                st.session_state.stump_len = st.selectbox("ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"], key="i_slen")
                st.session_state.stump_shape = st.selectbox("รูปทรง", ["Conical", "Cylindrical", "Bulbous", "Other"], key="i_shp")
                st.session_state.surgery = st.radio("ผ่าตัดเพิ่มเติม?", ["ไม่ใช่", "ใช่"], key="i_surg")
                if st.session_state.surgery == "ใช่": st.session_state.surg_details = st.multiselect("ระบุการผ่าตัด", ["ตัดกระดูก", "ตัดผิวหนัง"], key="i_surg_d")
                st.session_state.k_level = st.selectbox("K-Level ก่อนตัด", ["K0", "K1", "K2", "K3", "K4"], key="i_klevel")

        # --- SECTION 3 ---
        st.subheader("ส่วนที่ 3: การฟื้นฟู (Rehab)")
        with st.container(border=True):
            st.session_state.personnel = st.multiselect("บุคลากรที่ดูแล", ["นักกายอุปกรณ์", "นักกายภาพ", "แพทย์"], key="i_pers")
            st.session_state.rehab_status = st.radio("เคยฟื้นฟู?", ["ไม่เคย", "เคย"], horizontal=True, key="i_reh")
            if st.session_state.rehab_status == "เคย":
                st.session_state.activities = st.multiselect("กิจกรรม", ["ใส่ถุงลดบวม", "พันผ้ายืด", "ฝึกเดิน"], key="i_act")

        # --- SECTION 4 ---
        st.subheader("ส่วนที่ 4: กายอุปกรณ์ (Prosthesis)")
        with st.container(border=True):
            st.session_state.service = st.multiselect("บริการครั้งนี้", ["ทำใหม่", "เปลี่ยนเบ้า", "ซ่อม"], key="i_serv")
            d1, d2 = st.columns(2)
            d1.date_input("วันที่หล่อแบบ", key="i_dcast")
            d2.date_input("วันที่รับ", key="i_ddeliv")
            st.divider()
            c1, c2 = st.columns(2)
            c1.selectbox("Socket", ["PTB", "TSB", "Ischial", "Other"], key="i_sock")
            c1.multiselect("Liner", ["No liner", "Foam", "Silicone"], key="i_liner")
            c2.multiselect("Suspension", ["Suction", "Pin lock", "Belt"], key="i_susp")
            c2.multiselect("Foot", ["SACH", "Single axis", "Dynamic"], key="i_foot")
            if st.session_state.amp_level in ["Transfemoral", "Knee Disarticulation"]:
                st.multiselect("Knee (เฉพาะเหนือเข่า)", ["Single axis", "Polycentric", "Hydraulic"], key="i_knee")

        # --- SECTION 5 ---
        st.subheader("ส่วนที่ 5: สังคม & การใช้งาน (Social)")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            c1.selectbox("อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "ไม้เท้า", "Walker"], key="i_asst")
            c1.selectbox("ยืน/วัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="i_std")
            c1.selectbox("เดิน/วัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="i_wlk")
            
            c2.radio("ประวัติล้ม (6ด.)", ["ไม่มี", "มี"], key="i_fall")
            if st.session_state.fall_hist == "มี":
                c2.selectbox("ความถี่", ["1-2 ครั้ง", "> 2 ครั้ง"], key="i_ffreq")
                c2.checkbox("บาดเจ็บ", key="i_finj")
            
            st.markdown("---")
            st.write("**31-32. การมีส่วนร่วมในสังคม & การทำงาน**")
            st.session_state.q31_1 = st.selectbox("31.1 สังคม (ตนเอง)", PROBLEM_LEVELS, key="i_q31_1")
            st.session_state.q31_2 = st.selectbox("31.2 สังคม (เทียบคนอื่น)", PROBLEM_LEVELS, key="i_q31_2")
            st.session_state.q32_1 = st.selectbox("32.1 งาน (ตนเอง)", PROBLEM_LEVELS, key="i_q32_1")
            st.session_state.q32_2 = st.selectbox("32.2 งาน (เทียบคนอื่น)", PROBLEM_LEVELS, key="i_q32_2")
            
            st.markdown("---")
            st.radio("33.1 การดูแลจากครอบครัว", ["ใช่", "ไม่ใช่"], horizontal=True, key="i_sfam")
            st.session_state.supp_org = st.radio("33.2 สนับสนุนจากหน่วยงาน", ["ใช่", "ไม่ใช่"], horizontal=True, key="i_sorg")
            if st.session_state.supp_org == "ใช่":
                st.multiselect("ระบุหน่วยงาน", ["รัฐ", "เอกชน"], key="i_ssrc")

    with tab2:
        st.header("⏱️ TUG Test")
        # Logic นาฬิกา (ย่อให้สั้นลงแต่ทำงานได้เหมือนเดิม)
        t_cont = st.container(border=True)
        if st.session_state.is_running:
            t_val = time.time() - st.session_state.start_time
            t_cont.metric("Time", f"{t_val:.2f} s")
            time.sleep(0.1)
            st.rerun()
        else:
            t_cont.metric("Time", f"{st.session_state.stopwatch_value:.2f} s")

        b1, b2, b3 = st.columns(3)
        if b1.button("Start"): st.session_state.is_running=True; st.session_state.start_time=time.time(); st.rerun()
        if b2.button("Stop"): st.session_state.is_running=False; st.session_state.stopwatch_value=time.time()-st.session_state.start_time; st.rerun()
        if b3.button("Reset"): st.session_state.is_running=False; st.session_state.stopwatch_value=0.0; st.rerun()

        st.divider()
        c1, c2, c3 = st.columns(3)
        st.session_state.t1 = c1.number_input("T1", 0.0, key="vt1")
        st.session_state.t2 = c2.number_input("T2", 0.0, key="vt2")
        st.session_state.t3 = c3.number_input("T3", 0.0, key="vt3")
        
        valid = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0]
        st.session_state.tug_avg = sum(valid)/len(valid) if valid else 0.0
        
        if st.session_state.tug_avg > 0:
            color = "#C0392B" if st.session_state.tug_avg >= 13.5 else "#28B463"
            msg = "High Risk" if st.session_state.tug_avg >= 13.5 else "Normal"
            st.markdown(f"<h3 style='text-align:center; color:{color}'>{st.session_state.tug_avg:.2f} s ({msg})</h3>", unsafe_allow_html=True)


# =========================================================
# 🖨️ PART B: PRINT REPORT (สร้าง HTML โดยตรง)
# =========================================================
def show_print_report():
    # ฟังก์ชันช่วยแปลง List เป็น String
    def fmt(val):
        if isinstance(val, list): return ", ".join(val) if val else "-"
        return val if val else "-"

    ss = st.session_state # ย่อให้เขียนง่ายขึ้น

    # คำนวณค่าต่างๆ เพื่อใส่ใน Report
    age = datetime.now().year + 543 - ss.birth_year
    fall_txt = "ไม่มี"
    if ss.fall_hist == "มี":
        inj = "บาดเจ็บ" if ss.fall_inj else "ไม่เจ็บ"
        fall_txt = f"มี ({ss.fall_freq}) - {inj}"
    
    tug_color = "#C0392B" if ss.tug_avg >= 13.5 else "#28B463"
    tug_res = "High Risk" if ss.tug_avg >= 13.5 else "Normal"

    # --- HTML TEMPLATE (นี่คือหัวใจสำคัญ) ---
    html_content = f"""
    <div style="font-family: Sarabun, sans-serif; padding: 20px; line-height: 1.5;">
        <div style="text-align:center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px;">
            <h2 style="margin:0;">📄 รายงานผลการประเมิน (Prosthesis Registry Report)</h2>
            <p style="margin:0; font-size: 14px; color: gray;">พิมพ์เมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>

        <h3 style="background:#eee; padding:5px;">1. ข้อมูลทั่วไป (General Information)</h3>
        <table style="width:100%; border-collapse: collapse;">
            <tr>
                <td style="width:33%"><b>ชื่อ-สกุล:</b> {fmt(ss.fname)}</td>
                <td style="width:33%"><b>HN:</b> {fmt(ss.hn)}</td>
                <td style="width:33%"><b>อายุ:</b> {age} ปี</td>
            </tr>
            <tr>
                <td><b>เพศ:</b> {ss.gender}</td>
                <td><b>น้ำหนัก:</b> {ss.weight} กก.</td>
                <td><b>ส่วนสูง:</b> {ss.height} ซม.</td>
            </tr>
            <tr>
                <td><b>สัญชาติ:</b> {fmt(ss.nationality)}</td>
                <td><b>จังหวัด:</b> {ss.province}</td>
                <td><b>ประเทศ:</b> {fmt(ss.country)}</td>
            </tr>
        </table>

        <h3 style="background:#eee; padding:5px; margin-top:15px;">2. ข้อมูลทางการแพทย์ (Medical History)</h3>
        <table style="width:100%;">
            <tr>
                <td style="width:50%; vertical-align:top;">
                    <b>โรคประจำตัว:</b> {fmt(ss.comorbidities)}<br>
                    <b>สาเหตุตัดขา:</b> {fmt(ss.cause)}<br>
                    <b>ปีที่ตัดขา:</b> {ss.amp_year} (ข้าง{ss.side})<br>
                    <b>K-Level (ก่อน):</b> {ss.k_level}
                </td>
                <td style="width:50%; vertical-align:top;">
                    <b>ระดับการตัด:</b> {ss.amp_level}<br>
                    <b>ตอขา:</b> {ss.stump_len}, {ss.stump_shape}<br>
                    <b>ผ่าตัดเพิ่ม:</b> {ss.surgery} ({fmt(ss.surg_details)})
                </td>
            </tr>
        </table>

        <h3 style="background:#eee; padding:5px; margin-top:15px;">3. ข้อมูลการฟื้นฟู (Rehabilitation)</h3>
        <p>
            <b>บุคลากรที่ดูแล:</b> {fmt(ss.personnel)} <br>
            <b>เคยฟื้นฟู:</b> {ss.rehab_status} (กิจกรรม: {fmt(ss.activities)})
        </p>

        <h3 style="background:#eee; padding:5px; margin-top:15px;">4. ข้อมูลกายอุปกรณ์ (Prosthesis)</h3>
        <table style="width:100%;">
            <tr>
                <td><b>บริการครั้งนี้:</b> {fmt(ss.service)}</td>
                <td><b>วันรับขา:</b> {ss.date_deliv}</td>
            </tr>
            <tr>
                <td colspan="2"><hr style="margin:5px 0;"></td>
            </tr>
            <tr>
                <td style="vertical-align:top;">
                    <b>Socket:</b> {fmt(ss.socket)}<br>
                    <b>Liner:</b> {fmt(ss.liner)}<br>
                    <b>Knee:</b> {fmt(ss.knee)}
                </td>
                <td style="vertical-align:top;">
                    <b>Suspension:</b> {fmt(ss.suspension)}<br>
                    <b>Foot:</b> {fmt(ss.foot)}
                </td>
            </tr>
        </table>

        <h3 style="background:#eee; padding:5px; margin-top:15px;">5. สังคมและการใช้งาน (Social & Function)</h3>
        <table style="width:100%;">
            <tr>
                <td><b>อุปกรณ์ช่วยเดิน:</b> {ss.assist}</td>
                <td><b>ยืน/วัน:</b> {ss.stand_hours}</td>
                <td><b>เดิน/วัน:</b> {ss.walk_hours}</td>
            </tr>
        </table>
        <p><b>ประวัติล้ม (6ด.):</b> {fall_txt}</p>
        
        <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-top:5px;">
            <b>การประเมินตนเอง (Self-Evaluation):</b><br>
            • ปัญหาสังคม (ตนเอง/เทียบคนอื่น): <u>{ss.q31_1}</u> / <u>{ss.q31_2}</u><br>
            • ปัญหางาน (ตนเอง/เทียบคนอื่น): <u>{ss.q32_1}</u> / <u>{ss.q32_2}</u>
        </div>
        
        <p style="margin-top:10px;">
            <b>การสนับสนุนครอบครัว:</b> {ss.supp_family} | 
            <b>หน่วยงาน:</b> {ss.supp_org} ({fmt(ss.supp_sources)})
        </p>

        <h3 style="background:#eee; padding:5px; margin-top:15px;">6. ผลทดสอบ TUG Test</h3>
        <div style="display:flex; justify-content: space-between; align-items: center; border: 2px solid {tug_color}; padding: 10px; border-radius: 8px;">
            <div>
                Trial 1: {ss.t1} s<br>
                Trial 2: {ss.t2} s<br>
                Trial 3: {ss.t3} s
            </div>
            <div style="text-align:right;">
                <h1 style="margin:0; color:{tug_color};">{ss.tug_avg:.2f} s</h1>
                <b style="color:{tug_color};">{tug_res}</b>
            </div>
        </div>
    </div>
    """

    # Render HTML to screen (Printer friendly)
    st.markdown(html_content, unsafe_allow_html=True)

    # Back Button
    st.divider()
    if st.button("⬅️ กลับไปแก้ไข (Edit Mode)", use_container_width=True):
        st.session_state.print_mode = False
        st.rerun()
    st.info("💡 กด Ctrl + P เพื่อพิมพ์ (ติ๊กเลือก Background Graphics เพื่อให้เห็นแถบสี)")

# =========================================================
# MAIN APP
# =========================================================
if st.session_state.print_mode:
    show_print_report()
else:
    show_input_form()