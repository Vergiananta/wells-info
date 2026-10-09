import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from src.backend import WellsPipelineService, settings

st.set_page_config(
    page_title="Wells Information and Glossary QA",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stChatMessage {
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        background-color: #1e293b;
    }
    .source-badge {
        display: inline-block;
        background-color: #0f172a;
        color: #38bdf8;
        border: 1px solid #0284c7;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 0.8rem;
        margin-right: 6px;
        margin-top: 4px;
    }
    .status-card {
        background-color: #1e293b;
        border-radius: 6px;
        padding: 12px;
        border-left: 4px solid #38bdf8;
        margin-bottom: 12px;
    }
    .stButton>button {
        border-radius: 4px;
        font-weight: 500;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

@st.cache_resource
def get_pipeline():
    pipeline = WellsPipelineService()
    pipeline.initialize()
    return pipeline

def main():
    st.title("Wells Information and Glossary AI System")
    st.caption("Document-Grounded QA and Oil and Gas Knowledge Base")

    pipeline = get_pipeline()

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Halo. Saya adalah asisten AI untuk informasi operasional sumur dan istilah glosarium Oil and Gas. Silakan ajukan pertanyaan seputar dokumen yang tersedia.",
                "sources": []
            }
        ]

    if "pending_prompt" not in st.session_state:
        st.session_state["pending_prompt"] = None

    with st.sidebar:
        st.header("Sistem dan Data")
        
        st.markdown(
            f"""
            <div class="status-card">
                <div><strong>Model LLM:</strong> {settings.chat_model}</div>
                <div><strong>Embedding:</strong> {settings.embedding_model}</div>
                <div><strong>Database:</strong> SQLite FTS5</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("Manajemen Data")
        if st.button("Proses Ulang Dokumen (Reparse)", use_container_width=True):
            with st.spinner("Memproses ulang seluruh dokumen PDF dan DOCX..."):
                pipeline.initialize(force_reparse=True)
                st.success("Dokumen berhasil diparsing dan diindeks ulang.")

        st.divider()
        st.subheader("Pertanyaan Contoh")
        sample_questions = [
            "Dimana letak lokasi sumur ?",
            "Berapa Total NPT sumur ?",
            "Wireline run apa yang direncanakan ?",
            "Apa arti dari istilah BHA, NPT, dan MDT pada glosarium migas?",
            "Siapa presiden Amerika Serikat saat ini?"
        ]

        for q in sample_questions:
            if st.button(q, key=f"btn_{q}", use_container_width=True):
                st.session_state["pending_prompt"] = q
                st.rerun()

        st.divider()
        if st.button("Hapus Riwayat Chat", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["pending_prompt"] = None
            st.rerun()

    for message in st.session_state["messages"]:
        avatar_icon = "🧠" if message["role"] == "assistant" else "user"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])
            if message.get("sources"):
                st.markdown("**Dokumen Sumber Terkait:**")
                badges_html = "".join(
                    [f'<span class="source-badge">{src}</span>' for src in message["sources"]]
                )
                st.markdown(badges_html, unsafe_allow_html=True)

    user_input = st.chat_input("Ketik pertanyaan seputar sumur atau glosarium...")

    active_prompt = None
    if user_input:
        active_prompt = user_input
    elif st.session_state["pending_prompt"]:
        active_prompt = st.session_state["pending_prompt"]
        st.session_state["pending_prompt"] = None

    if active_prompt:
        st.session_state["messages"].append({"role": "user", "content": active_prompt})
        with st.chat_message("user", avatar="user"):
            st.markdown(active_prompt)

        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("Mencari dokumen dan menyusun jawaban..."):
                result = pipeline.ask(active_prompt)
                st.markdown(result.answer)

                if result.sources:
                    st.markdown("**Dokumen Sumber Terkait:**")
                    badges_html = "".join(
                        [f'<span class="source-badge">{src}</span>' for src in result.sources]
                    )
                    st.markdown(badges_html, unsafe_allow_html=True)

                if result.retrieved_items:
                    with st.expander("Detail Potongan Dokumen yang Ditemukan (Retrieval Context)"):
                        for idx, item in enumerate(result.retrieved_items, 1):
                            chunk = item.chunk
                            page_str = f"Halaman {chunk.page}" if chunk.page > 0 else "Summary"
                            st.markdown(
                                f"**[{idx}] {chunk.source_file}** ({page_str}) - *Score: {item.score:.3f}*"
                            )
                            st.text(chunk.content[:400] + ("..." if len(chunk.content) > 400 else ""))
                            st.divider()

                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": result.answer,
                    "sources": result.sources
                })
        st.rerun()

if __name__ == "__main__":
    main()
