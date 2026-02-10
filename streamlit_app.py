import streamlit as st
import time
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ & Custom CSS ---
st.set_page_config(page_title="Prosthesis Registry & OM", page_icon="🦿", layout="wide")

st.markdown("""
    <style>
    /* ปรับแต่งตัวเลขนาฬิกา */
    div[data-testid="stMetricValue"] {
        font-size: 70px !important;
        font-family: 'Courier New', monospace;
        font-weight: 700;
        color: #1F618D;
    }
    /* หัวข้อ Expander */
    .streamlit-expanderHeader {
        background-color: #EBF5FB;
        font-weight: bold;
        color: #154360;
    }
    /* กล่องผลลัพธ์ */
    .result-box {
        padding: 15px;
        background-color: #f0f2f6;
        border-radius: 10px;
        border-left: 5px solid #2E86C1;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ข้อมูลรายการ (Lists) ---
THAI_PROVINCES = [
    "กรุงเทพมหานคร", "กระบี่", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา", "ชลบุรี", "ชัยนาท",
    "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่", "ตรัง", "ตราด", "ตาก", "นครนายก", "นครปฐม", "นครพนม", "นครราชสีมา",
    "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน", "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี", "ประจวบคีรีขันธ์",
    "ปราจีนบุรี", "ปัตตานี", "พระนครศรีอยุธยา", "พะเยา", "พังงา", "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์",
    "แพร่", "ภูเก็ต", "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยโสธร", "ยะลา", "ร้อยเอ็ด", "ระนอง", "ระยอง", "ราชบุรี",
    "ลพบุรี", "ลำปาง", "ลำพูน", "เลย", "ศรีสะเกษ", "สกลนคร", "สงขลา", "สตูล", "สมุทรปราการ", "สมุทรสงคราม", "สมุทรสาคร",
    "สระแก้ว", "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี", "สุราษฎร์ธานี", "สุรินทร์", "หนองคาย", "หนองบัวลำภู",
    "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", "อุตรดิตถ์", "อุทัยธานี", "อุบลราชธานี"
]

COUNTRIES = ["Thailand", "United States", "United Kingdom", "Japan", "China", "Germany", "France", "Australia", 
             "Laos", "Myanmar", "Cambodia", "Vietnam", "Malaysia", "Singapore", "Other"]

# สร้างลิสต์ปี พ.ศ. (ย้อนหลัง 100 ปี)
current_year_be = datetime.now().year + 543
YEARS_LIST = list(range(current_year_be, current_year_be - 100, -1))

st.title("🦿 Digital Prosthesis Registry & OM Platform")

# --- 3. สร้าง Tabs ---
tab1, tab2 = st.tabs(["📋 Patient Registry (ทะเบียนประวัติ)", "⏱️ TUG Test (จับเวลา & แปลผล)"])

# =========================================================
# 📌 TAB 1: Patient Registry (ปรับแก้ตาม Requirement)
# =========================================================
with tab1:
    st.header("แบบสำรวจประวัติผู้ใช้ขาเทียม")

    # --- Module 1: ข้อมูลทั่วไป ---
    with st.expander("👤 1. ข้อมูลทั่วไป (General Info)", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            hn = st.text_input("เลขประจำตัวผู้ป่วย (HN)")
            fname = st.text_input("ชื่อ-นามสกุล")
            # แก้: เลือกปีเกิด แล้วคำนวณอายุ
            birth_year = st.selectbox("ปีเกิด (พ.ศ.)", YEARS_LIST, index=40) # Default แถวๆ อายุ 40
            calc_age = current_year_be - birth_year
            st.info(f"อายุ: {calc_age} ปี")
            
        with c2:
            gender = st.selectbox("เพศ", ["ชาย", "หญิง"])
            weight = st.number_input("น้ำหนัก (กก.)", 0.0, 200.0, 60.0)
            height = st.number_input("ส่วนสูง (ซม.)", 0, 250, 170)
        
        with c3:
            # แก้: Country & Province Dropdown
            nationality = st.text_input("สัญชาติ", value="ไทย")
            country = st.selectbox("ประเทศที่อยู่อาศัย", COUNTRIES)
            if country == "Other":
                st.text_input("ระบุประเทศ", key="country_other")
                
            province = st.selectbox("จังหวัดที่อยู่อาศัย", THAI_PROVINCES)

        st.markdown("---")
        # ข้อมูลการตัดขา
        c4, c5 = st.columns(2)
        with c4:
            comorbidities = st.multiselect("โรคประจำตัว", ["เบาหวาน", "ความดัน", "โรคหัวใจ", "โรคไต", "ไม่มี", "Other"])
            if "Other" in comorbidities:
                st.text_input("ระบุโรคประจำตัวอื่นๆ")

            cause = st.selectbox("สาเหตุการตัดขา", ["อุบัติเหตุ", "เบาหวาน", "โรคหลอดเลือด", "มะเร็ง", "ติดเชื้อ", "Other"])
            if cause == "Other":
                st.text_input("ระบุสาเหตุอื่นๆ")

            amp_year = st.number_input("ปี (พ.ศ.) ที่ตัดขา", 2490, 2600, 2566)
        
        with c5:
            side = st.radio("ข้างที่ตัด", ["ซ้าย", "ขวา", "สองข้าง"], horizontal=True)
            amp_level = st.selectbox("ระดับการตัดขา", ["Ankle disarticulation", "Transtibial", "Knee disarticulation", "Transfemoral", "Other"])
            if amp_level == "Other":
                st.text_input("ระบุระดับการตัดขา")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                stump_len = st.selectbox("ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"])
            with col_s2:
                stump_shape = st.selectbox("รูปทรงตอขา", ["Conical", "Cylindrical", "Bulbous", "Other"])
                if stump_shape == "Other":
                    st.text_input("ระบุรูปทรงอื่นๆ")

    # --- Module 3: ข้อมูลกายอุปกรณ์ ---
    with st.expander("🦾 3. ข้อมูลกายอุปกรณ์ (Prosthesis Info)"):
        # Logic เลือก Socket ตามระดับการตัดขา
        socket_opts = ["Other"]
        if amp_level == "Transtibial":
            socket_opts = ["PTB", "TSB", "Osseointegration", "Other"]
        elif amp_level == "Transfemoral":
            socket_opts = ["Quadrilateral", "Ischial Containment", "Sub Ischial", "Osseointegration", "Other"]
        # (เพิ่ม Case อื่นๆ ได้ตามต้องการ)

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            socket = st.selectbox("ชนิดเบ้า (Socket)", socket_opts)
            if socket == "Other":
                st.text_input("ระบุชนิดเบ้า")
            
            liner = st.multiselect("Liner", ["No liner", "Foam", "Silicone", "Gel", "Other"])
            if "Other" in liner:
                st.text_input("ระบุ Liner อื่นๆ")

        with col_p2:
            suspension = st.multiselect("ระบบยึด (Suspension)", ["Suction", "Pin lock", "Lanyard", "Sleeve", "Belt", "Other"])
            if "Other" in suspension:
                st.text_input("ระบุระบบยึดอื่นๆ")
                
            foot = st.multiselect("เท้าเทียม (Foot)", ["SACH", "Single axis", "Dynamic", "Microprocessor", "Other"])
            if "Other" in foot:
                st.text_input("ระบุชนิดเท้าเทียมอื่นๆ")

    if st.button("💾 บันทึกข้อมูล (SAVE)", type="primary"):
        st.success("บันทึกข้อมูลเรียบร้อย")

# =========================================================
# 📌 TAB 2: TUG Test (แก้ระบบจับเวลา: Freeze Time)
# =========================================================
with tab2:
    st.header("⏱️ Timed Up and Go (TUG)")
    
    # Session State
    if 'trials' not in st.session_state:
        st.session_state.trials = [0.0, 0.0, 0.0]
    if 'current_trial_idx' not in st.session_state:
        st.session_state.current_trial_idx = 0
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = None
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'temp_time' not in st.session_state:
        st.session_state.temp_time = 0.0  # ตัวแปรเก็บเวลาที่ Freeze ไว้

    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.markdown(f"### 🏁 ทดสอบครั้งที่ {st.session_state.current_trial_idx + 1} / 3")
        
        # กล่องนาฬิกา
        with st.container(border=True):
            @st.fragment(run_every=0.1)
            def live_clock():
                if st.session_state.timer_running:
                    # กำลังจับเวลา: วิ่งตลอด
                    elapsed = time.time() - st.session_state.timer_start
                    st.metric("Time", f"{elapsed:.2f} s")
                elif st.session_state.temp_time > 0:
                    # กดหยุดแล้ว: โชว์เวลาค้างไว้ (Freeze)
                    st.metric("Time", f"{st.session_state.temp_time:.2f} s")
                else:
                    # ยังไม่เริ่ม: โชว์ 0.00
                    st.metric("Time", "0.00 s")
            live_clock()

        # ปุ่มควบคุม (Logic ใหม่)
        b1, b2, b3 = st.columns(3)
        
        with b1:
            # ปุ่ม START
            if st.button("▶️ START", type="primary", use_container_width=True, 
                         disabled=st.session_state.timer_running or st.session_state.temp_time > 0):
                st.session_state.timer_running = True
                st.session_state.timer_start = time.time()
                st.rerun()

        with b2:
            # ปุ่ม STOP (กดแล้วเวลาหยุดเดิน แต่ยังไม่บันทึก)
            if st.button("⏸️ STOP", type="secondary", use_container_width=True, 
                         disabled=not st.session_state.timer_running):
                st.session_state.timer_running = False
                st.session_state.temp_time = time.time() - st.session_state.timer_start
                st.rerun()

        with b3:
            # ปุ่ม SAVE & NEXT (ยืนยันเวลา แล้วไปครั้งถัดไป)
            if st.button("✅ SAVE & NEXT", use_container_width=True, 
                         disabled=st.session_state.temp_time == 0 or st.session_state.current_trial_idx >= 3):
                # บันทึกลง List
                if st.session_state.current_trial_idx < 3:
                    st.session_state.trials[st.session_state.current_trial_idx] = st.session_state.temp_time
                    st.session_state.current_trial_idx += 1
                # รีเซ็ตตัวแปรชั่วคราว
                st.session_state.temp_time = 0.0
                st.session_state.timer_running = False
                st.rerun()
        
        # ปุ่ม Reset กรณีจับพลาด อยากเริ่มใหม่
        if st.button("❌ ไม่เอา กดผิด (RESET)", disabled=st.session_state.temp_time == 0):
            st.session_state.temp_time = 0.0
            st.session_state.timer_running = False
            st.rerun()

        if st.button("🔄 ล้างข้อมูลทั้งหมด (Clear All)"):
            st.session_state.trials = [0.0, 0.0, 0.0]
            st.session_state.current_trial_idx = 0
            st.session_state.temp_time = 0.0
            st.rerun()

    with col_right:
        st.markdown("### 📝 ผลการทดสอบ")
        # Input Manual (เผื่อแก้เอง)
        t1 = st.number_input("Trial 1", value=st.session_state.trials[0], key="t1")
        t2 = st.number_input("Trial 2", value=st.session_state.trials[1], key="t2")
        t3 = st.number_input("Trial 3", value=st.session_state.trials[2], key="t3")
        
        st.session_state.trials = [t1, t2, t3]

        # คำนวณค่าเฉลี่ย
        valid_trials = [t for t in st.session_state.trials if t > 0]
        avg_time = sum(valid_trials) / len(valid_trials) if valid_trials else 0.0
        
        st.markdown(f"""
        <div class="result-box">
            <h4>📊 Average Time</h4>
            <h1 style="color:#2E86C1;">{avg_time:.2f} s</h1>
        </div>
        """, unsafe_allow_html=True)

    # แปลผล
    st.divider()
    if avg_time > 0:
        if avg_time >= 13.5:
            st.error(f"⚠️ **High Fall Risk** (เสี่ยงล้มสูง)\n\nค่าเฉลี่ย {avg_time:.2f} วินาที (> 13.5 วินาที)")
        else:
            st.success(f"✅ **Normal Mobility** (ปกติ)\n\nค่าเฉลี่ย {avg_time:.2f} วินาที (< 13.5 วินาที)")