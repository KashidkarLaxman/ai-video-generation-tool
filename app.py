import os

import streamlit as st

from config import TEMP_DIR, ensure_directories
from core.news_pipeline import generate_news_script, render_news_video
from core.pipeline import create_video


st.set_page_config(page_title="AI Video Tool", page_icon="🎬")
st.title("AI Video Tool")

mode = st.radio("Source", ["From Article URL", "From Topic"], horizontal=True)

if mode == "From Article URL":
    orientation = st.radio("Orientation", ["Landscape", "Portrait"], horizontal=True, key="news_orientation")
    target_duration = st.slider(
        "Target video length (seconds)", min_value=15, max_value=120, value=45, step=15, key="news_duration"
    )
    url = st.text_input("Article URL", placeholder="https://example.com/news-article")

    if st.button("Step 1: Generate script", type="primary", disabled=not url):
        with st.spinner("Scraping article and writing script..."):
            try:
                script, article_images = generate_news_script(url, target_duration_seconds=target_duration)
            except Exception as exc:
                st.error(f"Script generation failed: {exc}")
            else:
                st.session_state.news_script = script
                st.session_state.news_article_images = article_images
                st.session_state.news_overrides = {}
                st.session_state.news_orientation_value = orientation.lower()

    if "news_script" in st.session_state:
        script = st.session_state.news_script
        st.subheader(script.title)
        st.caption(
            "Review each scene below. Edit the narration if you want, or upload your own "
            "image/video to use instead of the automatic search - then render when ready."
        )

        for scene in script.scenes:
            with st.expander(f"Scene {scene.scene}: {scene.narration[:60]}", expanded=False):
                edited_text = st.text_area("Narration", value=scene.narration, key=f"narration_{scene.scene}")
                scene.narration = edited_text

                st.caption(f"Auto search: {scene.visual_prompt}")

                uploaded = st.file_uploader(
                    "Override with your own image or video (optional)",
                    type=["jpg", "jpeg", "png", "webp", "mp4", "mov", "m4v"],
                    key=f"upload_{scene.scene}",
                )
                if uploaded is not None:
                    ensure_directories()
                    override_path = os.path.join(TEMP_DIR, f"override_{scene.scene}_{uploaded.name}")
                    with open(override_path, "wb") as file:
                        file.write(uploaded.getbuffer())
                    st.session_state.news_overrides[scene.scene] = override_path
                    st.success("This scene will use your uploaded file.")
                elif scene.scene in st.session_state.news_overrides:
                    st.info("Using a previously uploaded file for this scene.")

        if st.button("Step 2: Render video", type="primary"):
            with st.spinner("Fetching visuals, generating voice, and rendering... this takes a few minutes."):
                try:
                    output_path = render_news_video(
                        script,
                        st.session_state.news_article_images,
                        orientation=st.session_state.news_orientation_value,
                        overrides=st.session_state.news_overrides,
                    )
                except Exception as exc:
                    st.error(f"Render failed: {exc}")
                else:
                    st.success("Done!")
                    st.video(output_path)

else:
    orientation = st.radio("Orientation", ["Landscape", "Portrait"], horizontal=True, key="topic_orientation")
    target_duration = st.slider(
        "Target video length (seconds)", min_value=15, max_value=120, value=45, step=15, key="topic_duration"
    )
    topic = st.text_input("Topic", placeholder="e.g. the benefits of morning exercise")
    generate = st.button("Generate video", type="primary", disabled=not topic)

    if generate:
        with st.spinner("Writing script, fetching visuals, and rendering... this takes a minute or two."):
            try:
                output_path = create_video(
                    topic, orientation=orientation.lower(), target_duration_seconds=target_duration
                )
            except Exception as exc:
                st.error(f"Video generation failed: {exc}")
            else:
                st.success("Done!")
                st.video(output_path)
