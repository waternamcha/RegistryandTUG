import streamlit as st
import time
from datetime import date

# --- 1. ตั้งค่าหน้าเว็บ & Design System ---
st.set_page_config(page_title="Prosthesis Clinic Registry", page_icon="🦿", layout="wide")

st.markdown("""
    <style>
    /* ปรับแต่ง Font นาฬิกา */
    div[data-testid="stMetricValue"] {
        font-size: 80px !important;
        font-family: 'Courier New', monospace;
        font-weight: 700;
        color: #2E86C1;
        text-shadow: 2px 2px 4px #00000020;
    }
    /* ปรับหัวข้อ Expanders ให้เด่นขึ้น */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #1F618D;
        background-color: #F0F3F4;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🦿 Prosthesis Clinic Registry & OM")

# --- 2. ตัวแปรระบบ (Session State) ---
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0.0

# --- 3. สร้าง Tabs ---
tab1, tab2 = st.tabs(["📋 Patient Registry (ทะเบียนประวัติเต็มรูปแบบ)", "⏱️ TUG Test (ทดสอบเดิน)"])

# =========================================================
# 📌 TAB 1: Patient Registry (Based on LEAD_kobotoolbox_2)
# =========================================================
with tab1:
    st.header("แบบบันทึกข้อมูลผู้ใช้กายอุปกรณ์")
    
    # --- หมวดที่ 1: ข้อมูลทั่วไป (Demographics) ---
    with st.expander("👤 1. ข้อมูลส่วนตัว (Demographics)", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            hn = st.text_input("เลขประจำตัวผู้ป่วย (HN)", placeholder="Ex. 66-00123")
            prefix = st.selectbox("คำนำหน้า", ["นาย", "นาง", "นางสาว", "ด.ช.", "ด.ญ."])
            fname = st.text_input("ชื่อ-นามสกุล")
        with c2:
            gender = st.selectbox("เพศ", ["ชาย", "หญิง"])
            dob = st.date_input("วัน/เดือน/ปีเกิด", min_value=date(1920, 1, 1))
            age = st.number_input("อายุ (ปี)", 0, 120, 60)
        with c3:
            weight = st.number_input("น้ำหนัก (กก.)", 0.0, 200.0, 60.0)
            height = st.number_input("ส่วนสูง (ซม.)", 0, 250, 170)
            nationality = st.selectbox("สัญชาติ", ["ไทย", "อื่นๆ"])
        
        c4, c5 = st.columns(2)
        with c4:
            country = st.text_input("ประเทศที่อยู่อาศัย", value="Thailand")
        with c5:
            province = st.text_input("จังหวัด")

    # --- หมวดที่ 2: ประวัติการเจ็บป่วยและการตัดขา (Amputation History) ---
    with st.expander("🏥 2. ข้อมูลการตัดขาและสุขภาพ (Amputation Info)"):
        comorbidities = st.multiselect("โรคประจำตัว", 
            ["เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "โรคไต", "ไม่มี", "อื่นๆ"])
        
        col_amp1, col_amp2 = st.columns(2)
        with col_amp1:
            cause = st.selectbox("สาเหตุการตัดขา", 
                ["อุบัติเหตุ", "โรคเบาหวาน", "โรคหลอดเลือด", "มะเร็ง", "การติดเชื้อ", "พิการแต่กำเนิด", "อื่นๆ"])
            amp_year = st.number_input("ปี ค.ศ. ที่ตัดขา", 1950, 2030, 2023)
            amp_side = st.selectbox("ข้างที่ตัด", ["ซ้าย", "ขวา", "ทั้งสองข้าง"])
        
        with col_amp2:
            amp_level = st.selectbox("ระดับการตัดขา", 
                ["Transtibial (ใต้เข่า)", "Transfemoral (เหนือเข่า)", "Knee Disarticulation", "Symes", "Hip Disarticulation"])
            stump_len = st.selectbox("ความยาวตอขา", ["สั้น (Short)", "ปานกลาง (Medium)", "ยาว (Long)"])
            stump_shape = st.selectbox("รูปทรงตอขา", ["Conical", "Cylindrical", "Bulbous"])

        surgery_add = st.radio("เคยผ่าตัดแก้ไขตอขาเพิ่มเติมหรือไม่?", ["ไม่เคย", "เคย"])
        if surgery_add == "เคย":
            st.multiselect("ระบุการผ่าตัดเพิ่มเติม", ["ตัดแต่งกระดูก", "ตัดแต่งผิวหนัง", "ตัดระดับสูงขึ้น"])

    # --- หมวดที่ 3: ประวัติการฟื้นฟู (Rehabilitation) ---
    with st.expander("wwer 3. ข้อมูลการฟื้นฟู (Rehabilitation)"):
        col_rehab1, col_rehab2 = st.columns(2)
        with col_rehab1:
            k_level = st.selectbox("K-Level (ระดับกิจกรรม)", ["K1", "K2", "K3", "K4"])
            rehab_person = st.multiselect("บุคลากรที่เคยดูแลท่าน", 
                ["นักกายอุปกรณ์", "นักกายภาพบำบัด", "แพทย์เวชศาสตร์ฟื้นฟู", "พยาบาล", "นักจิตวิทยา", "ครอบครัว"])
        
        with col_rehab2:
            rehab_history = st.radio("เคยเข้ารับการฟื้นฟูหรือไม่?", ["เคย", "ไม่เคย"])
            if rehab_history == "เคย":
                st.multiselect("กิจกรรมที่เคยทำ", 
                    ["สวมถุงลดบวม (Shrinker)", "พันผ้ายืด", "ใส่เบ้าซิลิโคน", "ฝึกเดิน", "ออกกำลังกาย"])

    # --- หมวดที่ 4: ส่วนประกอบกายอุปกรณ์ (Prosthesis Components) ---
    with st.expander("🦾 4. ข้อมูลกายอุปกรณ์ (Prosthesis Components)"):
        service_type = st.multiselect("การรับบริการครั้งนี้", 
            ["ทำใหม่", "เปลี่ยนเบ้า", "ซ่อมแซม", "เปลี่ยนเท้า", "เปลี่ยน Liner", "เปลี่ยนระบบยึด"])
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            date_cast = st.date_input("วันที่หล่อแบบ (Casting Date)")
            socket_type = st.selectbox("ชนิดเบ้าขาเทียม (Socket)", 
                ["PTB", "TSB", "Quadrilateral", "Ischial Containment", "Sub-Ischial", "Osseointegration"])
            liner_type = st.selectbox("ชนิด Liner", 
                ["No liner", "Foam/Pelite", "Silicone", "Polyurethane", "Gel (TPE)"])
        
        with c_p2:
            date_deliver = st.date_input("วันที่ได้รับขา (Delivery Date)")
            suspension = st.selectbox("ระบบยึดตรึง (Suspension)", 
                ["Suction (Valve)", "Pin lock", "Lanyard", "Sleeve", "Cuff/Strap", "Vacuum", "Belt"])
            foot_type = st.selectbox("ชนิดเท้าเทียม (Foot)", 
                ["SACH", "Single Axis", "Multiaxial", "Dynamic Response", "Hydraulic", "Microprocessor"])
        
        if "Transfemoral" in amp_level or "Knee" in amp_level:
            knee_type = st.selectbox("ชนิดข้อเข่าเทียม (Knee)", 
                ["Single axis", "Polycentric", "Lock knee", "Weight-activated brake", "Hydraulic", "Pneumatic", "Microprocessor"])

    # --- หมวดที่ 5: สังคมและการใช้งาน (Social & Function) ---
    with st.expander("🌍 5. ประวัติการล้มและสังคม (Functional & Social)"):
        col_soc1, col_soc2 = st.columns(2)
        with col_soc1:
            assistive = st.selectbox("อุปกรณ์ช่วยเดินที่ใช้", ["ไม่ใช้", "ไม้เท้า (Cane)", "ไม้ค้ำยัน (Crutch)", "Walker", "Wheelchair"])
            hours_stand = st.selectbox("ชั่วโมงการยืนต่อวัน", ["0 ชม.", "< 1 ชม.", "1-3 ชม.", "3-7 ชม.", "> 8 ชม."])
            hours_walk = st.selectbox("ชั่วโมงการเดินต่อวัน", ["0 ชม.", "< 1 ชม.", "1-3 ชม.", "3-7 ชม.", "> 8 ชม."])
        
        with col_soc2:
            history_fall = st.radio("ประวัติการล้มใน 6 เดือน", ["ไม่มี", "มี"])
            if history_fall == "มี":
                fall_freq = st.selectbox("ความถี่การล้ม", ["< 1 ครั้ง", "1-2 ครั้ง", "3-4 ครั้ง", "> 4 ครั้ง"])
                fall_injury = st.checkbox("ได้รับบาดเจ็บจากการล้ม")

        st.markdown("---")
        st.write("**การประเมินตนเอง (Self-Assessment)**")
        work_ability = st.slider("ความสามารถในการทำงานเทียบกับคนปกติ (%)", 0, 100, 80)
        social_part = st.slider("การมีส่วนร่วมในสังคม (%)", 0, 100, 80)

    # ปุ่มบันทึกใหญ่
    st.markdown("---")
    if st.button("💾 บันทึกข้อมูลลงทะเบียน (SAVE TO REGISTRY)", type="primary", use_container_width=True):
        st.balloons()
        st.success(f"บันทึกข้อมูลคุณ {fname} (HN: {hn}) ลงในฐานข้อมูลเรียบร้อยแล้ว!")

# =========================================================
# 📌 TAB 2: OM TUG Test (Modern Clock)
# =========================================================
with tab2:
    col_img, col_timer = st.columns([1, 2])
    
    with col_img:
        st.info("💡 **วิธีทดสอบ TUG:**\n1. ลุกจากเก้าอี้\n2. เดิน 3 เมตร\n3. เลี้ยวกลับมานั่ง")
        # st.image("tug_guide.jpg", use_column_width=True)

    with col_timer:
        st.markdown("### ⏱️ Timed Up and Go (TUG)")
        
        with st.container(border=True):
            @st.fragment(run_every=0.1)
            def live_clock():
                if st.session_state.is_running:
                    current = time.time() - st.session_state.start_time
                    st.metric(label="เวลาที่ทำได้ (วินาที)", value=f"{current:.2f}")
                else:
                    st.metric(label="เวลาที่ทำได้ (วินาที)", value=f"{st.session_state.elapsed_time:.2f}")

            live_clock()

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("▶️ START", type="primary", use_container_width=True, disabled=st.session_state.is_running):
                st.session_state.is_running = True
                st.session_state.start_time = time.time()
                st.rerun()

        with c2:
            if st.button("⏹️ STOP", type="secondary", use_container_width=True, disabled=not st.session_state.is_running):
                st.session_state.is_running = False
                st.session_state.elapsed_time = time.time() - st.session_state.start_time
                st.rerun()

        with c3:
            if st.button("🔄 RESET", use_container_width=True):
                st.session_state.is_running = False
                st.session_state.elapsed_time = 0.0
                st.session_state.start_time = None
                st.rerun()

    # Interpretation
    st.divider()
    final_time = st.session_state.elapsed_time
    if final_time > 0 and not st.session_state.is_running:
        if final_time >= 13.5:
            st.error(f"⚠️ **High Fall Risk** ({final_time:.2f} วินาที) - ควรระวังการหกล้ม")
        else:
            st.success(f"✅ **Normal Mobility** ({final_time:.2f} วินาที) - การเคลื่อนไหวปกติ")