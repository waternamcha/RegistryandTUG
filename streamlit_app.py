import streamlit as st
import time
from datetime import datetime, date

# --- 1. ตั้งค่าหน้าเว็บ & CSS ---
st.set_page_config(page_title="Prosthesis Registry & OM", page_icon="🦿", layout="wide")

st.markdown("""
    <style>
    /* นาฬิกา TUG */
    div[data-testid="stMetricValue"] {
        font-size: 70px !important;
        font-family: 'Courier New', monospace;
        font-weight: 700;
        color: #1F618D;
    }
    /* กล่องผลลัพธ์ */
    .result-box-normal { padding: 15px; background-color: #D4EFDF; border: 2px solid #28B463; border-radius: 10px; text-align: center; }
    .result-box-risk { padding: 15px; background-color: #FADBD8; border: 2px solid #C0392B; border-radius: 10px; text-align: center; }
    
    /* CSS สำหรับการพิมพ์ (Print Mode) */
    @media print {
        .stButton, button, .stAppHeader, footer, [data-testid="stSidebar"], .stDeployButton { display: none !important; }
        .block-container { padding: 1rem !important; }
        .stTabs [role="tablist"] { display: none !important; }
        .no-print { display: none !important; }
        
        /* จัด Font ตอนปริ้นให้อ่านง่าย */
        body { font-family: 'Sarabun', sans-serif; font-size: 12pt; }
        h1, h2, h3 { color: #000 !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ตัวแปร Session State ---
# กำหนดค่าเริ่มต้นถ้ายังไม่มี
defaults = {
    'print_mode': False, 'is_running': False, 'start_time': None, 'stopwatch_value': 0.0,
    'fname': '', 'hn': '', 'birth_year': 2520, 'gender': 'ชาย', 
    'weight': 60.0, 'height': 170, 'nationality': 'ไทย', 'country': 'Thailand', 'province': 'กรุงเทพมหานคร',
    'comorbidities': [], 'cause': 'อุบัติเหตุ', 'amp_level': 'Transtibial', 'side': 'ขวา', 'amp_year': 2566,
    'stump_len': 'ปานกลาง', 'stump_shape': 'Cylindrical', 'surgery': 'ไม่ใช่',
    'k_level': 'K3', 'personnel': [], 'rehab_status': 'ไม่เคย',
    'service': [], 'socket': 'PTB', 'liner': [], 'suspension': [], 'foot': [], 'knee': [],
    'assist': 'ไม่ใช้', 'stand_hours': '1-3 ชม.', 'walk_hours': '1-3 ชม.', 'fall_hist': 'ไม่มี',
    'q31_1': 'ไม่มีปัญหา (0-4%)', 'q31_2': 'ไม่มีปัญหา (0-4%)',
    'q32_1': 'ไม่มีปัญหา (0-4%)', 'q32_2': 'ไม่มีปัญหา (0-4%)',
    'supp_family': 'ใช่', 'supp_org': 'ไม่ใช่',
    't1': 0.0, 't2': 0.0, 't3': 0.0
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 3. ข้อมูลตัวเลือก ---
THAI_PROVINCES = ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "สงขลา", "ชลบุรี", "นครราชสีมา", "ภูเก็ต", "อื่นๆ"] 
COUNTRIES = ["Thailand", "Other"]
current_year_be = datetime.now().year + 543
YEARS_LIST = list(range(current_year_be, current_year_be - 100, -1))
PROBLEM_LEVELS = ["ไม่มีปัญหา (0-4%)", "มีปัญหาเล็กน้อย (5-24%)", "มีปัญหาปานกลาง (25-49%)", "มีปัญหามาก (50-95%)", "มีปัญหามากที่สุด (96-100%)"]

# =========================================================
# 📝 FUNCTION: ส่วนกรอกข้อมูล (Edit Mode)
# =========================================================
def show_input_form():
    st.title("🦿 Digital Prosthesis Registry & OM Platform")
    
    # ปุ่มไปหน้า Preview
    col_h1, col_h2 = st.columns([3, 1])
    with col_h2:
        if st.button("📄 สรุปข้อมูล & สั่งพิมพ์ (Print Preview)", type="primary", use_container_width=True):
            st.session_state.print_mode = True
            st.rerun()

    tab1, tab2 = st.tabs(["📋 Patient Registry (กรอกประวัติ)", "⏱️ TUG Test (จับเวลา)"])

    # --- TAB 1: Registry ---
    with tab1:
        st.header("แบบสำรวจประวัติผู้ใช้ขาเทียม")
        
        # 1. General Info
        with st.expander("👤 1. ข้อมูลทั่วไป (General Info)", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state.hn = st.text_input("HN (เลขประจำตัวผู้ป่วย)", key="input_hn")
                st.session_state.fname = st.text_input("ชื่อ-นามสกุล", key="input_fname")
                st.session_state.birth_year = st.selectbox("ปีเกิด (พ.ศ.)", YEARS_LIST, key="input_byear")
            with c2:
                st.session_state.gender = st.selectbox("เพศ", ["ชาย", "หญิง"], key="input_gender")
                st.session_state.nationality = st.selectbox("สัญชาติ", ["ไทย", "Other"], key="input_nat")
                if st.session_state.nationality == "Other": st.text_input("ระบุสัญชาติ", key="nat_ot")
                st.session_state.province = st.selectbox("จังหวัด", THAI_PROVINCES, key="input_prov")
            with c3:
                st.session_state.country = st.selectbox("ประเทศ", COUNTRIES, key="input_country")
                if st.session_state.country == "Other": st.text_input("ระบุประเทศ", key="country_ot")
                st.session_state.weight = st.number_input("น้ำหนัก (กก.)", 0.0, 200.0, key="input_weight")
                st.session_state.height = st.number_input("ส่วนสูง (ซม.)", 0, 250, key="input_height")

        # 2. Medical Info
        with st.expander("🏥 2. ข้อมูลการตัดขาและสุขภาพ"):
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.comorbidities = st.multiselect("โรคประจำตัว", ["เบาหวาน", "ความดัน", "หัวใจ", "ไม่มี", "Other"], key="input_comorb")
                if "Other" in st.session_state.comorbidities: st.text_input("ระบุโรคอื่น", key="comorb_ot")
                
                st.session_state.cause = st.selectbox("สาเหตุการตัดขา", ["อุบัติเหตุ", "เบาหวาน", "มะเร็ง", "Other"], key="input_cause")
                if st.session_state.cause == "Other": st.text_input("ระบุสาเหตุ", key="cause_ot")
                
                st.session_state.amp_year = st.number_input("ปีที่ตัดขา (พ.ศ.)", 2490, 2600, key="input_amp_year")
                st.session_state.side = st.radio("ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="input_side")

            with c2:
                st.session_state.amp_level = st.selectbox("ระดับการตัดขา", ["Transtibial", "Transfemoral", "Knee Disarticulation", "Other"], key="input_level")
                if st.session_state.amp_level == "Other": st.text_input("ระบุระดับ", key="level_ot")
                
                st.session_state.stump_len = st.selectbox("ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"], key="input_slen")
                st.session_state.stump_shape = st.selectbox("รูปทรงตอขา", ["Conical", "Cylindrical", "Bulbous", "Other"], key="input_shape")
                if st.session_state.stump_shape == "Other": st.text_input("ระบุทรง", key="shape_ot")
                
                st.session_state.surgery = st.radio("ผ่าตัดเพิ่มเติม?", ["ไม่ใช่", "ใช่"], key="input_surg")
                if st.session_state.surgery == "ใช่":
                    st.session_state.surg_details = st.multiselect("ระบุการผ่าตัด", ["ตัดกระดูก", "ตัดผิวหนัง", "Other"], key="input_surg_det")
                    if "Other" in st.session_state.surg_details: st.text_input("ระบุผ่าตัดอื่น", key="surg_ot")
                
                st.session_state.k_level = st.selectbox("K-Level ก่อนตัด", ["K0", "K1", "K2", "K3", "K4"], key="input_klevel")

        # 3. Rehab
        with st.expander("🩺 3. ข้อมูลการฟื้นฟู"):
            st.session_state.personnel = st.multiselect("บุคลากรที่ดูแล", ["นักกายอุปกรณ์", "นักกายภาพ", "แพทย์", "Other"], key="input_person")
            if "Other" in st.session_state.personnel: st.text_input("ระบุบุคลากร", key="person_ot")
            
            st.session_state.rehab_status = st.radio("เคยฟื้นฟูสมรรถภาพ?", ["ไม่เคย", "เคย"], key="input_rehab")
            if st.session_state.rehab_status == "เคย":
                st.session_state.activities = st.multiselect("กิจกรรมที่ทำ", ["ใส่ถุงลดบวม", "พันผ้ายืด", "ฝึกเดิน", "Other"], key="input_act")
                if "Other" in st.session_state.activities: st.text_input("ระบุกิจกรรม", key="act_ot")

        # 4. Prosthesis
        with st.expander("🦾 4. ข้อมูลกายอุปกรณ์"):
            st.session_state.service = st.multiselect("การรับบริการ", ["ทำใหม่", "เปลี่ยนเบ้า", "ซ่อม", "Other"], key="input_serv")
            if "Other" in st.session_state.service: st.text_input("ระบุบริการ", key="service_ot")
            
            d1, d2 = st.columns(2)
            with d1: st.session_state.date_cast = st.date_input("วันที่หล่อแบบ", key="input_dcast")
            with d2: st.session_state.date_deliv = st.date_input("วันที่รับอุปกรณ์", key="input_ddeliv")
            
            st.divider()
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.session_state.socket = st.selectbox("Socket", ["PTB", "TSB", "Ischial", "Other"], key="input_socket")
                if st.session_state.socket == "Other": st.text_input("ระบุ Socket", key="sock_ot")
                
                st.session_state.liner = st.multiselect("Liner", ["No liner", "Foam", "Silicone", "Other"], key="input_liner")
                if "Other" in st.session_state.liner: st.text_input("ระบุ Liner", key="liner_ot")
            
            with c_p2:
                st.session_state.suspension = st.multiselect("Suspension", ["Suction", "Pin lock", "Belt", "Other"], key="input_susp")
                if "Other" in st.session_state.suspension: st.text_input("ระบุ Suspension", key="susp_ot")
                
                st.session_state.foot = st.multiselect("Foot", ["SACH", "Single axis", "Dynamic", "Other"], key="input_foot")
                if "Other" in st.session_state.foot: st.text_input("ระบุ Foot", key="foot_ot")

        # 5. Social & Functional
        with st.expander("🌍 5. ข้อมูลสังคมและการใช้งาน"):
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                st.session_state.assist = st.selectbox("อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "ไม้เท้า", "Walker", "Other"], key="input_assist")
                if st.session_state.assist == "Other": st.text_input("ระบุอุปกรณ์", key="assist_ot")
                st.session_state.stand_hours = st.selectbox("เวลา 'ยืน' ต่อวัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="input_stand")
                st.session_state.walk_hours = st.selectbox("เวลา 'เดิน' ต่อวัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="input_walk")
            with c_s2:
                st.session_state.fall_hist = st.radio("ประวัติล้ม (6 เดือน)", ["ไม่มี", "มี"], key="input_fall")
                if st.session_state.fall_hist == "มี":
                    st.session_state.fall_freq = st.selectbox("ความถี่", ["1-2 ครั้ง", "> 2 ครั้ง"], key="input_ffreq")
                    st.session_state.fall_inj = st.checkbox("ได้รับบาดเจ็บ", key="input_finj")
            
            st.divider()
            st.write("31.1 ปัญหาการมีส่วนร่วมในสังคม (เทียบความคาดหวังตนเอง)")
            st.session_state.q31_1 = st.radio("Level", PROBLEM_LEVELS, horizontal=True, key="input_q31_1")
            
            st.write("31.2 ปัญหาการมีส่วนร่วมในสังคม (เทียบคนปกติ)")
            st.session_state.q31_2 = st.radio("Level", PROBLEM_LEVELS, horizontal=True, key="input_q31_2")
            
            st.write("32.1 ปัญหาในการทำงาน (เทียบความคาดหวังตนเอง)")
            st.session_state.q32_1 = st.radio("Level", PROBLEM_LEVELS, horizontal=True, key="input_q32_1")
            
            st.write("32.2 ปัญหาในการทำงาน (เทียบคนปกติ)")
            st.session_state.q32_2 = st.radio("Level", PROBLEM_LEVELS, horizontal=True, key="input_q32_2")

            st.divider()
            st.session_state.supp_family = st.radio("การดูแลจากครอบครัว", ["ใช่", "ไม่ใช่"], key="input_s_fam")
            st.session_state.supp_org = st.radio("การสนับสนุนจากหน่วยงาน", ["ใช่", "ไม่ใช่"], key="input_s_org")
            if st.session_state.supp_org == "ใช่":
                st.session_state.supp_sources = st.multiselect("ระบุหน่วยงาน", ["รัฐ", "เอกชน", "Other"], key="input_s_src")
                if "Other" in st.session_state.supp_sources: st.text_input("ระบุหน่วยงานอื่น", key="supp_ot")

    # --- TAB 2: TUG Test ---
    with tab2:
        st.header("⏱️ Timed Up and Go (TUG)")
        col_l, col_r = st.columns([1.5, 1])
        
        with col_l:
            with st.container(border=True):
                @st.fragment(run_every=0.1)
                def live_clock():
                    if st.session_state.is_running:
                        val = time.time() - st.session_state.start_time
                        st.metric("Time", f"{val:.2f} s")
                    else:
                        st.metric("Time", f"{st.session_state.stopwatch_value:.2f} s")
                live_clock()
            
            b1, b2, b3 = st.columns(3)
            if b1.button("▶️ START", disabled=st.session_state.is_running, use_container_width=True):
                st.session_state.is_running = True
                st.session_state.start_time = time.time()
                st.rerun()
            if b2.button("⏸️ STOP", disabled=not st.session_state.is_running, use_container_width=True):
                st.session_state.is_running = False
                st.session_state.stopwatch_value = time.time() - st.session_state.start_time
                st.rerun()
            if b3.button("🔄 RESET", use_container_width=True):
                st.session_state.is_running = False
                st.session_state.stopwatch_value = 0.0
                st.rerun()

        with col_r:
            st.session_state.t1 = st.number_input("Trial 1 (s)", 0.0, format="%.2f", key="val_t1")
            st.session_state.t2 = st.number_input("Trial 2 (s)", 0.0, format="%.2f", key="val_t2")
            st.session_state.t3 = st.number_input("Trial 3 (s)", 0.0, format="%.2f", key="val_t3")
            
            valid_trials = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0]
            if valid_trials:
                avg = sum(valid_trials) / len(valid_trials)
                st.session_state.tug_avg = avg
                
                if avg >= 13.5:
                    st.markdown(f'<div class="result-box-risk"><h3>High Risk</h3><h1>{avg:.2f} s</h1></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="result-box-normal"><h3>Normal</h3><h1>{avg:.2f} s</h1></div>', unsafe_allow_html=True)
            else:
                st.session_state.tug_avg = 0.0

    st.markdown("---")
    if st.button("💾 บันทึกและดูรายงาน (SAVE & PREVIEW)", type="primary", use_container_width=True):
        st.session_state.print_mode = True
        st.rerun()

# =========================================================
# 🖨️ FUNCTION: หน้ารายงานผล (Print Mode) - ดึงข้อมูลครบ
# =========================================================
def show_print_report():
    # Helper func to handle "Other" text
    def get_text(val, other_key, suffix=""):
        if isinstance(val, list): # For Multiselect
            res = ", ".join(val)
            if "Other" in val and other_key in st.session_state:
                res += f" ({st.session_state[other_key]})"
            return res
        else: # For Selectbox/Radio
            if val == "Other" and other_key in st.session_state:
                return f"{st.session_state[other_key]} {suffix}"
            return f"{val} {suffix}"

    # Header
    st.markdown(f"""
    <div style="text-align: center;">
        <h2>📄 รายงานผลการประเมินผู้ใช้ขาเทียม (Comprehensive Report)</h2>
        <p>วันที่พิมพ์: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    </div>
    <hr style="border: 1px solid #333;">
    """, unsafe_allow_html=True)

    # 1. ข้อมูลทั่วไป
    st.subheader("1. ข้อมูลทั่วไป (General Information)")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**ชื่อ-สกุล:** {st.session_state.fname}")
    col1.markdown(f"**HN:** {st.session_state.hn}")
    col1.markdown(f"**อายุ:** {current_year_be - st.session_state.birth_year} ปี")
    
    col2.markdown(f"**เพศ:** {st.session_state.gender}")
    col2.markdown(f"**น้ำหนัก:** {st.session_state.weight} กก.")
    col2.markdown(f"**ส่วนสูง:** {st.session_state.height} ซม.")
    
    nat_txt = get_text(st.session_state.nationality, 'nat_ot')
    cnt_txt = get_text(st.session_state.country, 'country_ot')
    col3.markdown(f"**สัญชาติ:** {nat_txt}")
    col3.markdown(f"**ประเทศ:** {cnt_txt}")
    col3.markdown(f"**จังหวัด:** {st.session_state.province}")

    # 2. ข้อมูลการแพทย์
    st.markdown("---")
    st.subheader("2. ข้อมูลทางการแพทย์ (Medical & Amputation)")
    c1, c2 = st.columns(2)
    
    comorb_txt = get_text(st.session_state.comorbidities, 'comorb_ot')
    cause_txt = get_text(st.session_state.cause, 'cause_ot')
    level_txt = get_text(st.session_state.amp_level, 'level_ot')
    shape_txt = get_text(st.session_state.stump_shape, 'shape_ot')
    
    c1.markdown(f"**โรคประจำตัว:** {comorb_txt}")
    c1.markdown(f"**สาเหตุการตัดขา:** {cause_txt}")
    c1.markdown(f"**ปีที่ตัดขา:** {st.session_state.amp_year}")
    c1.markdown(f"**ข้าง:** {st.session_state.side}")
    c1.markdown(f"**K-Level ก่อนตัด:** {st.session_state.k_level}")

    c2.markdown(f"**ระดับการตัด:** {level_txt}")
    c2.markdown(f"**ความยาวตอขา:** {st.session_state.stump_len}")
    c2.markdown(f"**รูปทรงตอขา:** {shape_txt}")
    
    surg_info = "ไม่เคย"
    if st.session_state.surgery == "ใช่":
        det = get_text(st.session_state.surg_details, 'surg_ot')
        surg_info = f"เคย ({det})"
    c2.markdown(f"**ผ่าตัดเพิ่มเติม:** {surg_info}")

    # 3. ข้อมูลกายอุปกรณ์
    st.markdown("---")
    st.subheader("3. ข้อมูลกายอุปกรณ์ (Prosthesis)")
    
    serv_txt = get_text(st.session_state.service, 'service_ot')
    sock_txt = get_text(st.session_state.socket, 'sock_ot')
    liner_txt = get_text(st.session_state.liner, 'liner_ot')
    susp_txt = get_text(st.session_state.suspension, 'susp_ot')
    foot_txt = get_text(st.session_state.foot, 'foot_ot')
    
    st.markdown(f"**บริการครั้งนี้:** {serv_txt}")
    st.markdown(f"**วันที่หล่อแบบ:** {st.session_state.date_cast} | **วันที่รับ:** {st.session_state.date_deliv}")
    
    pc1, pc2 = st.columns(2)
    pc1.markdown(f"**Socket:** {sock_txt}")
    pc1.markdown(f"**Liner:** {liner_txt}")
    pc2.markdown(f"**Suspension:** {susp_txt}")
    pc2.markdown(f"**Foot:** {foot_txt}")

    # 4. ข้อมูลฟื้นฟู & สังคม
    st.markdown("---")
    st.subheader("4. ข้อมูลฟื้นฟูและสังคม (Rehab & Social)")
    rc1, rc2 = st.columns(2)
    
    person_txt = get_text(st.session_state.personnel, 'person_ot')
    assist_txt = get_text(st.session_state.assist, 'assist_ot')
    
    rc1.markdown(f"**บุคลากรที่ดูแล:** {person_txt}")
    rc1.markdown(f"**เคยฟื้นฟู:** {st.session_state.rehab_status}")
    rc1.markdown(f"**อุปกรณ์ช่วยเดิน:** {assist_txt}")
    rc1.markdown(f"**เวลายืน/วัน:** {st.session_state.stand_hours}")
    
    fall_info = "ไม่มี"
    if st.session_state.fall_hist == "มี":
        inj = "(บาดเจ็บ)" if st.session_state.get('fall_inj', False) else "(ไม่เจ็บ)"
        fall_info = f"มี ({st.session_state.fall_freq}) {inj}"
    rc2.markdown(f"**ประวัติล้ม (6ด.):** {fall_info}")
    rc2.markdown(f"**เวลาเดิน/วัน:** {st.session_state.walk_hours}")
    
    st.markdown("**การประเมินตนเอง (Self-Evaluation):**")
    st.write(f"- สังคม (คาดหวัง): {st.session_state.q31_1}")
    st.write(f"- สังคม (เทียบคนอื่น): {st.session_state.q31_2}")
    st.write(f"- งาน (คาดหวัง): {st.session_state.q32_1}")
    st.write(f"- งาน (เทียบคนอื่น): {st.session_state.q32_2}")

    # 5. TUG Result
    st.markdown("---")
    st.subheader("5. ผลทดสอบ TUG (Timed Up and Go)")
    
    t_avg = st.session_state.get('tug_avg', 0.0)
    col_t1, col_t2 = st.columns([1, 2])
    
    with col_t1:
        st.write(f"Trial 1: **{st.session_state.t1:.2f} s**")
        st.write(f"Trial 2: **{st.session_state.t2:.2f} s**")
        st.write(f"Trial 3: **{st.session_state.t3:.2f} s**")
    
    with col_t2:
        if t_avg > 0:
            status = "⚠️ High Fall Risk" if t_avg >= 13.5 else "✅ Normal Mobility"
            color = "#C0392B" if t_avg >= 13.5 else "#28B463"
            st.markdown(f"""
            <div style="border: 2px solid {color}; padding: 10px; border-radius: 8px; text-align: center;">
                <h2 style="margin:0; color: {color};">{t_avg:.2f} sec</h2>
                <h4 style="margin:5px 0 0 0;">{status}</h4>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write("-")

    # Footer & Print Button
    st.divider()
    col_b1, col_b2 = st.columns([1, 4])
    with col_b1:
        if st.button("⬅️ แก้ไข (Edit)", use_container_width=True):
            st.session_state.print_mode = False
            st.rerun()
    with col_b2:
        st.info("💡 กด `Ctrl + P` หรือ `Cmd + P` เพื่อปริ้นเป็น PDF (ปุ่มต่างๆ จะถูกซ่อนอัตโนมัติ)")

# =========================================================
# Main Controller
# =========================================================
if st.session_state.print_mode:
    show_print_report()
else:
    show_input_form()