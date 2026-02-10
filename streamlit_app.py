import streamlit as st
import time

# --- 1. ตั้งค่าหน้าเว็บ & Design System ---
st.set_page_config(page_title="Prosthesis Clinic Modern", page_icon="🦿", layout="wide")

# Custom CSS เพื่อความ Modern และตัวเลขใหญ่สะใจ
st.markdown("""
    <style>
    /* ปรับแต่ง Font ของนาฬิกาให้ดูเป็น Digital */
    div[data-testid="stMetricValue"] {
        font-size: 80px !important;
        font-family: 'Courier New', monospace;
        font-weight: 700;
        color: #2E86C1; /* สีฟ้าน้ำเงินทันสมัย */
        text-shadow: 2px 2px 4px #00000020;
    }
    /* ปรับแต่ง Label (คำว่า เวลาที่ทำได้) */
    div[data-testid="stMetricLabel"] {
        font-size: 20px !important;
        color: #555;
    }
    /* กรอบ Container ให้ดูมีมิติ */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FAFAFA;
        border-radius: 15px;
        padding: 20px;
    }
    /* ปุ่มกดขนาดใหญ่ */
    button {
        height: 3em !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🦿 Prosthesis Clinic Registry")

# --- 2. ตัวแปรระบบ (Session State) ---
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0.0

# --- 3. สร้าง Tabs แบ่งหมวดหมู่ ---
tab1, tab2 = st.tabs(["📋 Patient Registry", "⏱️ TUG Test (Real-time)"])

# ==========================================
# 📌 TAB 1: Patient Registry (ทะเบียนคนไข้)
# ==========================================
with tab1:
    st.subheader("บันทึกข้อมูลทั่วไป (General Information)")
    with st.container(border=True):
        col_a, col_b = st.columns(2)
        with col_a:
            hn = st.text_input("HN / ID Number", placeholder="Ex. 123456")
            name = st.text_input("ชื่อ-นามสกุล (Name)", placeholder="Ex. สมชาย ใจดี")
            age = st.number_input("อายุ (Age)", 1, 120, 60)
        
        with col_b:
            gender = st.selectbox("เพศ (Sex)", ["Male", "Female"])
            amp_level = st.selectbox("ระดับการตัดขา (Level)", 
                                     ["Transtibial (BK)", "Transfemoral (AK)", "Knee Disarticulation", "Symes"])
            side = st.radio("ข้าง (Side)", ["Left", "Right", "Bilateral"], horizontal=True)

    if st.button("💾 บันทึกประวัติ (Save Profile)", type="primary", use_container_width=True):
        st.toast(f"บันทึกข้อมูลคุณ {name} เรียบร้อย!", icon='✅')

# ==========================================
# 📌 TAB 2: OM TUG Test (จับเวลา Real-time)
# ==========================================
with tab2:
    col_img, col_timer = st.columns([1, 2])
    
    with col_img:
        st.info("💡 **วิธีทดสอบ:**\n1. ลุกจากเก้าอี้\n2. เดิน 3 เมตร\n3. เลี้ยวกลับมานั่ง")
        # ใส่รูปตรงนี้ได้เหมือนเดิม
        # st.image("tug_guide.jpg", use_column_width=True)

    with col_timer:
        st.markdown("### ⏱️ Timed Up and Go (TUG)")
        
        # --- กรอบนาฬิกา Modern ---
        with st.container(border=True):
            # ฟังก์ชันพิเศษ @st.fragment ช่วยให้เฉพาะส่วนนี้รีเฟรชตัวเองได้ (Real-time update)
            # run_every=0.1 คือสั่งให้รันใหม่ทุก 0.1 วินาที
            @st.fragment(run_every=0.1)
            def live_clock():
                if st.session_state.is_running:
                    # คำนวณเวลาสดๆ
                    current = time.time() - st.session_state.start_time
                    st.metric(label="เวลาที่ทำได้ (วินาที)", value=f"{current:.2f}")
                else:
                    # โชว์เวลาล่าสุดที่หยุดไว้
                    st.metric(label="เวลาที่ทำได้ (วินาที)", value=f"{st.session_state.elapsed_time:.2f}")

            # เรียกใช้งานนาฬิกา
            live_clock()

        # --- ปุ่มควบคุม (Control Buttons) ---
        c1, c2, c3 = st.columns(3)
        
        with c1:
            if st.button("▶️ START", type="primary", use_container_width=True, disabled=st.session_state.is_running):
                st.session_state.is_running = True
                st.session_state.start_time = time.time()
                st.rerun()

        with c2:
            if st.button("⏹️ STOP", type="secondary", use_container_width=True, disabled=not st.session_state.is_running):
                st.session_state.is_running = False
                # คำนวณเวลาจบจริง
                st.session_state.elapsed_time = time.time() - st.session_state.start_time
                st.rerun()

        with c3:
            if st.button("🔄 RESET", use_container_width=True):
                st.session_state.is_running = False
                st.session_state.elapsed_time = 0.0
                st.session_state.start_time = None
                st.rerun()

    # --- ส่วนแปลผล (Auto Interpretation) ---
    st.divider()
    final_time = st.session_state.elapsed_time
    
    if final_time > 0 and not st.session_state.is_running:
        if final_time >= 13.5:
            st.error(f"⚠️ **High Fall Risk (เสี่ยงล้มสูง)** — เวลา {final_time:.2f} วินาที (เกณฑ์ > 13.5 วิ)")
        else:
            st.success(f"✅ **Normal Mobility (ปกติ)** — เวลา {final_time:.2f} วินาที (เคลื่อนไหวได้ดี)")