import streamlit as st

st.set_page_config(page_title="한바다 챗봇", page_icon="🌊", layout="centered")

st.title("한바다 - OCEAN ICT 탐구 챗봇")
st.markdown("팀별 탐구 내용을 기반으로 질문에 답변하는 AI 챗봇입니다.\n\n*현재는 데모용 대화창입니다.*")

# 채팅 내역 저장용 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 사용자 입력 받기
user_input = st.text_input("질문을 입력하세요", key="input")

if user_input:
    # 사용자가 입력한 메시지를 대화 내역에 추가
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # (여기에 실제 AI 답변 처리 로직 넣으면 됨)
    # 지금은 단순히 "답변 준비 중입니다" 출력
    bot_response = "답변 준비 중입니다..."
    st.session_state.chat_history.append({"role": "bot", "content": bot_response})

# 채팅 내역 출력 (가장 최신 메시지 아래쪽에 표시)
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"<div style='text-align: right; color: blue; padding:5px 10px; border-radius:10px; background:#D6EAF8; margin: 5px 0;'>{chat['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: left; color: black; padding:5px 10px; border-radius:10px; background:#F2F3F4; margin: 5px 0;'>{chat['content']}</div>", unsafe_allow_html=True)
