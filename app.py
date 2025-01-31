import streamlit as st
import yaml
from pathlib import Path
from src.video.processor import VideoProcessor
from src.audio.transcriber import Transcriber
import tempfile
import os
import humanize

def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    st.set_page_config(page_title="Video to User Guide Converter", layout="wide")
    
    # Add custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🎥 Video to User Guide Converter")
    st.markdown("---")
    
    config = load_config()
    video_processor = VideoProcessor(config)
    transcriber = Transcriber(config)
    
    # Create two columns for input and preview
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Input Options")
        
        # Input selection
        input_type = st.radio(
            "Choose input type:",
            ["Upload Video", "YouTube URL"],
            help="Select whether to upload a video file or provide a YouTube URL"
        )
        
        video_path = None
        
        # Add compression settings
        max_size = st.slider(
            "Maximum video size (MB)",
            min_value=50,
            max_value=500,
            value=200,
            help="Videos larger than this will be automatically compressed"
        )
        
        if input_type == "Upload Video":
            uploaded_file = st.file_uploader(
                "Upload a video file",
                type=config['video']['supported_formats'],
                help=f"Supported formats: {', '.join(config['video']['supported_formats'])}"
            )
            if uploaded_file:
                file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Size in MB
                st.info(f"Original file size: {humanize.naturalsize(len(uploaded_file.getvalue()))}")
                
                # Save uploaded file temporarily
                temp_path = Path("data/raw") / uploaded_file.name
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path.write_bytes(uploaded_file.read())
                
                try:
                    with st.spinner("Processing video..."):
                        # Compress video if needed
                        video_path = video_processor.process_input(temp_path, max_size_mb=max_size)
                        
                        if video_path != temp_path:
                            compressed_size = os.path.getsize(video_path) / (1024 * 1024)
                            st.success(f"Video compressed from {file_size:.1f}MB to {compressed_size:.1f}MB")
                        
                    # Show video preview
                    st.video(video_path)
                    
                except Exception as e:
                    st.error(f"Error processing video: {str(e)}")
                    if temp_path.exists():
                        os.unlink(temp_path)
                
        else:  # YouTube URL
            youtube_url = st.text_input(
                "Enter YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Paste the URL of the YouTube video you want to process"
            )
            if youtube_url and st.button("📥 Download Video"):
                try:
                    with st.spinner("Downloading YouTube video..."):
                        video_path = video_processor.process_input(youtube_url)
                    st.success("Video downloaded successfully!")
                    # Show video preview
                    st.video(youtube_url)
                except Exception as e:
                    st.error(f"Error downloading video: {str(e)}")
        
        if video_path:
            # Add this check before processing
            if not video_path.exists():
                st.error(f"Video file not found at: {video_path}")
                st.stop()
            
            st.markdown("---")
            st.subheader("Output Options")
            
            # Language selection
            target_language = st.selectbox(
                "Select output language",
                config['nlp']['translation']['supported_languages'],
                format_func=lambda x: {'en': 'English', 'es': 'Spanish', 
                                     'fr': 'French', 'zh': 'Chinese', 
                                     'de': 'German'}[x]
            )
            
            # Output format selection
            output_format = st.selectbox(
                "Select output format",
                ["PDF", "HTML"],
                help="Choose the format for your user guide"
            )
            
            if st.button("🔄 Generate User Guide"):
                try:
                    with st.spinner("Processing video..."):
                        # Show progress
                        progress_bar = st.progress(0)
                        
                        # Extract audio
                        st.write("Extracting audio...")
                        try:
                            audio_path = video_processor.extract_audio(video_path)
                            st.success(f"Audio extracted to: {audio_path}")
                            progress_bar.progress(25)
                        except Exception as e:
                            st.error(f"Error extracting audio: {str(e)}")
                            st.stop()
                        
                        # Transcribe audio
                        st.write("Transcribing content...")
                        try:
                            transcription = transcriber.transcribe(audio_path)
                            st.success("Transcription completed")
                            progress_bar.progress(50)
                        except Exception as e:
                            st.error(f"Error during transcription: {str(e)}")
                            st.stop()
                        
                        st.write("Generating summary...")
                        progress_bar.progress(75)
                        
                        st.write("Creating user guide...")
                        progress_bar.progress(100)
                        
                        st.success("User guide generated successfully!")
                        
                        # Add download button (mock for now)
                        st.download_button(
                            label="⬇️ Download User Guide",
                            data=b"Sample guide content",
                            file_name=f"user_guide_{target_language}.{output_format.lower()}",
                            mime="application/pdf" if output_format == "PDF" else "text/html"
                        )
                        
                except Exception as e:
                    st.error(f"Error generating guide: {str(e)}")
                finally:
                    # Cleanup temporary files
                    if video_path and video_path.exists():
                        try:
                            os.unlink(video_path)
                        except Exception as e:
                            st.warning(f"Could not remove temporary file: {str(e)}")
    
    with col2:
        st.subheader("Preview")
        if video_path:
            # Show processing status and preview
            st.info("Video loaded and ready for processing!")
            
            # Show extracted frames (if any)
            frames = video_processor.extract_frames(video_path)
            if frames:
                st.subheader("Key Frames")
                for i, frame in enumerate(frames[:3]):  # Show first 3 frames
                    st.image(str(frame), caption=f"Frame {i+1}")

if __name__ == "__main__":
    main()
