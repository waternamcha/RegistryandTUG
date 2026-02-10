import streamlit as st
import time
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ & CSS (Print Fix Version) ---
st.set_page_config(page_title="Prosthesis Registry & OM", page_icon="🦿", layout="wide")

st.markdown("""
    <style>
    /* นาฬิกา TUG ใหญ่ชัดเจน */
    div[data-testid="stMetricValue"] {
        font-size: 70px !important;
        font-family: 'Courier New', monospace;
        font-weight: 700;
        color: #1F618D;
    }
    
    /* กล่องผลลัพธ์ */
    .result-box-normal { padding: 10px; background-color: #D4EFDF; border: 2px solid #28B463; border-radius: 8px; text-align: center; }
    .result-box-risk { padding: 10px; background-color: #FADBD8; border: 2px solid #C0392B; border-radius: 8px; text-align: center; }
    
    /* =========================================
       🖨️ CSS สำหรับโหมดพิมพ์ (PRINT FULL)
       ========================================= */
    @media print {
        /* ซ่อนปุ่มและเมนูที่ไม่จำเป็น */
        .stButton, button, .stAppHeader, footer, [data-testid="stSidebar"], .stDeployButton, header { 
            display: none !important; 
        }
        
        /* ตั้งค่าหน้ากระดาษ A4 */
        @page { size: A4; margin: 1cm; }
        
        html, body {
            width: 100%; height: 100%; margin: 0 !important; padding: 0 !important;
            font-size: 11pt; line-height: 1.4;
            overflow: visible !important;
        }

        /* ปรับ Layout ให้เต็มหน้า */
        .block-container {
            width: 100% !important; max-width: 100% !important;
            padding: 0 !important; margin: 0 !important;
            overflow: visible !important;
        }

        /* ซ่อน Tab */
        .stTabs [role="tablist"] { display: none !important; }
        
        /* บังคับพิมพ์สีพื้นหลัง */
        * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        
        /* การตัดหน้า */
        .no-break { page-break-inside: avoid; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ตัวแปร Session State (เก็บข้อมูลให้ครบ 33 ข้อ) ---
defaults = {
    'print_mode': False, 'is_running': False, 'start_time': None, 'stopwatch_value': 0.0,
    # 1. General
    'fname': '', 'hn': '', 'birth_year': 2520, 'gender': 'ชาย', 
    'weight': 60.0, 'height': 170, 'nationality': 'ไทย', 'country': 'Thailand', 'province': 'กรุงเทพมหานคร',
    # 2. Medical
    'comorbidities': [], 'cause': 'อุบัติเหตุ', 'amp_level': 'Transtibial', 'side': 'ขวา', 'amp_year': 2566,
    'stump_len': 'ปานกลาง', 'stump_shape': 'Cylindrical', 'surgery': 'ไม่ใช่', 'k_level': 'K3',
    # 3. Rehab
    'personnel': [], 'rehab_status': 'ไม่เคย', 'activities': [],
    # 4. Prosthesis
    'service': [], 'date_cast': None, 'date_deliv': None,
    'socket': 'PTB', 'liner': [], 'suspension': [], 'foot': [], 'knee': [], # <-- เพิ่ม Knee
    # 5. Social
    'assist': 'ไม่ใช้', 'stand_hours': '1-3 ชม.', 'walk_hours': '1-3 ชม.', 
    'fall_hist': 'ไม่มี', 'fall_freq': '', 'fall_inj': False,
    'q31_1': 'ไม่มีปัญหา (0-4%)', 'q31_2': 'ไม่มีปัญหา (0-4%)',
    'q32_1': 'ไม่มีปัญหา (0-4%)', 'q32_2': 'ไม่มีปัญหา (0-4%)',
    'supp_family': 'ใช่', 'supp_org': 'ไม่ใช่', 'supp_sources': [],
    # TUG
    't1': 0.0, 't2': 0.0, 't3': 0.0, 'tug_avg': 0.0
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
# 📝 FUNCTION: Edit Mode (กรอกข้อมูล)
# =========================================================
def show_input_form():
    st.title("🦿 Digital Prosthesis Registry & OM Platform")
    
    col_h1, col_h2 = st.columns([3, 1])
    with col_h2:
        if st.button("📄 สรุปข้อมูล & สั่งพิมพ์ (Print)", type="primary", use_container_width=True):
            st.session_state.print_mode = True
            st.rerun()

    tab1, tab2 = st.tabs(["📋 Patient Registry (กรอกประวัติ)", "⏱️ TUG Test (จับเวลา)"])

    with tab1:
        st.header("แบบสำรวจประวัติผู้ใช้ขาเทียม (Items 1-33)")
        
        # --- PART 1: General (ข้อ 1-8) ---
        with st.expander("👤 1. ข้อมูลทั่วไป (ข้อ 1-8)", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state.hn = st.text_input("6. HN", key="i_hn")
                st.session_state.fname = st.text_input("ชื่อ-นามสกุล", key="i_fname")
                st.session_state.birth_year = st.selectbox("1. ปีเกิด (พ.ศ.)", YEARS_LIST, key="i_byear")
            with c2:
                st.session_state.gender = st.selectbox("2. เพศ", ["ชาย", "หญิง"], key="i_gen")
                st.session_state.nationality = st.selectbox("5. สัญชาติ", ["ไทย", "Other"], key="i_nat")
                if st.session_state.nationality == "Other": st.text_input("ระบุสัญชาติ", key="nat_ot")
                st.session_state.province = st.selectbox("4. จังหวัด", THAI_PROVINCES, key="i_prov")
            with c3:
                st.session_state.country = st.selectbox("3. ประเทศ", COUNTRIES, key="i_cnt")
                if st.session_state.country == "Other": st.text_input("ระบุประเทศ", key="cnt_ot")
                st.session_state.weight = st.number_input("7. น้ำหนัก (กก.)", 0.0, 200.0, key="i_wt")
                st.session_state.height = st.number_input("8. ส่วนสูง (ซม.)", 0, 250, key="i_ht")

        # --- PART 2: Medical (ข้อ 9-17) ---
        with st.expander("🏥 2. ข้อมูลการตัดขาและสุขภาพ (ข้อ 9-17)"):
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.comorbidities = st.multiselect("9. โรคประจำตัว", ["เบาหวาน", "ความดัน", "หัวใจ", "ไม่มี", "Other"], key="i_comorb")
                if "Other" in st.session_state.comorbidities: st.text_input("ระบุโรคอื่น", key="comorb_ot")
                
                st.session_state.cause = st.selectbox("10. สาเหตุ", ["อุบัติเหตุ", "เบาหวาน", "มะเร็ง", "Other"], key="i_cause")
                if st.session_state.cause == "Other": st.text_input("ระบุสาเหตุ", key="cause_ot")
                
                st.session_state.amp_year = st.number_input("11. ปีที่ตัดขา (พ.ศ.)", 2490, 2600, key="i_ayear")
                st.session_state.side = st.radio("12. ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True, key="i_side")

            with c2:
                st.session_state.amp_level = st.selectbox("13. ระดับ", ["Transtibial", "Transfemoral", "Knee Disarticulation", "Other"], key="i_lvl")
                if st.session_state.amp_level == "Other": st.text_input("ระบุระดับ", key="level_ot")
                
                st.session_state.stump_len = st.selectbox("14. ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"], key="i_slen")
                st.session_state.stump_shape = st.selectbox("15. รูปทรง", ["Conical", "Cylindrical", "Bulbous", "Other"], key="i_shp")
                if st.session_state.stump_shape == "Other": st.text_input("ระบุทรง", key="shape_ot")
                
                st.session_state.surgery = st.radio("16. ผ่าตัดเพิ่มเติม?", ["ไม่ใช่", "ใช่"], key="i_surg")
                if st.session_state.surgery == "ใช่":
                    st.session_state.surg_details = st.multiselect("ระบุการผ่าตัด", ["ตัดกระดูก", "ตัดผิวหนัง", "Other"], key="i_surg_d")
                    if "Other" in st.session_state.surg_details: st.text_input("ระบุผ่าตัดอื่น", key="surg_ot")
                
                st.session_state.k_level = st.selectbox("17. K-Level ก่อนตัด", ["K0", "K1", "K2", "K3", "K4"], key="i_klevel")

        # --- PART 3: Rehab (ข้อ 18-19) ---
        with st.expander("🩺 3. ข้อมูลการฟื้นฟู (ข้อ 18-19)"):
            st.session_state.personnel = st.multiselect("18. บุคลากร", ["นักกายอุปกรณ์", "นักกายภาพ", "แพทย์", "Other"], key="i_pers")
            if "Other" in st.session_state.personnel: st.text_input("ระบุบุคลากร", key="pers_ot")
            
            st.session_state.rehab_status = st.radio("19. เคยฟื้นฟู?", ["ไม่เคย", "เคย"], key="i_reh")
            if st.session_state.rehab_status == "เคย":
                st.session_state.activities = st.multiselect("19.1 กิจกรรม", ["ใส่ถุงลดบวม", "พันผ้ายืด", "ฝึกเดิน", "Other"], key="i_act")
                if "Other" in st.session_state.activities: st.text_input("ระบุกิจกรรม", key="act_ot")

        # --- PART 4: Prosthesis (ข้อ 20-27) ---
        with st.expander("🦾 4. ข้อมูลกายอุปกรณ์ (ข้อ 20-27)"):
            st.session_state.service = st.multiselect("20. บริการครั้งนี้", ["ทำใหม่", "เปลี่ยนเบ้า", "ซ่อม", "Other"], key="i_serv")
            if "Other" in st.session_state.service: st.text_input("ระบุบริการ", key="serv_ot")
            
            d1, d2 = st.columns(2)
            with d1: st.session_state.date_cast = st.date_input("21. วันที่หล่อแบบ", key="i_dcast")
            with d2: st.session_state.date_deliv = st.date_input("22. วันที่รับ", key="i_ddeliv")
            
            st.divider()
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.session_state.socket = st.selectbox("23. Socket", ["PTB", "TSB", "Ischial", "Other"], key="i_sock")
                if st.session_state.socket == "Other": st.text_input("ระบุ Socket", key="sock_ot")
                
                st.session_state.liner = st.multiselect("24. Liner", ["No liner", "Foam", "Silicone", "Other"], key="i_liner")
                if "Other" in st.session_state.liner: st.text_input("ระบุ Liner", key="liner_ot")
            
            with c_p2:
                st.session_state.suspension = st.multiselect("25. Suspension", ["Suction", "Pin lock", "Belt", "Other"], key="i_susp")
                if "Other" in st.session_state.suspension: st.text_input("ระบุ Suspension", key="susp_ot")
                
                st.session_state.foot = st.multiselect("26. Foot", ["SACH", "Single axis", "Dynamic", "Other"], key="i_foot")
                if "Other" in st.session_state.foot: st.text_input("ระบุ Foot", key="foot_ot")

            # ข้อ 27 Knee (เพิ่มใหม่ตาม PDF)
            if st.session_state.amp_level in ["Transfemoral", "Knee Disarticulation"]:
                st.session_state.knee = st.multiselect("27. Knee (ข้อเข่า)", ["Single axis", "Polycentric", "Hydraulic", "Other"], key="i_knee")
                if "Other" in st.session_state.knee: st.text_input("ระบุ Knee", key="knee_ot")

        # --- PART 5: Social (ข้อ 28-33) ---
        with st.expander("🌍 5. สังคมและการใช้งาน (ข้อ 28-33)"):
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                st.session_state.assist = st.selectbox("28. อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "ไม้เท้า", "Walker", "Other"], key="i_asst")
                if st.session_state.assist == "Other": st.text_input("ระบุอุปกรณ์", key="asst_ot")
                st.session_state.stand_hours = st.selectbox("29.1 ยืน/วัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="i_std")
                st.session_state.walk_hours = st.selectbox("29.2 เดิน/วัน", ["< 1 ชม.", "1-3 ชม.", "> 3 ชม."], key="i_wlk")
            with c_s2:
                st.session_state.fall_hist = st.radio("30. ประวัติล้ม (6ด.)", ["ไม่มี", "มี"], key="i_fall")
                if st.session_state.fall_hist == "มี":
                    st.session_state.fall_freq = st.selectbox("30.1 ความถี่", ["1-2 ครั้ง", "> 2 ครั้ง"], key="i_ffreq")
                    st.session_state.fall_inj = st.checkbox("30.2 บาดเจ็บ", key="i_finj")
            
            st.divider()
            st.write("31.1 ปัญหาการมีส่วนร่วมในสังคม (เทียบตนเอง)")
            st.session_state.q31_1 = st.radio("L1", PROBLEM_LEVELS, horizontal=True, label_visibility="collapsed", key="i_q31_1")
            st.write("31.2 ปัญหาการมีส่วนร่วมในสังคม (เทียบคนอื่น)")
            st.session_state.q31_2 = st.radio("L2", PROBLEM_LEVELS, horizontal=True, label_visibility="collapsed", key="i_q31_2")
            st.write("32.1 ปัญหาในการทำงาน (เทียบตนเอง)")
            st.session_state.q32_1 = st.radio("L3", PROBLEM_LEVELS, horizontal=True, label_visibility="collapsed", key="i_q32_1")
            st.write("32.2 ปัญหาในการทำงาน (เทียบคนอื่น)")
            st.session_state.q32_2 = st.radio("L4", PROBLEM_LEVELS, horizontal=True, label_visibility="collapsed", key="i_q32_2")

            st.divider()
            # ข้อ 33 (เพิ่มใหม่ตาม PDF)
            st.session_state.supp_family = st.radio("33.1 การดูแลจากครอบครัว", ["ใช่", "ไม่ใช่"], key="i_sfam")
            st.session_state.supp_org = st.radio("33.2 การสนับสนุนจากหน่วยงาน", ["ใช่", "ไม่ใช่"], key="i_sorg")
            if st.session_state.supp_org == "ใช่":
                st.session_state.supp_sources = st.multiselect("ระบุหน่วยงาน", ["รัฐ", "เอกชน", "Other"], key="i_ssrc")
                if "Other" in st.session_state.supp_sources: st.text_input("ระบุหน่วยงานอื่น", key="supp_ot")

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
            st.session_state.t1 = st.number_input("Trial 1 (s)", 0.0, format="%.2f", key="vt1")
            st.session_state.t2 = st.number_input("Trial 2 (s)", 0.0, format="%.2f", key="vt2")
            st.session_state.t3 = st.number_input("Trial 3 (s)", 0.0, format="%.2f", key="vt3")
            valid = [t for t in [st.session_state.t1, st.session_state.t2, st.session_state.t3] if t > 0]
            if valid:
                avg = sum(valid)/len(valid)
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
# 🖨️ FUNCTION: Print Mode (ดึงข้อมูลครบทุกเม็ด)
# =========================================================
def show_print_report():
    def get_text(val, other_key, suffix=""):
        if isinstance(val, list):
            res = ", ".join(val)
            if "Other" in val and other_key in st.session_state: res += f" ({st.session_state[other_key]})"
            return res if res else "-"
        else:
            if val == "Other" and other_key in st.session_state: return f"{st.session_state[other_key]} {suffix}"
            return f"{val} {suffix}"

    st.markdown(f"""
    <div style="text-align: center;">
        <h2 style="margin-bottom:0px;">📄 รายงานผลการประเมินผู้ใช้ขาเทียม (Prosthesis Report)</h2>
        <p style="color:gray; font-size:14px;">วันที่พิมพ์: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    </div>
    <hr style="border: 1px solid #ddd; margin: 10px 0;">
    """, unsafe_allow_html=True)

    # 1. ข้อมูลทั่วไป
    st.subheader("1. ข้อมูลทั่วไป")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**ชื่อ-สกุล:** {st.session_state.fname or '-'}")
    c1.markdown(f"**HN:** {st.session_state.hn or '-'}")
    c1.markdown(f"**อายุ:** {current_year_be - st.session_state.birth_year} ปี")
    
    c2.markdown(f"**เพศ:** {st.session_state.gender}")
    c2.markdown(f"**น้ำหนัก:** {st.session_state.weight} กก.")
    c2.markdown(f"**ส่วนสูง:** {st.session_state.height} ซม.")
    
    c3.markdown(f"**จังหวัด:** {st.session_state.province}")
    c3.markdown(f"**สัญชาติ:** {get_text(st.session_state.nationality, 'nat_ot')}")
    c3.markdown(f"**ประเทศ:** {get_text(st.session_state.country, 'cnt_ot')}")

    # 2. ข้อมูลการแพทย์
    st.markdown("<div class='no-break'>", unsafe_allow_html=True)
    st.subheader("2. ข้อมูลทางการแพทย์ & กายอุปกรณ์")
    mc1, mc2 = st.columns(2)
    with mc1:
        st.markdown(f"**โรคประจำตัว:** {get_text(st.session_state.comorbidities, 'comorb_ot')}")
        st.markdown(f"**สาเหตุ:** {get_text(st.session_state.cause, 'cause_ot')}")
        st.markdown(f"**ระดับตัดขา:** {get_text(st.session_state.amp_level, 'level_ot')} ({st.session_state.side})")
        st.markdown(f"**ปีที่ตัดขา:** {st.session_state.amp_year}")
        st.markdown(f"**ตอขา:** {st.session_state.stump_len}, {get_text(st.session_state.stump_shape, 'shape_ot')}")
        
        surg_txt = "ไม่เคย"
        if st.session_state.surgery == "ใช่": surg_txt = f"เคย ({get_text(st.session_state.surg_details, 'surg_ot')})"
        st.markdown(f"**ผ่าตัดเพิ่ม:** {surg_txt}")
        st.markdown(f"**K-Level (ก่อน):** {st.session_state.k_level}")

    with mc2:
        st.markdown(f"**บริการ:** {get_text(st.session_state.service, 'serv_ot')}")
        st.markdown(f"**Socket:** {get_text(st.session_state.socket, 'sock_ot')}")
        st.markdown(f"**Suspension:** {get_text(st.session_state.suspension, 'susp_ot')}")
        st.markdown(f"**Foot:** {get_text(st.session_state.foot, 'foot_ot')}")
        
        # Knee (แสดงเฉพาะถ้ามี)
        if st.session_state.knee:
            st.markdown(f"**Knee:** {get_text(st.session_state.knee, 'knee_ot')}")
            
        st.markdown(f"**Liner:** {get_text(st.session_state.liner, 'liner_ot')}")
        st.markdown(f"**วันที่รับขา:** {st.session_state.date_deliv}")
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. ข้อมูลฟื้นฟู & สังคม
    st.markdown("<div class='no-break'>", unsafe_allow_html=True)
    st.subheader("3. ข้อมูลฟื้นฟูและสังคม")
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(f"**บุคลากร:** {get_text(st.session_state.personnel, 'pers_ot')}")
        st.markdown(f"**ฟื้นฟู:** {st.session_state.rehab_status}")
        st.markdown(f"**อุปกรณ์ช่วย:** {get_text(st.session_state.assist, 'asst_ot')}")
        st.markdown(f"**ยืน/เดิน (วัน):** {st.session_state.stand_hours} / {st.session_state.walk_hours}")
    with sc2:
        fall_txt = "ไม่มี"
        if st.session_state.fall_hist == "มี":
            inj = "บาดเจ็บ" if st.session_state.fall_inj else "ไม่เจ็บ"
            fall_txt = f"มี ({st.session_state.fall_freq}) - {inj}"
        st.markdown(f"**ประวัติล้ม:** {fall_txt}")
        
        st.markdown(f"**ดูแลจากครอบครัว:** {st.session_state.supp_family}")
        supp_org_txt = "ไม่มี"
        if st.session_state.supp_org == "ใช่": supp_org_txt = get_text(st.session_state.supp_sources, 'supp_ot')
        st.markdown(f"**สนับสนุนจากองค์กร:** {supp_org_txt}")
    
    st.write("**การประเมินตนเอง (Self-Evaluation):**")
    st.write(f"• สังคม (คาดหวัง/เทียบคนอื่น): {st.session_state.q31_1} / {st.session_state.q31_2}")
    st.write(f"• งาน (คาดหวัง/เทียบคนอื่น): {st.session_state.q32_1} / {st.session_state.q32_2}")
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. TUG Result
    st.markdown("<div class='no-break'>", unsafe_allow_html=True)
    st.subheader("4. ผลทดสอบ TUG (Timed Up and Go)")
    
    t_avg = st.session_state.get('tug_avg', 0.0)
    tc1, tc2 = st.columns([1, 2])
    with tc1:
        st.write(f"Trial 1: {st.session_state.t1:.2f} s")
        st.write(f"Trial 2: {st.session_state.t2:.2f} s")
        st.write(f"Trial 3: {st.session_state.t3:.2f} s")
    with tc2:
        if t_avg > 0:
            status = "⚠️ High Fall Risk (เสี่ยงล้มสูง)" if t_avg >= 13.5 else "✅ Normal Mobility (ปกติ)"
            color = "#C0392B" if t_avg >= 13.5 else "#28B463"
            st.markdown(f"""
            <div style="border: 2px solid {color}; padding: 10px; border-radius: 8px; text-align: center; background-color: {'#FADBD8' if t_avg >= 13.5 else '#D4EFDF'};">
                <h3 style="margin:0; color: {color};">Average: {t_avg:.2f} sec</h3>
                <p style="margin:5px 0 0 0;">{status}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("ยังไม่ได้ทำการทดสอบ")
    st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.divider()
    col_b1, col_b2 = st.columns([1, 4])
    with col_b1:
        if st.button("⬅️ แก้ไขข้อมูล (Edit)", use_container_width=True):
            st.session_state.print_mode = False
            st.rerun()
    with col_b2:
        st.info("💡 **คำแนะนำการพิมพ์:** กด `Ctrl + P` > เลือก 'Save as PDF' > ที่ More settings ให้ติ๊ก **'Background graphics'** เพื่อให้เห็นสี")

# =========================================================
# Main Controller
# =========================================================
if st.session_state.print_mode:
    show_print_report()
else:
    show_input_form()