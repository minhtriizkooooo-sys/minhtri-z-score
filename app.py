import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import io
import base64
import os

# ==========================
# Cấu hình trang
# ==========================
st.set_page_config(page_title="Phân Tích Điểm Bất Thường", layout="wide", page_icon="📊")

# Intro video fullscreen (using external URL to avoid Render timeout)
video_url = "https://raw.githubusercontent.com/minhtriizkooooo-sys/minhtri-z-score/main/test.mp4"  # Replace with your actual GitHub raw URL
try:
    st.markdown(f"""
    <div id="video-container" style="position:fixed; top:0; left:0; width:100vw; height:100vh; background-color:black; z-index:9999; display:flex; align-items:center; justify-content:center;">
        <video id="intro-video" autoplay playsinline muted style="max-width:100%; max-height:100%;">
            <source src="{video_url}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>
    <script>
        var video = document.getElementById('intro-video');
        var container = document.getElementById('video-container');
        
        video.onended = function() {{
            container.style.display = 'none';
        }};
        
        setTimeout(function() {{
            if (container.style.display !== 'none') {{
                container.style.display = 'none';
            }}
        }}, 5000);
        
        video.onerror = function() {{
            container.style.display = 'none';
        }};
        
        video.play().catch(function(e) {{
            console.log('Autoplay prevented:', e);
            container.style.display = 'none';
        }});
    </script>
    """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Video load error: {e}. Skipping intro.")

# Theme selection
theme = st.selectbox("Chọn theme", ["Original", "Castorice", "TealCoral", "VibrantOrange"])

if theme == "Original":
    css = """
    <style>
        .main { background-color: #f0f2f6; }
        .stButton>button { background-color: #4CAF50; color: white; border-radius: 5px; }
        .stFileUploader>label { font-weight: bold; }
        .css-1d391kg { background-color: #ffffff; border-radius: 10px; padding: 20px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; }
        .stAlert { border-radius: 5px; }
        footer { visibility: hidden; }
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #2c3e50;
            color: white;
            text-align: center;
            padding: 10px;
        }
    </style>
    """
    primary_color = "#4CAF50"
    anomaly_color = "#FF5252"
    hist_normal = "#4CAF50"
    hist_anom = "#FF0000"
elif theme == "Castorice":
    css = """
    <style>
        .main { background-color: #e6e6fa; }  /* Lavender */
        .stButton>button { background-color: #c8a2c8; color: white; border-radius: 5px; }  /* Lilac */
        .stFileUploader>label { font-weight: bold; }
        .css-1d391kg { background-color: #f3e5f5; border-radius: 10px; padding: 20px; }  /* Light purple */
        h1 { color: #4b0082; }  /* Indigo */
        h2 { color: #6a1b9a; }  /* Purple */
        .stAlert { border-radius: 5px; }
        footer { visibility: hidden; }
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #4b0082;  /* Indigo */
            color: white;
            text-align: center;
            padding: 10px;
        }
    </style>
    """
    primary_color = "#c8a2c8"  # Lilac
    anomaly_color = "#9370db"  # Medium purple
    hist_normal = "#dda0dd"  # Plum
    hist_anom = "#4b0082"  # Indigo
elif theme == "TealCoral":
    css = """
    <style>
        .main { background-color: #e0f7fa; }  /* Light teal background */
        .stButton>button { background-color: #008080; color: white; border-radius: 5px; }  /* Teal buttons */
        .stFileUploader>label { font-weight: bold; color: #ff6f61; }  /* Coral label */
        .css-1d391kg { background-color: #ffffff; border-radius: 10px; padding: 20px; border: 1px solid #008080; }  /* White card with teal border */
        h1 { color: #00695c; }  /* Dark teal headers */
        h2 { color: #ff6f61; }  /* Coral subheaders */
        .stAlert { border-radius: 5px; border: 1px solid #ff6f61; }  /* Coral alert border */
        footer { visibility: hidden; }
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #00695c;  /* Dark teal footer */
            color: white;
            text-align: center;
            padding: 10px;
        }
    </style>
    """
    primary_color = "#008080"  # Teal
    anomaly_color = "#ff6f61"  # Coral
    hist_normal = "#26a69a"  # Lighter teal
    hist_anom = "#d81b60"  # Darker coral
else:  # VibrantOrange theme
    css = """
    <style>
        .main { background-color: #fff3e0; }  /* Light orange background */
        .stButton>button { background-color: #f57c00; color: white; border-radius: 5px; }  /* Orange buttons */
        .stFileUploader>label { font-weight: bold; color: #0277bd; }  /* Blue label */
        .css-1d391kg { background-color: #ffffff; border-radius: 10px; padding: 20px; border: 1px solid #f57c00; }  /* White card with orange border */
        h1 { color: #ef6c00; }  /* Dark orange headers */
        h2 { color: #0288d1; }  /* Light blue subheaders */
        .stAlert { border-radius: 5px; border: 1px solid #0288d1; }  /* Blue alert border */
        footer { visibility: hidden; }
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #ef6c00;  /* Dark orange footer */
            color: white;
            text-align: center;
            padding: 10px;
        }
    </style>
    """
    primary_color = "#ff9800"  # Orange
    anomaly_color = "#2196f3"  # Blue
    hist_normal = "#ffb74d"  # Light orange
    hist_anom = "#1565c0"  # Dark blue

st.markdown(css, unsafe_allow_html=True)

# ==========================
# Header logo
# ==========================
col_logo, col_title = st.columns([1,6])
with col_logo:
    try:
        st.image("Logo_Marie_Curie.png", width=100)
    except:
        st.write("🏫 THPT Marie Curie")
with col_title:
    st.title("📊 Phân Tích Điểm Số Bất Thường Sử Dụng Z-Score")

st.markdown("""
Ứng dụng phân tích điểm số bất thường dựa trên Z-score.  
- File CSV cần có header: "MaHS", "Lop", các cột môn học.  
- Z-score: Điểm bất thường nếu |z-score| > ngưỡng (mặc định 2).  
- Hỗ trợ UTF-8.
""")

# ==========================
# Sidebar
# ==========================
with st.sidebar:
    st.header("🛠 Cài đặt")
    z_threshold = st.slider("Ngưỡng Z-Score", 1.0, 5.0, 2.0, 0.1)
    st.markdown("---")
    st.info("CSV phải có cột số cho điểm và mã hóa UTF-8.")

# ==========================
# Upload file
# ==========================
uploaded_file = st.file_uploader("📂 Upload bảng điểm (CSV)", type="csv")
if uploaded_file is not None:
    # Đọc file CSV
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='latin1')
        st.warning("File không phải UTF-8, đã dùng latin1.")

    # Chuẩn hóa tên cột
    df.columns = df.columns.str.strip().str.replace(' ','').str.capitalize()

    # Kiểm tra cột lớp
    class_col = [c for c in df.columns if c.lower()=='lop']
    if not class_col:
        st.error("Không tìm thấy cột 'Lop'.")
        st.stop()
    df['Lop'] = df[class_col[0]]

    # Kiểm tra cột học sinh
    student_col = [c for c in df.columns if c.lower() in ['mahs','id','studentid']]
    if not student_col:
        st.error("Không tìm thấy cột 'MaHS'.")
        st.stop()
    df['MaHS'] = df[student
