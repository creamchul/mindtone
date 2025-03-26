import os
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64
import tempfile
import streamlit as st

# 데이터 저장 경로 (스트림릿 세션 상태 또는 임시 디렉토리 사용)
def get_data_dir():
    # 스트림릿이 실행 중인 환경이라면 st.session_state를 사용
    if 'data_dir' not in st.session_state:
        # 기본 'data' 디렉토리 시도 (로컬 실행 시)
        if os.access('.', os.W_OK):
            data_dir = 'data'
        else:
            # 쓰기 권한이 없으면 임시 디렉토리 사용
            data_dir = os.path.join(tempfile.gettempdir(), 'couple_app_data')
        st.session_state.data_dir = data_dir
    
    return st.session_state.data_dir

# 파일 경로 가져오기
def get_file_paths():
    data_dir = get_data_dir()
    memories_file = os.path.join(data_dir, 'memories.csv')
    emotions_file = os.path.join(data_dir, 'emotions.csv')
    today_word_file = os.path.join(data_dir, 'today_word.json')
    images_dir = os.path.join(data_dir, 'images')
    
    return data_dir, memories_file, emotions_file, today_word_file, images_dir

# 데이터 디렉토리 초기화
def init_data_dir():
    data_dir, memories_file, emotions_file, today_word_file, images_dir = get_file_paths()
    
    try:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        # 메모리 파일 초기화
        if not os.path.exists(memories_file):
            df = pd.DataFrame(columns=['date', 'title', 'content', 'summary', 'emotion', 'empathy', 'image_path'])
            df.to_csv(memories_file, index=False, encoding='utf-8')
        
        # 감정 파일 초기화
        if not os.path.exists(emotions_file):
            df = pd.DataFrame(columns=['date', 'emotion', 'reason'])
            df.to_csv(emotions_file, index=False, encoding='utf-8')
        
        # 오늘의 한마디 파일 초기화
        if not os.path.exists(today_word_file):
            with open(today_word_file, 'w', encoding='utf-8') as f:
                json.dump({'date': datetime.now().strftime('%Y-%m-%d'), 'word': ''}, f, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"데이터 디렉토리 초기화 중 오류 발생: {str(e)}")
        return False

# 추억 저장 함수
def save_memory(title, content, summary, emotion, empathy, image=None):
    if not init_data_dir():
        st.error("데이터 디렉토리를 초기화할 수 없습니다.")
        return False
    
    data_dir, memories_file, _, _, images_dir = get_file_paths()
    
    try:
        # 현재 날짜 가져오기
        date = datetime.now().strftime('%Y-%m-%d')
        
        # 이미지 저장 경로
        image_path = None
        if image is not None:
            try:
                image_filename = f"{date}_{title.replace(' ', '_')}.jpg"
                image_path = os.path.join('images', image_filename)
                image.save(os.path.join(data_dir, image_path))
            except Exception as e:
                st.warning(f"이미지 저장 중 오류 발생: {str(e)}")
                image_path = None
        
        # 기존 데이터 로드
        try:
            memories = pd.read_csv(memories_file, encoding='utf-8')
        except:
            memories = pd.DataFrame(columns=['date', 'title', 'content', 'summary', 'emotion', 'empathy', 'image_path'])
        
        # 새 데이터 추가
        new_memory = pd.DataFrame({
            'date': [date],
            'title': [title],
            'content': [content],
            'summary': [summary],
            'emotion': [emotion],
            'empathy': [empathy],
            'image_path': [image_path]
        })
        
        memories = pd.concat([memories, new_memory], ignore_index=True)
        memories.to_csv(memories_file, index=False, encoding='utf-8')
        
        # 데이터가 저장되었는지 확인
        st.session_state.memories_updated = True
        
        # 감정 데이터도 저장
        save_emotion(date, emotion, "대화 기반 감정 분석")
        
        return True
    except Exception as e:
        st.error(f"추억 저장 중 오류 발생: {str(e)}")
        return False

# 감정 저장 함수
def save_emotion(date, emotion, reason):
    if not init_data_dir():
        st.error("데이터 디렉토리를 초기화할 수 없습니다.")
        return False
    
    _, _, emotions_file, _, _ = get_file_paths()
    
    try:
        # 기존 데이터 로드
        try:
            emotions = pd.read_csv(emotions_file, encoding='utf-8')
        except:
            emotions = pd.DataFrame(columns=['date', 'emotion', 'reason'])
        
        # 같은 날짜에 이미 감정이 저장되어 있는지 확인
        if date in emotions['date'].values:
            emotions.loc[emotions['date'] == date, 'emotion'] = emotion
            emotions.loc[emotions['date'] == date, 'reason'] = reason
        else:
            new_emotion = pd.DataFrame({
                'date': [date],
                'emotion': [emotion],
                'reason': [reason]
            })
            emotions = pd.concat([emotions, new_emotion], ignore_index=True)
        
        emotions.to_csv(emotions_file, index=False, encoding='utf-8')
        
        # 데이터가 저장되었는지 확인
        st.session_state.emotions_updated = True
        
        return True
    except Exception as e:
        st.error(f"감정 저장 중 오류 발생: {str(e)}")
        return False

# 오늘의 한마디 저장 함수
def save_today_word(word):
    if not init_data_dir():
        st.error("데이터 디렉토리를 초기화할 수 없습니다.")
        return False
    
    _, _, _, today_word_file, _ = get_file_paths()
    
    try:
        date = datetime.now().strftime('%Y-%m-%d')
        
        with open(today_word_file, 'w', encoding='utf-8') as f:
            json.dump({'date': date, 'word': word}, f, ensure_ascii=False)
        
        # 데이터가 저장되었는지 확인
        st.session_state.today_word_updated = True
        
        return True
    except Exception as e:
        st.error(f"오늘의 한마디 저장 중 오류 발생: {str(e)}")
        return False

# 오늘의 한마디 불러오기 함수
def load_today_word():
    if not init_data_dir():
        st.warning("데이터 디렉토리를 초기화할 수 없습니다.")
        return {'date': datetime.now().strftime('%Y-%m-%d'), 'word': ''}
    
    _, _, _, today_word_file, _ = get_file_paths()
    
    try:
        with open(today_word_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.warning(f"오늘의 한마디를 불러오는 중 오류 발생: {str(e)}")
        return {'date': datetime.now().strftime('%Y-%m-%d'), 'word': ''}

# 모든 추억 불러오기 함수
def load_all_memories():
    if not init_data_dir():
        st.warning("데이터 디렉토리를 초기화할 수 없습니다.")
        return pd.DataFrame(columns=['date', 'title', 'content', 'summary', 'emotion', 'empathy', 'image_path'])
    
    _, memories_file, _, _, _ = get_file_paths()
    
    try:
        memories = pd.read_csv(memories_file, encoding='utf-8')
        return memories.sort_values('date', ascending=False)
    except Exception as e:
        st.warning(f"추억을 불러오는 중 오류 발생: {str(e)}")
        return pd.DataFrame(columns=['date', 'title', 'content', 'summary', 'emotion', 'empathy', 'image_path'])

# 최근 추억 N개 불러오기 함수
def load_recent_memories(n=3):
    memories = load_all_memories()
    if len(memories) > 0:
        return memories.head(n)
    return memories

# 특정 날짜의 추억 불러오기 함수
def load_memory_by_date(date):
    memories = load_all_memories()
    return memories[memories['date'] == date]

# 모든 감정 데이터 불러오기 함수
def load_all_emotions():
    if not init_data_dir():
        st.warning("데이터 디렉토리를 초기화할 수 없습니다.")
        return pd.DataFrame(columns=['date', 'emotion', 'reason'])
    
    _, _, emotions_file, _, _ = get_file_paths()
    
    try:
        emotions = pd.read_csv(emotions_file, encoding='utf-8')
        return emotions.sort_values('date')
    except Exception as e:
        st.warning(f"감정 데이터를 불러오는 중 오류 발생: {str(e)}")
        return pd.DataFrame(columns=['date', 'emotion', 'reason'])

# 감정 시각화 함수
def visualize_emotions():
    emotions = load_all_emotions()
    
    if emotions.empty:
        return None
    
    try:
        # 날짜와 감정만 추출
        plt.figure(figsize=(12, 5))
        
        # 자주 등장하는 감정들
        common_emotions = ['기쁨', '행복', '설렘', '사랑', '감동', '감사', '그리움', '기대', 
                          '슬픔', '우울', '불안', '걱정', '화남', '짜증', '답답함']
        
        # 감정이 자주 등장하는 감정 중 하나인지 확인
        def map_emotion(emotion_text):
            if pd.isna(emotion_text):
                return '알 수 없음'
            for common in common_emotions:
                if common in emotion_text:
                    return common
            emotion_words = emotion_text.split()
            if emotion_words:
                return emotion_words[0]  # 첫 번째 단어만 사용
            return '알 수 없음'
        
        # 감정 매핑
        emotions['mapped_emotion'] = emotions['emotion'].apply(map_emotion)
        
        # 그래프 생성
        emotion_counts = emotions['mapped_emotion'].value_counts()
        plt.figure(figsize=(10, 6))
        if not emotion_counts.empty:
            emotion_counts.plot(kind='bar', color='skyblue')
            plt.title('감정 분포')
            plt.xlabel('감정')
            plt.ylabel('횟수')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # 이미지 바이트로 변환
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            
            # 이미지 인코딩
            img_str = base64.b64encode(buf.read()).decode()
            plt.close()
            
            return img_str
        
        plt.close()
        return None
    except Exception as e:
        st.warning(f"감정 시각화 중 오류 발생: {str(e)}")
        return None

# 이미지 로드 함수
def load_image(image_path):
    if not image_path or pd.isna(image_path):
        return None
    
    data_dir, _, _, _, _ = get_file_paths()
    
    try:
        full_path = os.path.join(data_dir, image_path)
        if os.path.exists(full_path):
            return Image.open(full_path)
    except Exception as e:
        st.warning(f"이미지를 불러오는 중 오류 발생: {str(e)}")
    
    return None 