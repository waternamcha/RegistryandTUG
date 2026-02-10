import streamlit as st
import time
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Prosthesis Registry & TUG", page_icon="🦿")

# --- ส่วนหัว (Header) ---
st.title("🦿 Prosthesis Clinic Registry")
st.markdown("### & Timed Up and Go (TUG) Test")
st.divider()

# --- 1. ส่วนทะเบียนคนไข้ (Patient Registry) ---
st.sidebar.header("📋 ข้อมูลคนไข้ (Patient Profile)")
hn = st.sidebar.text_input("HN / ID No.")
name = st.sidebar.text_input("ชื่อ-นามสกุล (Name)")
age = st.sidebar.number_input("อายุ (Age)", min_value=1, max_value=120, value=60)
gender = st.sidebar.selectbox("เพศ (Sex)", ["Male", "Female"])
amp_level = st.sidebar.selectbox("ระดับการตัดขา (Level)", ["Transtibial (BK)", "Transfemoral (AK)", "Knee Disarticulation", "Symes"])
side = st.sidebar.radio("ข้าง (Side)", ["Left", "Right", "Bilateral"])

# --- 2. ส่วนจับเวลา (Stopwatch) ---
st.subheader("⏱️ Timed Up and Go (TUG) Test")

# คำแนะนำ (Instruction)
with st.expander("ℹ️ ดูวิธีการทดสอบ (Instruction)", expanded=True):
    st.write("1. ให้คนไข้นั่งพิงเก้าอี้ให้สบาย")
    st.write("2. เมื่อพร้อม สั่ง 'เริ่ม' ให้คนไข้ลุกเดิน 3 เมตร")
    st.write("3. เลี้ยวกลับมานั่งที่เดิม")
    # ตรงนี้ถ้าคุณมีไฟล์รูป แนะนำให้เอาไฟล์ไปวางใน GitHub แล้วใส่โค้ด st.image("ชื่อรูป.jpg")

# ตัวแปรจับเวลา (Session State)
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0

# ปุ่มควบคุม
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟢 เริ่มจับเวลา (START)", use_container_width=True):
        st.session_state.start_time = time.time()
        st.toast('เริ่มจับเวลาแล้ว! Go!', icon='🏃')

with col2:
    if st.button("🛑 หยุด (STOP)", type="primary", use_container_width=True):
        if st.session_state.start_time:
            st.session_state.elapsed_time = time.time() - st.session_state.start_time
            st.session_state.start_time = None # Reset
        else:
            st.warning("กรุณากดเริ่มก่อน")

with col3:
    if st.button("🔄 รีเซ็ต (RESET)", use_container_width=True):
        st.session_state.elapsed_time = 0
        st.session_state.start_time = None

# แสดงเวลาตัวใหญ่ๆ
st.metric(label="เวลาที่ทำได้ (วินาที)", value=f"{st.session_state.elapsed_time:.2f} s")

# --- 3. การแปลผล (Interpretation) ---
if st.session_state.elapsed_time > 0:
    st.markdown("### 📝 ผลการประเมิน (Result)")
    
    # Logic การแปลผล (Cut-off point ที่ 13.5 วินาที)
    if st.session_state.elapsed_time >= 13.5:
        st.error(f"⚠️ **High Fall Risk (เสี่ยงล้มสูง)**\n\nเวลา {st.session_state.elapsed_time:.2f} วินาที เกินเกณฑ์มาตรฐาน (13.5 วินาที)")
    else:
        st.success(f"✅ **Normal Mobility (ปกติ)**\n\nเวลา {st.session_state.elapsed_time:.2f} วินาที อยู่ในเกณฑ์ดี")

    # ปุ่มบันทึกข้อมูล (Mock Save)
    if st.button("💾 บันทึกผลลงทะเบียน (Save Record)"):
        # ในอนาคตเราจะเขียนโค้ดตรงนี้ให้ส่งไป Google Sheets
        st.balloons()
        st.info(f"บันทึกข้อมูลคุณ {name} (HN: {hn}) เรียบร้อยแล้ว!")