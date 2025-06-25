import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
import datetime

st.set_page_config(page_title="YouTube Video Downloader", page_icon="🎬", layout="centered")

st.markdown(
    """
    <style>
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #b0b0b0;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        background-color: #ff3333;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .url-input {
        background: rgba(255, 255, 255, 0.1);
        border: none;
        border-radius: 12px;
        padding: 15px;
        color: white;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .url-input:focus {
        outline: none;
        box-shadow: 0 0 0 2px #ff416c;
    }
    
    /* Button styling */
    .search-btn {
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-bottom: 1rem;
    }
    
    .search-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 65, 108, 0.4);
    }
    
    .download-btn {
        background: linear-gradient(90deg, #1e9bff, #0077ff);
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 1rem;
    }
    
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(30, 155, 255, 0.4);
    }
    
    /* Video details styling */
    .details-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 0.5rem;
        margin-bottom: 0.25rem;
        backdrop-filter: blur(10px);
    }
    
    .thumbnail {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }
    
    /* Progress bar styling */
    .progress-container {
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown('<div class="big-font title">🎬 YouTube Video Downloader</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Paste a YouTube URL and search for details, then download in your favorite quality!</div>', unsafe_allow_html=True)
st.write("")

with st.form("yt_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input(
            "YouTube URL",
            placeholder="Paste YouTube URL here...",
            key="url",
            help="Paste the full link, e.g. https://www.youtube.com/watch?v=...",
            label_visibility="collapsed"
        )
    with col2:
        search = st.form_submit_button("🔍 Search Video", use_container_width=True)
        
    # Session state initialization
    if 'progress' not in st.session_state:
        st.session_state.progress = 0
    if 'downloaded' not in st.session_state:
        st.session_state.downloaded = False

if url and search:
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        # Display video details
        st.markdown('<div class="details-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown('<div class="thumbnail">', unsafe_allow_html=True)
            st.image(yt.thumbnail_url, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Quick stats
            st.markdown(f"**⏱️ Duration:** {str(datetime.timedelta(seconds=yt.length))}")
            st.markdown(f"**👁️ Views:** {yt.views:,}")
            st.markdown(f"**📅 Published:** {yt.publish_date.strftime('%b %d, %Y')}")
            
        with col2:
            st.markdown(f"### {yt.title}")
            st.markdown(f"**👤 Channel:** {yt.author}")
            
            # Show description with expander
            with st.expander("📝 Description"):
                st.write(yt.description)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close details-card
    
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