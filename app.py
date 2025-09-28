import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import io
import base64

# ==========================
# Cấu hình trang
# ==========================
st.set_page_config(page_title="Phân Tích Điểm Bất Thường", layout="wide", page_icon="📊")

# Intro video fullscreen
try:
    video_file = open("test.mp4", "rb")
    video_bytes = video_file.read()
    video_base64 = base64.b64encode(video_bytes).decode()
    st.markdown(f"""
    <div id="video-container" style="position:fixed; top:0; left:0; width:100vw; height:100vh; background-color:black; z-index:9999; display:flex; align-items:center; justify-content:center;">
        <video id="intro-video" autoplay playsinline style="max-width:100%; max-height:100%;">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
    </div>
    <script>
        var video = document.getElementById('intro-video');
        video.onended = function() {{
            document.getElementById('video-container').style.display = 'none';
        }};
    </script>
    """, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("File test.mp4 not found. Skipping intro video.")

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
        st.dataframe(anomalies[anomaly_cols], use_container_width=True)

        # Download CSV
        csv_buffer = io.StringIO()
        anomalies.to_csv(csv_buffer, index=False, encoding='utf-8')
        st.download_button("📥 Xuất CSV học sinh bất thường", csv_buffer.getvalue(), file_name="Students_Anomalies.csv")

    # ==========================
    # Biểu đồ cột tổng học sinh vs học sinh bất thường theo lớp
    # ==========================
    st.subheader("📊 Biểu đồ cột theo lớp")
    class_summary = df_filtered.groupby('Lop').size().reset_index(name='Tổng học sinh')
    anomaly_count = anomalies.groupby('Lop').size().reset_index(name='Học sinh bất thường')
    summary = pd.merge(class_summary, anomaly_count, on='Lop', how='left').fillna(0)

    fig_col = px.bar(summary, x='Lop', y=['Tổng học sinh','Học sinh bất thường'],
                     barmode='group', color_discrete_map={'Tổng học sinh':primary_color,'Học sinh bất thường':anomaly_color},
                     labels={'value':'Số học sinh','Lop':'Lớp'}, title="Tổng học sinh & Học sinh bất thường theo lớp")
    st.plotly_chart(fig_col, use_container_width=True)

    # ==========================
    # Scatter & Histogram từng môn
    # ==========================
    st.subheader("📈 Scatter & Histogram theo môn")
    for subj in subjects:
        st.markdown(f"### {subj}")

        # Scatter
        fig_scat = px.scatter(df_filtered, x='MaHS', y=subj, color=f'Z_{subj}',
                              color_continuous_scale='RdYlGn_r', 
                              size=df_filtered[f'Z_{subj}'].abs(),
                              size_max=20,
                              hover_data={'MaHS':True, subj:True, f'Z_{subj}':True})
        st.plotly_chart(fig_scat, use_container_width=True)

        # Histogram
        fig_hist = px.histogram(df_filtered, x=subj, nbins=20, color=f'Highlight_{subj}',
                                color_discrete_map={True:hist_anom, False:hist_normal},
                                labels={'count':'Số học sinh'})
        st.plotly_chart(fig_hist, use_container_width=True)

# ==========================
# Footer
# ==========================
st.markdown("""
<div class="footer">
    <p><b>Nhóm Thực Hiện:</b> Lại Nguyễn Minh Trí và những người bạn</p>
    <p>📞 Liên hệ: 0908-083566 | 📧 Email: laingminhtri@gmail.com</p>
    <p>© 2025 Trường THPT Marie Curie - Dự án Phân Tích Điểm Bất Thường</p>
</div>
""", unsafe_allow_html=True)
