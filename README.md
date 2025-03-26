# Mindtone - 감정 지원 챗봇

Mindtone은 사용자가 자신의 감정을 선택하고 AI 챗봇과 대화할 수 있는 간단한 웹 애플리케이션입니다.

## 주요 기능

- **감정 선택**: 기쁨, 슬픔, 화남, 불안 등 다양한 감정 버튼 중에서 선택할 수 있습니다.
- **AI 챗봇 대화**: 선택한 감정에 맞게 공감하고 이해하는 AI와 대화할 수 있습니다.
- **채팅 기록**: 사용자와 AI의 대화 내용이 채팅 인터페이스에 표시됩니다.

## 설치 방법

1. 필요한 패키지 설치:
   ```
   pip install -r requirements.txt
   ```

2. `.env` 파일에 OpenAI API 키 설정:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## 실행 방법

```
streamlit run app.py
```

## 기술 스택

- **프레임워크**: Streamlit
- **언어**: Python
- **AI 모델**: OpenAI GPT-3.5 Turbo
- **UI 컴포넌트**: 
  - 감정 버튼 (이모지와 색상으로 스타일링)
  - 채팅 인터페이스 (스크롤 가능)
  - 입력 박스와 전송 버튼

## 사용자 흐름

1. 사용자가 페이지에 접속하면 감정 선택 버튼이 표시됩니다.
2. 감정을 선택하면 채팅 인터페이스가 나타납니다.
3. 사용자가 메시지를 입력하고 전송하면 AI가 응답합니다.
4. 모든 메시지는 세션 동안 유지됩니다. 