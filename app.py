import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import io

# ==========================
# Cấu hình trang
# ==========================
st.set_page_config(page_title="Phân Tích Điểm Bất Thường", layout="wide", page_icon="📊")

# Intro video
try:
    with open("test.mp4", "rb") as video_file:
        video_bytes = video_file.read()
    st.video(video_bytes)
except FileNotFoundError:
    st.warning("File test.mp4 not found. Skipping intro video.")

# Theme selection
theme = st.selectbox("Chọn theme", ["Original", "Castorice", "TealCoral"])

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
else:  # TealCoral theme
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
    df['MaHS'] = df[student_col[0]]

    # Chọn các cột môn học
    subject_cols = [c for c in df.columns if c not in ['MaHS','Lop']]
    if len(subject_cols)==0:
        st.error("Không tìm thấy cột điểm môn học.")
        st.stop()

    # Multi chọn lớp + môn
    classes = st.multiselect("Chọn lớp để lọc", sorted(df['Lop'].unique()), default=sorted(df['Lop'].unique()))
    subjects = st.multiselect("Chọn môn để phân tích", subject_cols, default=subject_cols)

    df_filtered = df[df['Lop'].isin(classes)].copy()
    if df_filtered.empty:
        st.warning("Không có dữ liệu cho lớp được chọn.")
        st.stop()

    # Tính Z-score riêng từng môn
    for subj in subjects:
        df_filtered[f'Z_{subj}'] = stats.zscore(df_filtered[subj].fillna(0))
        df_filtered[f'Highlight_{subj}'] = df_filtered[f'Z_{subj}'].abs() > z_threshold

    # ==========================
    # Bảng dữ liệu
    # ==========================
    st.subheader("📋 Bảng điểm gốc và bất thường")
    col1, col2 = st.columns([3,1])

    with col1:
        st.write("**Bảng gốc học sinh**")
        st.dataframe(df_filtered[['MaHS','Lop']+subjects], use_container_width=True)

        # Tạo bảng bất thường
        anomaly_cols = ['MaHS','Lop'] + [subj for subj in subjects]
        anomalies = df_filtered.copy()
        anomalies = anomalies[anomalies[[f'Highlight_{subj}' for subj in subjects]].any(axis=1)]
        st.write("**Học sinh bất thường**")
        st.dataframe(anomalies[anomaly_cols], use_container_width
