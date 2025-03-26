import streamlit as st
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Mindtone - 감정 지원 챗봇",
    page_icon="💭",
    layout="centered"
)

# 사이드바에 앱 정보 표시
st.sidebar.title("Mindtone")
st.sidebar.write("감정 지원 AI 챗봇")
st.sidebar.divider()
st.sidebar.write("자신의 감정을 선택하고 AI와 대화하세요.")

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    st.error("OpenAI API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 설정해주세요.")
    st.stop()

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_emotion' not in st.session_state:
    st.session_state.current_emotion = None

# 메인 페이지 제목
st.title("Mindtone")
st.write("지금 어떤 감정이 드시나요?")

# 감정 버튼 스타일 설정
emotion_button_style = """
<style>
    div.emotion-button > button {
        background-color: #f0f2f6;
        border-radius: 12px;
        padding: 15px 15px;
        font-size: 16px;
        margin: 5px;
        transition: all 0.3s;
    }
    div.emotion-button > button:hover {
        background-color: #e0e2e6;
        transform: translateY(-2px);
    }
    div.emotion-active > button {
        background-color: #6c7ac9;
        color: white;
    }
</style>
"""
st.markdown(emotion_button_style, unsafe_allow_html=True)

# 감정 버튼 정의
emotions = {
    "기쁨": "😊",
    "슬픔": "😢",
    "화남": "😠",
    "불안": "😰",
    "지침": "😩",
    "혼란": "😕",
    "희망": "🌈",
    "감사": "🙏"
}

# 감정 버튼 행 생성
col1, col2, col3, col4 = st.columns(4)
cols = [col1, col2, col3, col4]

for idx, (emotion, emoji) in enumerate(emotions.items()):
    col_idx = idx % 4
    button_text = f"{emoji} {emotion}"
    
    # 선택된 감정에 active 클래스 추가
    button_class = "emotion-button"
    if st.session_state.current_emotion == emotion:
        button_class += " emotion-active"
    
    with cols[col_idx]:
        st.markdown(f'<div class="{button_class}">', unsafe_allow_html=True)
        if st.button(button_text, key=f"emotion_{emotion}"):
            st.session_state.current_emotion = emotion
            if not st.session_state.messages:
                # AI의 첫 응답 추가
                ai_first_msg = f"안녕하세요! 오늘 {emotion} 감정을 느끼고 계시는군요. 어떤 일이 있으신가요?"
                st.session_state.messages.append({"role": "assistant", "content": ai_first_msg})
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 현재 선택된 감정 표시
if st.session_state.current_emotion:
    st.write(f"현재 감정: {emotions[st.session_state.current_emotion]} {st.session_state.current_emotion}")
    
    # 채팅 인터페이스 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                # 시스템 메시지로 현재 감정 정보 전달
                messages = [
                    {"role": "system", "content": f"당신은 감정 지원 AI 챗봇입니다. 사용자가 '{st.session_state.current_emotion}' 감정을 느끼고 있습니다. 공감적이고 이해심 있는 태도로 대화해주세요."}
                ]
                
                # 이전 대화 기록 추가
                for msg in st.session_state.messages:
                    messages.append(msg)
                
                # API 호출
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                
                ai_response = response.choices[0].message.content
                st.write(ai_response)
                
                # AI 응답 저장
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
else:
    st.info("대화를 시작하려면 위에서 감정을 선택해주세요.") 