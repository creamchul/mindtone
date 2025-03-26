import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 키 확인
api_key = os.getenv("OPENAI_API_KEY")
api_key_is_valid = api_key and api_key != "your_openai_api_key_here"

# 커스텀 모듈 불러오기
import utils
from data_handler import (
    init_data_dir, save_memory, save_today_word, load_today_word,
    load_all_memories, load_recent_memories, load_all_emotions,
    visualize_emotions, load_image, get_data_dir, get_file_paths
)
from gpt_handler import analyze_conversation

# 페이지 기본 설정
utils.page_config()

# 배경 추가 (원하는 이미지 URL로 변경 가능)
utils.add_bg_from_url('https://img.freepik.com/premium-vector/cute-romantic-hand-drawn-doodle-pattern-background_179234-513.jpg')

# 헤더 표시
utils.display_header()

# 데이터 디렉토리 초기화
init_data_dir()

# 세션 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'show_api_settings' not in st.session_state:
    st.session_state.show_api_settings = False
if 'show_debug_info' not in st.session_state:
    st.session_state.show_debug_info = False
if 'memories_updated' not in st.session_state:
    st.session_state.memories_updated = False
if 'emotions_updated' not in st.session_state:
    st.session_state.emotions_updated = False
if 'today_word_updated' not in st.session_state:
    st.session_state.today_word_updated = False

# OpenAI API 키 저장 함수
def save_api_key(api_key):
    try:
        with open('.env', 'w') as f:
            f.write(f'OPENAI_API_KEY={api_key}')
        return True
    except Exception as e:
        st.error(f"API 키 저장 중 오류 발생: {e}")
        return False

# 사이드바 네비게이션
st.sidebar.title("메뉴")

# API 키 설정 기능
if not api_key_is_valid:
    st.sidebar.error("⚠️ OpenAI API 키가 설정되지 않았습니다.")
    
    if st.sidebar.button("API 키 설정"):
        st.session_state.show_api_settings = True
    
    st.sidebar.info("""
    API 키 설정 방법:
    1. OpenAI에서 API 키 발급
    2. 위 버튼을 클릭하여 API 키 입력
    3. 또는 `.env.example` 파일을 `.env`로 복사하고 API 키 입력
    """)
else:
    st.sidebar.success("✅ OpenAI API 키가 설정되었습니다.")
    if st.sidebar.button("API 키 재설정"):
        st.session_state.show_api_settings = True

# 데이터 디버깅 정보 표시 토글
if st.sidebar.button("디버그 정보 표시" if not st.session_state.show_debug_info else "디버그 정보 숨기기"):
    st.session_state.show_debug_info = not st.session_state.show_debug_info

# 디버그 정보 표시
if st.session_state.show_debug_info:
    st.sidebar.subheader("디버그 정보")
    data_dir = get_data_dir()
    data_dir, memories_file, emotions_file, today_word_file, images_dir = get_file_paths()
    
    st.sidebar.write(f"데이터 디렉토리: {data_dir}")
    st.sidebar.write(f"쓰기 권한: {os.access(data_dir, os.W_OK)}")
    
    if os.path.exists(memories_file):
        try:
            memories = pd.read_csv(memories_file)
            st.sidebar.write(f"추억 수: {len(memories)}")
        except:
            st.sidebar.write("추억 파일 읽기 오류")
    else:
        st.sidebar.write("추억 파일 없음")
    
    if os.path.exists(emotions_file):
        try:
            emotions = pd.read_csv(emotions_file)
            st.sidebar.write(f"감정 기록 수: {len(emotions)}")
        except:
            st.sidebar.write("감정 파일 읽기 오류")
    else:
        st.sidebar.write("감정 파일 없음")
    
    if os.path.exists(today_word_file):
        st.sidebar.write("오늘의 한마디 파일 있음")
    else:
        st.sidebar.write("오늘의 한마디 파일 없음")
    
    st.sidebar.write("세션 상태:")
    st.sidebar.write(f"- 추억 업데이트됨: {st.session_state.memories_updated}")
    st.sidebar.write(f"- 감정 업데이트됨: {st.session_state.emotions_updated}")
    st.sidebar.write(f"- 오늘의 한마디 업데이트됨: {st.session_state.today_word_updated}")

# API 키 설정 UI
if st.session_state.show_api_settings:
    with st.sidebar.form("api_key_form"):
        new_api_key = st.text_input("OpenAI API 키", type="password", help="https://platform.openai.com/api-keys 에서 API 키를 발급받으세요.")
        submit_key = st.form_submit_button("저장")
        
        if submit_key and new_api_key:
            if save_api_key(new_api_key):
                st.success("API 키가 저장되었습니다. 앱을 새로고침해주세요.")
                st.session_state.show_api_settings = False
                api_key = new_api_key
                api_key_is_valid = True

# 네비게이션 버튼들
if st.sidebar.button("🏠 홈"):
    st.session_state.current_page = 'home'
if st.sidebar.button("📚 추억 타임라인"):
    st.session_state.current_page = 'timeline'
if st.sidebar.button("💬 대화 분석"):
    st.session_state.current_page = 'conversation'
if st.sidebar.button("📊 감정 히스토리"):
    st.session_state.current_page = 'emotions'

# 현재 페이지에 따라 다른 내용 표시
if st.session_state.current_page == 'home':
    # 홈 페이지
    st.title("🏠 홈")
    
    if not api_key_is_valid:
        st.warning("⚠️ OpenAI API 키가 설정되지 않았습니다. 사이드바에서 API 키를 설정해주세요.")
    
    # 오늘의 한마디
    st.header("💌 오늘의 한마디")
    
    # 기존의 오늘의 한마디 불러오기
    today_word_data = load_today_word()
    today_word = today_word_data.get('word', '')
    
    # 오늘의 한마디 입력 폼
    with st.form("today_word_form"):
        new_word = st.text_area("오늘 하고 싶은 말을 적어보세요:", value=today_word, height=100)
        submit_word = st.form_submit_button("저장하기")
    
    if submit_word:
        if save_today_word(new_word):
            st.success("오늘의 한마디가 저장되었습니다! 💕")
            if st.session_state.today_word_updated:
                st.rerun()
    
    # 최근 추억 표시
    st.header("✨ 최근 추억")
    recent_memories = load_recent_memories(3)
    
    if not recent_memories.empty:
        for _, memory in recent_memories.iterrows():
            # 이미지 로드
            image = None
            if memory['image_path'] and not pd.isna(memory['image_path']):
                image = load_image(memory['image_path'])
            
            # 메모리 카드 표시
            utils.display_memory_card(
                memory['date'],
                memory['title'],
                memory['content'],
                memory['summary'],
                memory['emotion'],
                memory['empathy'],
                image
            )
    else:
        st.info("아직 저장된 추억이 없어요! '대화 분석' 탭에서 새로운 추억을 만들어보세요.")

elif st.session_state.current_page == 'timeline':
    # 추억 타임라인 페이지
    st.title("📚 추억 타임라인")
    
    # 모든 추억 불러오기
    all_memories = load_all_memories()
    
    if not all_memories.empty:
        for _, memory in all_memories.iterrows():
            # 이미지 로드
            image = None
            if memory['image_path'] and not pd.isna(memory['image_path']):
                image = load_image(memory['image_path'])
            
            # 메모리 카드 표시
            utils.display_memory_card(
                memory['date'],
                memory['title'],
                memory['content'],
                memory['summary'],
                memory['emotion'],
                memory['empathy'],
                image
            )
    else:
        st.info("아직 저장된 추억이 없어요! '대화 분석' 탭에서 새로운 추억을 만들어보세요.")

elif st.session_state.current_page == 'conversation':
    # 대화 분석 페이지
    st.title("💬 대화 분석")
    
    # API 키 미설정 경고
    if not api_key_is_valid:
        st.warning("⚠️ OpenAI API 키가 설정되지 않아 AI 분석 기능을 사용할 수 없습니다. 사이드바에서 API 키를 설정해주세요.")
    
    st.markdown("""
    대화 내용을 입력하면 AI가 다음을 생성합니다:
    1. 따뜻한 요약
    2. 감정 분석
    3. 공감 멘트
    """)
    
    # 대화 입력 폼
    with st.form("conversation_form"):
        title = st.text_input("추억의 제목:")
        conversation = st.text_area("대화 내용을 입력하세요:", height=200)
        
        # 이미지 업로드
        uploaded_file = st.file_uploader("이미지 추가하기 (선택사항)", type=["jpg", "jpeg", "png"])
        
        analyze_button = st.form_submit_button("분석하기")
    
    # 분석 버튼이 클릭되었을 때
    if analyze_button and conversation and title:
        with st.spinner("AI가 대화를 분석하고 있어요..."):
            # GPT로 대화 분석
            summary, emotion, empathy = analyze_conversation(conversation)
            
            # 결과 표시
            st.success("대화 분석이 완료되었습니다!")
            
            st.subheader("🌟 요약")
            st.write(summary)
            
            st.subheader("💭 감정 분석")
            st.write(emotion)
            
            st.subheader("💌 공감 멘트")
            st.write(empathy)
            
            # 이미지 처리
            image = None
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="업로드된 이미지", use_column_width=True)
            
            # 저장 버튼
            if st.button("추억으로 저장하기"):
                if save_memory(title, conversation, summary, emotion, empathy, image):
                    st.success("추억이 저장되었습니다! 💕")
                    # 타임라인 페이지로 이동
                    if st.session_state.memories_updated:
                        st.session_state.current_page = 'timeline'
                        st.rerun()
    elif analyze_button:
        if not title:
            st.error("추억의 제목을 입력해주세요.")
        if not conversation:
            st.error("대화 내용을 입력하세요.")

elif st.session_state.current_page == 'emotions':
    # 감정 히스토리 페이지
    st.title("📊 감정 히스토리")
    
    # 모든 감정 데이터 불러오기
    emotions_data = load_all_emotions()
    
    if not emotions_data.empty:
        # 감정 시각화
        emotion_chart = visualize_emotions()
        
        if emotion_chart:
            st.image(f"data:image/png;base64,{emotion_chart}", use_column_width=True)
        
        # 감정 데이터 테이블로 표시
        st.subheader("감정 기록")
        
        # 날짜 포맷 변경
        emotions_data['formatted_date'] = emotions_data['date'].apply(utils.format_date)
        
        # 테이블 표시
        for _, emotion in emotions_data.iterrows():
            st.markdown(f"""
            <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                <div style="font-weight: bold; color: #1565C0;">{emotion['formatted_date']}</div>
                <div style="font-size: 18px; margin: 10px 0;">{emotion['emotion']}</div>
                <div style="color: #757575; font-size: 14px;">{emotion['reason']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("아직 감정 기록이 없어요! '대화 분석' 탭에서 대화를 통해 감정을 기록해보세요.")

# 푸터 추가
utils.create_footer() 