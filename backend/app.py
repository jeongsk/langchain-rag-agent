import traceback
import uuid

import streamlit as st

from graph import agent


def extract_text_content(content):
    """메시지 콘텐츠에서 텍스트를 추출합니다."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item["text"])
            elif isinstance(item, str):
                text_parts.append(item)
        return "\n".join(text_parts)

    return ""


# 페이지 설정
st.set_page_config(
    page_title="LangChain & LangGraph RAG 챗봇",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


# 사이드바
with st.sidebar:
    st.title("🤖 LangChain & LangGraph RAG 챗봇")
    st.markdown("""
    LangChain과 LangGraph 공식 문서를 기반으로 질문에 답변합니다.

    📚 **지원하는 주제:**
    - LangChain/LangGraph API, 클래스, 메서드
    - 구현 패턴과 모범 사례
    - 상태 관리, 에이전트 워크플로우
    - 도구 통합 및 함수 호출
    - 문제 해결 및 디버깅

    💬 **한국어로 질문해주세요!**
    """)

    st.divider()

    st.subheader("📝 예제 질문")
    examples = [
        "LangGraph에서 supervisor agent를 만드는 방법을 알려줘",
        "LangChain에서 tool calling을 어떻게 사용하나요?",
        "StateGraph에서 concurrent updates는 어떻게 처리하나요?",
        "LangGraph의 checkpointer는 무엇인가요?",
        "LangChain에서 RAG를 구현하는 방법을 설명해줘",
    ]

    for idx, example in enumerate(examples):
        if st.button(example, key=f"example_{idx}", use_container_width=True):
            st.session_state.selected_example = example
            st.session_state.example_processed = True

    st.divider()

    if st.button("🗑️ 대화 기록 지우기", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()


# 메인 영역
st.title("💬 채팅")

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 예제 질문 처리
if "selected_example" in st.session_state:
    user_input = st.session_state.selected_example
    del st.session_state.selected_example
else:
    user_input = st.chat_input("질문을 입력하세요...")

# 사용자 입력 처리
if user_input:
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 어시스턴트 응답 생성
    with st.chat_message("assistant"):
        status_container = st.empty()
        tool_placeholder = st.empty()
        tool_call_placeholder = st.empty()
        message_placeholder = st.empty()
        full_response = ""

        try:
            with status_container.status("답변 생성 중...", state="running") as status:
                for chunk in agent.stream(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config={"configurable": {"thread_id": st.session_state.thread_id}},
                    stream_mode="updates",
                ):
                    for node_name, state in chunk.items():
                        print("node_name:", node_name)

                        if not isinstance(state, dict) or not state.get("messages"):
                            continue

                        for msg in state["messages"]:
                            msg_type = type(msg).__name__

                            # 1. 도구 호출
                            if msg_type == "AIMessage" and msg.tool_calls:
                                for tool_call in msg.tool_calls:
                                    with tool_placeholder.expander(
                                        f"🔧 도구 호출: {tool_call['name']}",
                                        expanded=False,
                                    ):
                                        st.json(tool_call["args"])

                            # 2 도구 실행 결과
                            elif msg_type == "ToolMessage":
                                with tool_call_placeholder.expander(
                                    f"🔧 도구 결과: {msg.name}", expanded=False
                                ):
                                    st.text(msg.content)

                            # 3. 최종 AI 응답
                            elif msg_type == "AIMessage":
                                full_response += extract_text_content(msg.content)
                                if full_response:
                                    message_placeholder.markdown(full_response)

            # 답변 완료 후 status 제거
            status_container.empty()

        except Exception as e:
            traceback.print_exc()
            error_message = f"오류가 발생했습니다: {str(e)}"
            st.error(error_message)
            full_response = error_message

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

        # 예제 질문 처리 후 재실행하여 입력창 다시 표시
        if "example_processed" in st.session_state:
            del st.session_state.example_processed
            st.rerun()
