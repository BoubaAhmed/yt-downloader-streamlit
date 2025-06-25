import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
import datetime
import os

st.set_page_config(page_title="YouTube Video Downloader", page_icon="🎬", layout="centered")

st.markdown("""
    <style>
    .main-card {
        background: linear-gradient(120deg, #f8fafc 60%, #e0e7ef 100%);
        border-radius: 20px;
        padding: 2.5rem 2.5rem 2rem 2.5rem;
        box-shadow: 0 6px 32px 0 rgba(60,60,120,0.12), 0 1.5px 4px 0 rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    .yt-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.3em;
        background: linear-gradient(90deg,#ff416c,#ff4b2b 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .yt-thumb {
        border-radius: 15px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.09);
        margin-bottom: 1rem;
    }
    .stats-card {
        display: flex;
        justify-content: space-between;
        gap: 2rem;
        margin-top: 1.3rem;
        margin-bottom: 1.7rem;
    }
    .stat {
        background: #fff;
        border-radius: 15px;
        padding: 0.8rem 1.3rem;
        box-shadow: 0 1px 6px rgba(60,60,120,0.09);
        text-align: center;
        min-width: 110px;
        font-size: 1rem;
    }
    .stat-title {
        color: #777;
        font-size: 0.89rem;
        margin-top: 0.2em;
    }
    .pill-btn {
        background: linear-gradient(90deg,#1e9bff,#0077ff 85%);
        border: none;
        color: #fff;
        border-radius: 50px;
        padding: 0.75rem 2.2rem;
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 1rem;
        box-shadow: 0 1.5px 8px 0 rgba(30,155,255,0.18);
        cursor: pointer;
        transition: all 0.18s;
        width: 100%;
    }
    .pill-btn:hover {
        background: linear-gradient(90deg,#0077ff,#1e9bff 90%);
        box-shadow: 0 6px 18px 0 rgba(30,155,255,0.30);
        transform: translateY(-2px) scale(1.01);
    }
    .desc-expander {
        background: #f4f7fa;
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
        color: #333;
        margin-top: 1em;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<div style="text-align:center"><span class="yt-title">🎬 YouTube Video Downloader</span><br><span style="color:#888;font-size:1.1rem;">Paste a YouTube URL and download your favorite content in style!</span></div>', unsafe_allow_html=True)
st.write("")

url = st.text_input(
    "YouTube Video URL",
    placeholder="Paste YouTube URL here...",
    help="Paste the full link, e.g. https://www.youtube.com/watch?v=...",
    label_visibility="collapsed"
)

if url:
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        # --- Video Details Card ---
        st.markdown(f'<img src="{yt.thumbnail_url}" class="yt-thumb" width="100%">', unsafe_allow_html=True)
        st.markdown(f'<div class="yt-title">{yt.title}</div>', unsafe_allow_html=True)
        
        # Stats
        stats_html = f"""
        <div class="stats-card">
            <div class="stat"><b>👁️ {yt.views:,}</b><div class="stat-title">Views</div></div>
            <div class="stat"><b>👤 {yt.author}</b><div class="stat-title">Channel</div></div>
            <div class="stat"><b>⏱️ {str(datetime.timedelta(seconds=yt.length))}</b><div class="stat-title">Duration</div></div>
            <div class="stat"><b>📅 {yt.publish_date.strftime('%b %d, %Y') if yt.publish_date else 'Unknown'}</b><div class="stat-title">Published</div></div>
        </div>
        """
        st.markdown(stats_html, unsafe_allow_html=True)

        # Description in expander
        with st.expander("📝 Show video description"):
            st.markdown(f'<div class="desc-expander">{yt.description if yt.description else "No description available."}</div>', unsafe_allow_html=True)

        st.divider()

        # --- Download Section ---
        st.markdown("### 🎞️ Download Video")
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        # if stream:
        #     st.markdown(f"**Highest Resolution Available:** <span style='color:#0077ff'>{stream.resolution}</span>", unsafe_allow_html=True)
        #     if st.button("⬇️ Download Video", key="dl", help="Download video in highest available resolution", type="primary"):
        #         with st.spinner("Downloading..."):
        #             stream.download()
        #         st.success("Download completed!")
        # else:
        #     st.error("No downloadable video streams found.")

        if stream:
            st.markdown(f"**Highest Resolution Available:** <span style='color:#0077ff'>{stream.resolution}</span>", unsafe_allow_html=True)
            if st.button("⬇️ Prepare Download", key="dl", help="Prepare video for downloading", type="primary"):
                with st.spinner("Preparing video..."):
                    filename = stream.default_filename
                    stream.download(filename=filename)
                    with open(filename, "rb") as f:
                        video_bytes = f.read()
                    st.success("Download ready! Click below to save to your device.")
                    st.download_button(
                        label="Download Video File",
                        data=video_bytes,
                        file_name=filename,
                        mime="video/mp4"
                    )
                    os.remove(filename)
        else:
            st.error("No downloadable video streams found.")

        st.divider()
        # Optionally: Add more download options (audio only, select resolution, etc.)

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Please check that the URL is correct and the video is public.")

st.markdown('</div>', unsafe_allow_html=True)