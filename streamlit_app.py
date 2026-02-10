import streamlit as st
import time
from datetime import date

# --- 1. ตั้งค่าหน้าเว็บ & Custom CSS ---
st.set_page_config(page_title="Prosthesis Registry & OM", page_icon="🦿", layout="wide")

st.markdown("""
    <style>
    /* ปรับแต่ง Font นาฬิกา */
    div[data-testid="stMetricValue"] {
        font-size: 60px !important;
        font-family: 'Courier New', monospace;
        font-weight: 700;
        color: #2E86C1;
    }
    /* ปรับหัวข้อ Expanders */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #154360;
        background-color: #EBF5FB;
        border-radius: 8px;
    }
    /* กล่องผลลัพธ์ */
    .result-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        border-left: 5px solid #2E86C1;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🦿 Digital Prosthesis Registry & OM Platform")

# --- 2. สร้าง Tabs ---
tab1, tab2 = st.tabs(["📋 Patient Registry (แบบสำรวจประวัติ)", "⏱️ TUG Test (MDC & Normative)"])

# =========================================================
# 📌 TAB 1: Patient Registry (Based on Capstone PDF)
# =========================================================
with tab1:
    st.markdown("### แบบสำรวจประวัติของผู้ใช้ขาเทียม (Prosthetic User Registry)")
    
    # --- Module 1: ข้อมูลทั่วไป (General Information) ---
    with st.expander("👤 1. ข้อมูลทั่วไปของผู้ใช้กายอุปกรณ์ (General Info)", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            hn = st.text_input("6. เลขประจำตัวผู้ป่วย (HN)")
            fname = st.text_input("ชื่อ-นามสกุล")
            dob = st.date_input("1. วัน/เดือน/ปีเกิด", min_value=date(1920, 1, 1))
        with col2:
            gender = st.selectbox("2. เพศ", ["ชาย", "หญิง"])
            weight = st.number_input("7. น้ำหนัก (กก.)", 0.0, 200.0, 60.0)
            height = st.number_input("8. ส่วนสูง (ซม.)", 0, 250, 170)
        with col3:
            nationality = st.text_input("5. สัญชาติ", value="ไทย")
            province = st.text_input("4. จังหวัดที่อยู่อาศัย")
            country = st.text_input("3. ประเทศที่อยู่อาศัย", value="Thailand")

        st.markdown("---")
        # ข้อมูลการตัดขา
        col4, col5 = st.columns(2)
        with col4:
            comorbidities = st.multiselect("9. โรคประจำตัว", 
                ["เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "โรคไต", "ไม่มี", "อื่นๆ"])
            cause = st.selectbox("10. สาเหตุการตัดขา", 
                ["อุบัติเหตุ", "โรคเบาหวาน", "โรคหลอดเลือด", "มะเร็ง", "การติดเชื้อ", "พิการแต่กำเนิด", "อื่นๆ"])
            amp_year = st.number_input("11. ปี (พ.ศ.) ที่ตัดขา/สูญเสียอวัยวะ", 2490, 2600, 2566)
        
        with col5:
            side = st.radio("12. ข้างที่ตัด", ["ซ้าย", "ขวา", "ทั้งสองข้าง"], horizontal=True)
            level_options = ["Ankle disarticulation", "Transtibial", "Knee disarticulation", "Transfemoral", "Other"]
            amp_level = st.selectbox("13. ระดับการตัดขา", level_options)
            
            c_stump1, c_stump2 = st.columns(2)
            with c_stump1:
                stump_len = st.selectbox("14. ความยาวตอขา", ["สั้น", "ปานกลาง", "ยาว"])
            with c_stump2:
                stump_shape = st.selectbox("15. รูปทรงตอขา", ["Conical", "Cylindrical", "Bulbous", "Other"])

        surgery = st.radio("16. เคยเข้ารับการผ่าตัดขาเพิ่มเติมหรือไม่?", ["ไม่ใช่", "ใช่"])
        if surgery == "ใช่":
            st.multiselect("16.1 ถ้าใช่ เคยตัดแต่งเพิ่มเติมแบบใด", ["ตัดแต่งกระดูก", "ตัดแต่งผิวหนัง", "ตัดแต่งระดับสูงขึ้น"])
        
        k_level_pre = st.selectbox("17. ความสามารถในการเดินก่อนถูกตัดขา (K-level)", ["K0", "K1", "K2", "K3", "K4"])

    # --- Module 2: ข้อมูลการฟื้นฟู (Rehabilitation) ---
    with st.expander("🏥 2. ข้อมูลการฟื้นฟู (Rehabilitation)"):
        st.multiselect("18. บุคลากรทางการแพทย์ที่ท่านเคยเข้ารับการรักษา", 
                       ["นักกายอุปกรณ์", "นักกายภาพบำบัด", "นักกิจกรรมบำบัด", "นักสังคมสงเคราะห์", "นักจิตวิทยา", 
                        "แพทย์เวชศาสตร์ฟื้นฟู", "พยาบาล", "นักสาธารณสุขชุมชน", "ครอบครัว/คนใกล้ชิด", "อื่นๆ"])
        
        rehab = st.radio("19. เคยเข้ารับการฟื้นฟูสมรรถภาพร่างกายหรือไม่?", ["ไม่เคย", "เคย"])
        if rehab == "เคย":
            st.multiselect("19.1 โปรดเลือกกิจกรรมที่เคยทำ", 
                           ["สวมถุงลดบวม (Shrinker)", "พันผ้ายืด", "เบ้าอ่อนซิลิโคน", "เฝือกแข็งถอดได้", 
                            "ฝึกเดิน", "ออกกำลังกาย/กีฬา", "อื่นๆ"])

    # --- Module 3: ข้อมูลกายอุปกรณ์ (Prosthesis Info) ---
    with st.expander("🦾 3. ข้อมูลกายอุปกรณ์ (Prosthesis Components)"):
        st.multiselect("20. การรับบริการครั้งนี้", 
                       ["ทำใหม่", "เปลี่ยนเบ้า", "ซ่อม/ปรับเปลี่ยน", "เปลี่ยนเท้า", "เปลี่ยนเบ้าอ่อน", 
                        "เปลี่ยนระบบยึด", "เปลี่ยนส่วนประกอบ", "อื่นๆ"])
        
        d1, d2 = st.columns(2)
        with d1:
            date_cast = st.date_input("21. วันที่ปรึกษา/หล่อแบบ")
        with d2:
            date_deliv = st.date_input("22. วันที่ได้รับอุปกรณ์")

        st.markdown("---")
        st.markdown("**23. ส่วนประกอบ (Components)**")
        
        # Logic เลือก Socket ตามระดับการตัดขา (ตาม PDF หน้า 5)
        socket_options = []
        if amp_level == "Ankle disarticulation":
            socket_options = ["Push fit", "Window opening", "Distal end bearing", "Proximal bearing", "Other"]
        elif amp_level == "Transtibial":
            socket_options = ["Patella Tendon Bearing (PTB)", "Total Surface Bearing (TSB)", "Osseointegration", "Other"]
        elif amp_level == "Knee disarticulation":
            socket_options = ["Push fit", "Window opening", "Distal end bearing", "Ischial bearing", "Other"]
        elif amp_level == "Transfemoral":
            socket_options = ["Quadrilateral", "Ischial Containment", "Sub Ischial", "Osseointegration", "Other"]
        else:
            socket_options = ["Other"]

        c_comp1, c_comp2 = st.columns(2)
        with c_comp1:
            st.selectbox("23. ชนิดเบ้าขาเทียม (Socket Type)", socket_options)
            st.multiselect("24. ชนิดเบ้าอ่อน (Liner)", ["No liner", "Foam/Pelite", "Silicone Liner", "Polyurethane Liner", "Gel Liner (TPE)", "Socks", "Other"])
        
        with c_comp2:
            st.multiselect("25. ระบบยึดตอขา (Suspension)", 
                           ["Self-suspension", "Cuff/strap", "Pin lock", "Lanyard", "Sleeve", 
                            "Expulsion valve", "Silesian belt", "TES belt", "Pelvic band", "Other"])
            st.multiselect("26. ประเภทของเท้าเทียม (Foot)", 
                           ["SACH foot", "Single axis", "Multiaxial", "Dynamic response", 
                            "Hydraulic ankle", "Microprocessor foot", "Special activity", "Other"])
        
        # Knee Joint (เฉพาะเคสเหนือเข่า/ข้อเข่า)
        if amp_level in ["Knee disarticulation", "Transfemoral"]:
            st.multiselect("27. ประเภทของข้อเข่าเทียม (Knee)", 
                           ["Single axis", "Polycentric", "Lock knee", "Weight-activated brake", 
                            "Hydraulic", "Pneumatic", "Microprocessor", "Manual lock"])

    # --- Module 4: สังคมและการทำงาน (Social & Function) ---
    with st.expander("🌍 4. ข้อมูลทางสังคมและการทำงาน (Social & Functional)"):
        sc1, sc2 = st.columns(2)
        with sc1:
            st.selectbox("28. อุปกรณ์ช่วยเดิน", ["ไม่ใช้", "Cane (ไม้เท้า)", "Crutch (ไม้ค้ำยัน)", "Walker", "Wheelchair", "Other"])
            st.selectbox("29.1 เวลาที่ใช้ 'ยืน' ต่อวัน", ["ไม่ได้ยืนเลย", "< 1 ชม.", "1-3 ชม.", "3-7 ชม.", "8 ชม.ขึ้นไป"])
            st.selectbox("29.2 เวลาที่ใช้ 'เดิน' ต่อวัน", ["ไม่ได้เดินเลย", "< 1 ชม.", "1-3 ชม.", "3-7 ชม.", "8 ชม.ขึ้นไป"])
        
        with sc2:
            fall_hist = st.radio("30. ประวัติการล้ม (ใน 6 เดือน)", ["ไม่มี", "มี"])
            if fall_hist == "มี":
                st.selectbox("30.1 ความถี่การล้ม", ["< 1 ครั้ง", "1-2 ครั้ง", "3-4 ครั้ง", "> 4 ครั้ง"])
                st.checkbox("30.2 ได้รับบาดเจ็บจากการล้ม")

        st.markdown("---")
        st.markdown("**การประเมินตนเอง (Self-Evaluation)**")
        st.slider("31.1 ปัญหาการมีส่วนร่วมในสังคม (เทียบความคาดหวังตนเอง)", 0, 100, 0, help="0=ไม่มีปัญหา, 100=ปัญหามากที่สุด")
        st.slider("31.2 ปัญหาการมีส่วนร่วมในสังคม (เทียบคนปกติ)", 0, 100, 0)
        st.slider("32.1 ปัญหาในการทำงาน (เทียบความคาดหวังตนเอง)", 0, 100, 0)
        st.slider("32.2 ปัญหาในการทำงาน (เทียบคนปกติ)", 0, 100, 0)
        
        st.markdown("**33. การสนับสนุน (Support)**")
        st.checkbox("33.1 เข้าถึงการดูแลจากครอบครัว/ผู้ดูแล")
        support_org = st.checkbox("33.2 เข้าถึงการสนับสนุนจากหน่วยงาน (สิทธิผู้พิการ/ประกันสังคม)")
        if support_org:
            st.multiselect("ระบุหน่วยงาน", ["ภาครัฐ", "ไม่แสวงหาผลกำไร", "จ่ายเอง", "อื่นๆ"])

    if st.button("💾 บันทึกข้อมูลลงฐานข้อมูล (SAVE)", type="primary", use_container_width=True):
        st.success(f"บันทึกข้อมูลคุณ {fname} (HN: {hn}) เรียบร้อยแล้ว")


# =========================================================
# 📌 TAB 2: OM TUG Test (3 Trials & Average)
# =========================================================
with tab2:
    st.header("⏱️ Timed Up and Go (TUG) Test")
    st.info("💡 **Protocol:** เดิน 3 เมตร (Walk 3 meters) -> Turn -> Walk back -> Sit")

    # --- ส่วนจัดการ Session State สำหรับ 3 Trials ---
    if 'trials' not in st.session_state:
        st.session_state.trials = [0.0, 0.0, 0.0]  # เก็บค่า 3 ครั้ง
    if 'current_trial_idx' not in st.session_state:
        st.session_state.current_trial_idx = 0
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = None
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False

    # --- Layout: ซ้าย(นาฬิกา) | ขวา(ตารางบันทึก) ---
    col_timer, col_record = st.columns([1.5, 1])

    with col_timer:
        st.markdown(f"### 🏁 Testing Trial {st.session_state.current_trial_idx + 1} / 3")
        
        # นาฬิกา Real-time
        with st.container(border=True):
            @st.fragment(run_every=0.1)
            def live_clock():
                if st.session_state.timer_running:
                    elapsed = time.time() - st.session_state.timer_start
                    st.metric("Time", f"{elapsed:.2f} s")
                else:
                    # โชว์ค่าล่าสุดของ Trial ปัจจุบัน หรือ 0.00
                    current_val = st.session_state.trials[st.session_state.current_trial_idx] if st.session_state.current_trial_idx < 3 else 0.0
                    st.metric("Time", f"{current_val:.2f} s")
            live_clock()

        # ปุ่มควบคุม
        b1, b2 = st.columns(2)
        with b1:
            if st.button("▶️ START", type="primary", use_container_width=True, 
                         disabled=st.session_state.timer_running or st.session_state.current_trial_idx >= 3):
                st.session_state.timer_running = True
                st.session_state.timer_start = time.time()
                st.rerun()
        
        with b2:
            if st.button("⏹️ STOP & RECORD", type="secondary", use_container_width=True, 
                         disabled=not st.session_state.timer_running):
                st.session_state.timer_running = False
                final_time = time.time() - st.session_state.timer_start
                # บันทึกค่าลง List
                if st.session_state.current_trial_idx < 3:
                    st.session_state.trials[st.session_state.current_trial_idx] = final_time
                    st.session_state.current_trial_idx += 1 # ขยับไป Trial ถัดไป
                st.rerun()

        if st.button("🔄 Reset All Trials"):
            st.session_state.trials = [0.0, 0.0, 0.0]
            st.session_state.current_trial_idx = 0
            st.session_state.timer_running = False
            st.rerun()

    with col_record:
        st.markdown("### 📝 Record Summary")
        # Input แบบ Manual เผื่ออยากแก้ตัวเลขเอง
        t1 = st.number_input("Trial 1 (sec)", value=st.session_state.trials[0], key="t1")
        t2 = st.number_input("Trial 2 (sec)", value=st.session_state.trials[1], key="t2")
        t3 = st.number_input("Trial 3 (sec)", value=st.session_state.trials[2], key="t3")
        
        # อัปเดตค่ากลับเข้าไปในตัวแปร (กรณีแก้ Manual)
        st.session_state.trials = [t1, t2, t3]

        # คำนวณค่าเฉลี่ย
        valid_trials = [t for t in [t1, t2, t3] if t > 0]
        average_time = sum(valid_trials) / len(valid_trials) if valid_trials else 0.0
        
        st.markdown(f"""
        <div class="result-box">
            <h4>📊 Average Time</h4>
            <h1 style="color:#1F618D;">{average_time:.2f} s</h1>
        </div>
        """, unsafe_allow_html=True)

    # --- Interpretation Section ---
    st.divider()
    if average_time > 0:
        st.subheader("🔎 Interpretation (การแปลผล)")
        
        # Normative Data (Cut-off 13.5s for Fall Risk)
        st.markdown("**1. Normative Data (เกณฑ์มาตรฐานผู้สูงอายุชุมชน):**")
        if average_time >= 13.5:
            st.error(f"⚠️ **High Fall Risk (เสี่ยงล้มสูง)**\n\nค่าเฉลี่ย {average_time:.2f} วินาที มากกว่าเกณฑ์มาตรฐาน (13.5 วินาที)")
        else:
            st.success(f"✅ **Normal Mobility (ปกติ)**\n\nค่าเฉลี่ย {average_time:.2f} วินาที อยู่ในเกณฑ์ดี (< 13.5 วินาที)")

        # MDC Info
        st.info("""
        **ℹ️ Minimal Detectable Change (MDC):** ค่าความเปลี่ยนแปลงที่น้อยที่สุดที่ถือว่ามีความสำคัญทางคลินิก (MDC95) สำหรับ TUG ในผู้ป่วยขาเทียมคือประมาณ **3.6 วินาที** (Resnik & Borgia, 2011). หากท่านทดสอบซ้ำแล้วเวลาลดลงมากกว่า 3.6 วินาที แสดงว่าคนไข้ดีขึ้นจริง
        """)