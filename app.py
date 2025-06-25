import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
import datetime

st.set_page_config(page_title="YouTube Video Downloader", page_icon="🎬", layout="centered")

st.markdown(
    """
    <style>
    .big-font {
        font-size:24px !important;
        font-weight: bold;
    }
    .subtitle {
        color: #888888;
    }
    .stButton>button {
        background-color: #ff3333;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown('<div class="big-font">🎬 YouTube Video Downloader</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Paste a YouTube URL and search for details, then download in your favorite quality!</div>', unsafe_allow_html=True)
st.write("")

with st.form("yt_form"):
    url = st.text_input("YouTube Video URL", help="Paste the full link, e.g. https://www.youtube.com/watch?v=...")
    search = st.form_submit_button("🔍 Search Video")

if url and search:
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        st.success("Video found! Details below:")
        # Display video details
        col1, col2 = st.columns([1,2])
        with col1:
            st.image(yt.thumbnail_url, width=240, caption="Video Thumbnail")
        with col2:
            st.markdown(
                f"""
                **Title:** {yt.title}  
                **Channel:** {yt.author}  
                **Published:** {yt.publish_date.strftime('%Y-%m-%d') if yt.publish_date else 'Unknown'}  
                **Length:** {str(datetime.timedelta(seconds=yt.length)) if yt.length else 'Unknown'}  
                **Views:** {yt.views:,}  
                **Description:**  
                <div style='max-height:80px;overflow:auto;background:#fafafa;border-radius:4px;padding:6px;'>{yt.description[:400] + ("..." if len(yt.description) > 400 else "")}</div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        st.markdown("#### Choose a quality to download 🎥")
        mp4_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        resolutions = [f"{s.resolution} ({round(s.filesize / (1024*1024), 2)} MB)" for s in mp4_streams if s.resolution]
        if not resolutions:
            st.error("No downloadable video streams found.")
        else:
            selected = st.selectbox("Available Resolutions:", options=resolutions)
            stream = list(mp4_streams)[resolutions.index(selected)]
            if st.button("⬇️ Download Video"):
                with st.spinner("Downloading..."):
                    stream.download()
                st.success("✅ Download completed! Check your folder.")

        st.divider()
        st.markdown("##### Want audio only? (MP3 extract)")
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        audio_options = [f"{a.abr} ({round(a.filesize / (1024*1024), 2)} MB)" for a in audio_streams if a.abr]
        if audio_options:
            selected_audio = st.selectbox("Available Audio Qualities:", options=audio_options, key="audio")
            audio_stream = list(audio_streams)[audio_options.index(selected_audio)]
            if st.button("🎵 Download Audio (MP4A)"):
                with st.spinner("Downloading Audio..."):
                    audio_stream.download(filename_prefix="AUDIO_")
                st.success("✅ Audio download completed! Check your folder.")
        else:
            st.info("No audio-only streams available.")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Please check that the URL is correct, the video is public, and try again.")