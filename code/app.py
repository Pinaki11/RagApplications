import streamlit as st

from rag_query import answer_query


# Configure the browser page and create a focused insurance assistant shell.
st.set_page_config(
    page_title="Insurance Query Agent",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="expanded",
)


# Keep the visual language calm and trustworthy without hiding core controls.
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root { --ink: #17313b; --muted: #667b80; --teal: #087f78; --mint: #e4f2ed; --line: #d8e6e2; --paper: #fbfdfb; }
        .stApp { background: radial-gradient(circle at 15% 0%, #e7f3ef 0, #f7faf8 34%, #fbfdfb 72%); color: var(--ink); }
        .block-container { max-width: 850px; padding-top: 2.7rem; padding-bottom: 3rem; }
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; color: var(--ink) !important; }
        p, div, textarea, button { font-family: 'DM Sans', sans-serif; }
        .brand { display: flex; align-items: center; gap: 13px; margin-bottom: 1.6rem; }
        .brand-mark { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 13px; background: var(--teal); color: white; font-size: 22px; box-shadow: 0 8px 20px #087f7833; }
        .brand-name { font-family: 'Space Grotesk', sans-serif; font-size: 1.06rem; font-weight: 700; letter-spacing: .01em; }
        .brand-caption { color: var(--muted); font-size: .8rem; margin-top: 2px; }
        .hero { padding: 1.55rem 1.65rem 1.4rem; border: 1px solid var(--line); border-radius: 18px; background: #ffffffb8; box-shadow: 0 15px 40px #17313b0b; margin-bottom: 1.6rem; }
        .eyebrow { color: var(--teal); font-size: .75rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
        .hero h1 { font-size: clamp(1.8rem, 4vw, 2.7rem); margin: .3rem 0 .45rem; }
        .hero p { color: var(--muted); margin: 0; line-height: 1.6; }
        [data-testid='stChatMessage'] { border: 1px solid var(--line); border-radius: 16px; padding: .9rem 1rem; background: #ffffffaa; }
        [data-testid='stChatMessage']:has([data-testid='chatAvatarIcon-user']) { background: var(--mint); border-color: #c8e2da; }
        [data-testid='stChatInput'] { border-top: 1px solid var(--line); padding-top: 1rem; }
        .stButton button { border-radius: 10px; border: 1px solid var(--line); color: var(--ink); }
        .source-note { color: var(--muted); font-size: .77rem; padding-top: .5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# Initialize the chat with the requested greeting and a useful opening prompt.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi I am Alexa,How can I help you today?",
            "sources": [],
        }
    ]


st.markdown(
    """
    <div class="brand">
        <div class="brand-mark">✦</div>
        <div><div class="brand-name">Insurance Query Agent</div><div class="brand-caption">Policy intelligence, grounded in your documents</div></div>
    </div>
    <div class="hero">
        <div class="eyebrow">Your policy desk</div>
        <h1>Ask with confidence.</h1>
        <p>Explore waiting periods, coverage terms, premiums, and plan details across the indexed insurance policies.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Offer a simple reset action without disturbing the main conversation area.
with st.sidebar:
    st.markdown("### Insurance Query Agent")
    st.caption("Ask follow-up questions naturally. Each answer is grounded in the indexed policy pages.")
    if st.button("Start a new conversation", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi I am Alexa,How can I help you today?", "sources": []}
        ]
        st.rerun()
    st.divider()
    st.caption("Answers are for demonstration and document-retrieval purposes. The policy PDFs are fictional.")


# Render the conversation history, including compact source provenance on answers.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            sources = ", ".join(
                f"{source['company']} · p.{source['page']}" for source in message["sources"]
            )
            st.markdown(f'<div class="source-note">Sources: {sources}</div>', unsafe_allow_html=True)


# Retrieve fresh policy context and pass the recent conversation to Azure OpenAI.
query = st.chat_input("Ask about a policy, plan, or coverage term...")
if query:
    st.session_state.messages.append({"role": "user", "content": query, "sources": []})
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("Reviewing the policy documents..."):
            try:
                conversation = [
                    {"role": item["role"], "content": item["content"]}
                    for item in st.session_state.messages[:-1]
                    if item["role"] in {"user", "assistant"}
                ]
                result = answer_query(query, n_results=5, conversation=conversation)
                answer = result["answer"]
                sources = [chunk["metadata"] for chunk in result["chunks"]]
            except Exception as error:
                answer = f"I could not complete that request: {error}"
                sources = []
            st.markdown(answer)
            if sources:
                source_text = ", ".join(f"{source['company']} · p.{source['page']}" for source in sources)
                st.markdown(f'<div class="source-note">Sources: {source_text}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})