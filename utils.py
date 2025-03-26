import streamlit as st
from datetime import datetime
import base64
from PIL import Image
import io

def format_date(date_str):
    """
    날짜 문자열을 '2023년 5월 15일' 형식으로 변환합니다.
    
    Args:
        date_str (str): 'YYYY-MM-DD' 형식의 날짜 문자열
        
    Returns:
        str: 변환된 날짜 문자열
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%Y년 %m월 %d일')
    except:
        return date_str

def get_image_base64(img):
    """
    PIL Image 객체를 base64로 인코딩합니다.
    
    Args:
        img (PIL.Image): 인코딩할 이미지
        
    Returns:
        str: base64로 인코딩된 이미지 문자열
    """
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def display_memory_card(date, title, content, summary, emotion, empathy, image=None):
    """
    추억 카드를 Streamlit에 표시합니다.
    
    Args:
        date (str): 날짜
        title (str): 제목
        content (str): 내용
        summary (str): 요약
        emotion (str): 감정 분석
        empathy (str): 공감 멘트
        image (PIL.Image, optional): 이미지
    """
    with st.container():
        # 카드 스타일 시작
        st.markdown("""
        <style>
        .memory-card {
            background-color: #f0f8ff;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .memory-title {
            color: #1E88E5;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .memory-date {
            color: #757575;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .memory-content {
            margin-bottom: 15px;
            padding: 10px;
            background-color: white;
            border-radius: 5px;
        }
        .memory-analysis {
            background-color: #E3F2FD;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .analysis-title {
            font-weight: bold;
            color: #1565C0;
        }
        .analysis-content {
            margin-top: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 카드 내용
        st.markdown(f"""
        <div class="memory-card">
            <div class="memory-title">{title}</div>
            <div class="memory-date">{format_date(date)}</div>
            <div class="memory-content">{content.replace('\n', '<br>')}</div>
            
            <div class="memory-analysis">
                <div class="analysis-title">🌟 요약</div>
                <div class="analysis-content">{summary}</div>
            </div>
            
            <div class="memory-analysis">
                <div class="analysis-title">💭 감정 분석</div>
                <div class="analysis-content">{emotion}</div>
            </div>
            
            <div class="memory-analysis">
                <div class="analysis-title">💌 공감 멘트</div>
                <div class="analysis-content">{empathy}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 이미지가 있으면 표시
        if image is not None:
            st.image(image, use_column_width=True)

def add_bg_from_url(url):
    """
    URL에서 배경 이미지를 가져와 전체 페이지에 적용합니다.
    
    Args:
        url (str): 배경 이미지 URL
    """
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url({url});
            background-size: cover;
        }}
        .block-container {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def create_footer():
    """
    페이지 하단에 푸터를 추가합니다.
    """
    st.markdown("""
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f5f5f5;
        text-align: center;
        padding: 10px;
        font-size: 12px;
        color: #757575;
    }
    </style>
    <div class="footer">
        우리의 이야기 © 2023 - 소중한 추억을 AI와 함께 기록하세요.
    </div>
    """, unsafe_allow_html=True)

def page_config():
    """
    Streamlit 페이지 설정을 구성합니다.
    """
    st.set_page_config(
        page_title="우리의 이야기",
        page_icon="💕",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 기본 스타일
    st.markdown("""
    <style>
    h1, h2, h3 {
        color: #1E88E5;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        border-radius: 20px;
    }
    .stButton button:hover {
        background-color: #1565C0;
    }
    .stTextInput, .stTextArea {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    """
    앱 상단 헤더를 표시합니다.
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>💕 우리의 이야기 💕</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>소중한 대화와 추억을 AI와 함께 기록하세요</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True) 