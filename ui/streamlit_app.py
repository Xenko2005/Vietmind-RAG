import requests
import streamlit as st


API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="VietMind-RAG",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 VietMind-RAG")
st.caption("Local Vietnamese Knowledge Assistant using RAG + Ollama + ChromaDB")

with st.sidebar:
    st.header("Upload tài liệu")

    uploaded_file = st.file_uploader(
        "Chọn file PDF/TXT/DOCX",
        type=["pdf", "txt", "docx"]
    )

    if uploaded_file is not None:
        if st.button("Index tài liệu"):
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            with st.spinner("Đang xử lý và index tài liệu..."):
                response = requests.post(
                    f"{API_URL}/upload",
                    files=files,
                    timeout=300
                )

            if response.status_code == 200:
                st.success("Index thành công!")
                st.json(response.json())
            else:
                st.error(response.text)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Hỏi gì đó về tài liệu của bạn...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm tài liệu và sinh câu trả lời..."):
            response = requests.post(
                f"{API_URL}/ask",
                json={
                    "question": question,
                    "top_k": 5
                },
                timeout=300
            )

            if response.status_code == 200:
                data = response.json()
                answer = data["answer"]

                st.markdown(answer)

                with st.expander("Xem các đoạn tài liệu được truy xuất"):
                    for source in data["sources"]:
                        st.markdown(
                            f"**File:** {source['source']} | "
                            f"**Trang:** {source['page']} | "
                            f"**Distance:** {source['distance']:.4f}"
                        )
                        st.write(source["text"])
                        st.divider()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
            else:
                st.error(response.text)