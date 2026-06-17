"""Streamlit app for multilingual translation and voice assistance."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from database import (
    TranslationRecord,
    clear_history,
    fetch_history,
    get_statistics,
    initialize_database,
    save_translation,
)
from translator import (
    LANGUAGE_OPTIONS,
    TranslationError,
    TranslationService,
    get_language_code,
    recognize_speech_from_microphone,
    synthesize_speech,
)


APP_TITLE = "Multilingual AI Translation and Voice Assistant"
DEFAULT_SOURCE_LANGUAGE = "English"
DEFAULT_TARGET_LANGUAGE = "Hindi"


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .main .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
                max-width: 1200px;
            }
            .hero {
                border: 1px solid #d7dde8;
                border-radius: 8px;
                padding: 1.25rem 1.4rem;
                background: linear-gradient(135deg, #f7fbff 0%, #f9fafb 55%, #fff7ed 100%);
                margin-bottom: 1rem;
            }
            .hero h1 {
                font-size: 2rem;
                margin: 0 0 .35rem 0;
                letter-spacing: 0;
            }
            .hero p {
                margin: 0;
                color: #4b5563;
                font-size: 1rem;
            }
            .translated-box {
                border: 1px solid #d7dde8;
                border-radius: 8px;
                padding: 1rem;
                min-height: 170px;
                background: #ffffff;
                color: #111827;
                white-space: pre-wrap;
                line-height: 1.55;
            }
            .small-muted {
                color: #6b7280;
                font-size: .9rem;
            }
            div[data-testid="stMetricValue"] {
                font-size: 1.55rem;
            }
            .stButton>button, .stDownloadButton>button {
                border-radius: 8px;
                min-height: 2.55rem;
                font-weight: 600;
            }
            textarea {
                border-radius: 8px !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_translation_service() -> TranslationService:
    return TranslationService()


def get_word_count(text: str) -> int:
    return len([word for word in text.split() if word.strip()])


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>🌐 Multilingual AI Translation and Voice Assistant</h1>
            <p>Translate text, capture speech, generate audio, and track multilingual activity in one production-ready Streamlit dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Translator", "Voice Assistant", "History", "Statistics", "About"],
        label_visibility="collapsed",
    )

    st.sidebar.divider()
    st.sidebar.subheader("⚙️ Settings")
    st.sidebar.caption("Google Translate, Google Speech Recognition, and gTTS require internet access.")
    st.sidebar.caption("History is stored locally in SQLite.")
    return page


def render_statistics_cards() -> None:
    stats = get_statistics()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Translations", stats["total_translations"])
    col2.metric("Source Languages", stats["unique_source_languages"])
    col3.metric("Target Languages", stats["unique_target_languages"])
    col4.metric("Characters", stats["total_characters"])


def render_translator_page() -> None:
    service = get_translation_service()
    st.subheader("📝 Text Translation")
    render_statistics_cards()

    language_names = list(LANGUAGE_OPTIONS.keys())
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        auto_detect = st.toggle("Auto-detect source language", value=True)
    with col2:
        source_language = st.selectbox(
            "Source language",
            language_names,
            index=language_names.index(DEFAULT_SOURCE_LANGUAGE),
            disabled=auto_detect,
        )
    with col3:
        target_language = st.selectbox(
            "Target language",
            language_names,
            index=language_names.index(DEFAULT_TARGET_LANGUAGE),
        )

    input_text = st.text_area(
        "Original text",
        value=st.session_state.get("input_text", ""),
        height=210,
        placeholder="Type or paste text to translate...",
    )

    c1, c2, c3 = st.columns([1, 1, 2])
    c1.metric("Characters", len(input_text))
    c2.metric("Words", get_word_count(input_text))

    translate_clicked = st.button("✨ Translate", type="primary", use_container_width=True)

    if translate_clicked:
        try:
            result = service.translate_text(
                text=input_text,
                target_language=target_language,
                source_language=None if auto_detect else source_language,
            )
            st.session_state["last_translation"] = result
            st.session_state["input_text"] = input_text

            save_translation(
                TranslationRecord(
                    original_text=result["original_text"],
                    source_language=result["source_language"],
                    target_language=result["target_language"],
                    translated_text=result["translated_text"],
                )
            )
            st.success(
                f"Translated from {result['source_language']} to {result['target_language']}."
            )
        except TranslationError as exc:
            st.error(str(exc))

    render_translation_result()


def render_translation_result() -> None:
    result = st.session_state.get("last_translation")
    st.subheader("✅ Translation Result")

    if not result:
        st.info("Your translated text will appear here.")
        return

    st.markdown(
        f"<div class='translated-box'>{result['translated_text']}</div>",
        unsafe_allow_html=True,
    )

    st.caption(
        f"Source: {result['source_language']} | Target: {result['target_language']} | "
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    download_name = f"translation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    col1, col2, col3 = st.columns(3)
    col1.download_button(
        "⬇️ Download TXT",
        data=result["translated_text"],
        file_name=download_name,
        mime="text/plain",
        use_container_width=True,
    )
    with col2:
        render_copy_button(result["translated_text"])

    if col3.button("🔊 Generate audio", use_container_width=True):
        try:
            audio_bytes = synthesize_speech(
                result["translated_text"],
                result["target_code"],
            )
            st.session_state["last_audio"] = audio_bytes
        except TranslationError as exc:
            st.error(str(exc))

    if st.session_state.get("last_audio"):
        st.audio(st.session_state["last_audio"], format="audio/mp3")
        st.download_button(
            "⬇️ Download MP3",
            data=st.session_state["last_audio"],
            file_name="translated_audio.mp3",
            mime="audio/mpeg",
            use_container_width=True,
        )


def render_copy_button(text: str) -> None:
    escaped_text = (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )
    components.html(
        f"""
        <button id="copyButton" style="
            width: 100%;
            min-height: 41px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            background: #ffffff;
            color: #111827;
            font-weight: 600;
            cursor: pointer;
        ">📋 Copy text</button>
        <script>
            const button = document.getElementById("copyButton");
            button.addEventListener("click", async () => {{
                try {{
                    await navigator.clipboard.writeText(`{escaped_text}`);
                    button.innerText = "Copied";
                    setTimeout(() => button.innerText = "📋 Copy text", 1400);
                }} catch (error) {{
                    button.innerText = "Copy failed";
                    setTimeout(() => button.innerText = "📋 Copy text", 1400);
                }}
            }});
        </script>
        """,
        height=48,
    )


def render_voice_page() -> None:
    st.subheader("🎙️ Voice Assistant")
    st.write("Record speech, convert it to text, and send it directly to the translator.")

    language_names = list(LANGUAGE_OPTIONS.keys())
    speech_language = st.selectbox(
        "Speech recognition language",
        language_names,
        index=language_names.index(DEFAULT_SOURCE_LANGUAGE),
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        record_clicked = st.button("🎤 Record from microphone", type="primary", use_container_width=True)
    with col2:
        st.info("Use a local machine with microphone permissions enabled. Cloud deployments may not expose microphone hardware.")

    if record_clicked:
        try:
            language_code = get_language_code(speech_language)
            with st.spinner("Listening..."):
                recognized_text = recognize_speech_from_microphone(language_code)
            st.session_state["input_text"] = recognized_text
            st.success("Speech converted to text.")
            st.text_area("Recognized text", recognized_text, height=140)
            st.caption("Go to the Translator page to translate this captured text.")
        except TranslationError as exc:
            st.error(str(exc))


def render_history_page() -> None:
    st.subheader("🗂️ Translation History")
    search_query = st.text_input("Search history", placeholder="Search text or language...")
    history = fetch_history(search_query)

    col1, col2 = st.columns([1, 1])
    col1.metric("Rows", len(history))

    csv_data = history.to_csv(index=False).encode("utf-8")
    col2.download_button(
        "⬇️ Export CSV",
        data=csv_data,
        file_name="translation_history.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.dataframe(history, use_container_width=True, hide_index=True)

    with st.expander("Danger zone"):
        st.warning("This removes all saved translation history from SQLite.")
        if st.button("Clear all history"):
            clear_history()
            st.success("History cleared. Refresh the page to see the update.")


def render_statistics_page() -> None:
    st.subheader("📊 Translation Statistics")
    render_statistics_cards()
    history = fetch_history()

    if history.empty:
        st.info("Translate some text to populate charts.")
        return

    source_counts = history["Source Language"].value_counts().reset_index()
    source_counts.columns = ["Language", "Count"]
    target_counts = history["Target Language"].value_counts().reset_index()
    target_counts.columns = ["Language", "Count"]

    col1, col2 = st.columns(2)
    col1.bar_chart(source_counts, x="Language", y="Count")
    col2.bar_chart(target_counts, x="Language", y="Count")

    history["Timestamp"] = pd.to_datetime(history["Timestamp"])
    daily_counts = (
        history.assign(Date=history["Timestamp"].dt.date)
        .groupby("Date")
        .size()
        .reset_index(name="Translations")
    )
    st.line_chart(daily_counts, x="Date", y="Translations")


def render_about_page() -> None:
    st.subheader("ℹ️ About")
    st.markdown(
        """
        This project demonstrates a complete AI-assisted language workflow:

        - Text translation with automatic language detection
        - Speech-to-text using microphone input
        - Text-to-speech audio generation
        - Local SQLite translation history
        - Downloadable TXT, MP3, and CSV outputs
        - Searchable analytics-ready history

        It is designed for final year projects, AI internship submissions, GitHub portfolios, and LinkedIn project showcases.
        """
    )


def main() -> None:
    initialize_database()
    inject_styles()
    render_header()
    page = render_sidebar()

    if page == "Translator":
        render_translator_page()
    elif page == "Voice Assistant":
        render_voice_page()
    elif page == "History":
        render_history_page()
    elif page == "Statistics":
        render_statistics_page()
    else:
        render_about_page()


if __name__ == "__main__":
    main()
