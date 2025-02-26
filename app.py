import base64
import requests
import streamlit as st
import yaml
from pathlib import Path
from src.video.processor import VideoProcessor
import tempfile
import os
import humanize
from PIL import Image 
from fpdf import FPDF
import json
import subprocess
import PyPDF2

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
        frames = None
        
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
                print(f"temp_path, {temp_path}")
                try:
                    with st.spinner("Processing video..."):
                        # Compress video if needed
                        video_path = Path(video_processor.process_input(temp_path, max_size_mb=max_size))
                        print(f"video_path, {video_path}")
                        st.info(f"Hello, {temp_path}!")
                        
                        if video_path != temp_path:
                            compressed_size = os.path.getsize(video_path) / (1024 * 1024)
                            st.success(f"Video compressed from {file_size:.1f}MB to {compressed_size:.1f}MB")
                        
                    # Show video preview
                    st.video(str(video_path))
                    
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
        
    
    with col2:
        
        if video_path:
            # Show processing status and preview
            st.info("Video loaded and ready for processing!")
            if not video_path.exists():
                st.error(f"Video file not found at: {video_path}")
                st.stop()
            
            frames_dir = Path('data/processed/frames') / video_path.stem
            frames_dir.mkdir(parents=True, exist_ok=True)
            frame_data = video_processor.directory_has_files(frames_dir)
            st.info(f"frame_data, {frame_data}")
            if not frame_data:
                try: 
                    with st.spinner("Extracting Frames..."):
                        frames = video_processor.extract_frames(video_path)
                    
                    st.subheader("Preview")
                    st.subheader("Key Frames")
                    for i, frame in enumerate(frames[:3]):  # Show first 3 frames
                        st.image(str(frame), caption=f"Frame {i+1}")
                    st.success("Frames extracted successfully!")
                except Exception as e:
                    st.error(f"Error extracting frames: {str(e)}")
            
            
            st.info(f"{video_processor.directory_has_files(frames_dir)}")
            if video_processor.directory_has_files(frames_dir):
                with st.spinner("Extracting audio..."):
                    audio_path = video_processor.extract_audio(video_path)
                # if audio_path:
                #     audio_text= video_processor.transcribe_audio(audio_path)
                #     st.info(f"audio_text, {audio_text}")
                st.info(f"audio_path, {audio_path}")
                # Language selection
                target_language = st.selectbox(
                    "Select output language",
                    config['nlp']['translation']['supported_languages'],
                    format_func=lambda x: {'english': 'English', 'spanish': 'Spanish', 
                                        'french': 'French', 'chinese': 'Chinese', 
                                        'german': 'German'}[x]
                )
                st.info(f"Target lang, {target_language}")
                # Output format selection
                output_format = st.selectbox(
                    "Select output format",
                    ["PDF", "HTML"],
                    help="Choose the format for your user guide"
                )
                if st.button("🔄 Generate User Guide"):
                    try:
                        with st.spinner("Generating PDF..."):
                            # Show progress
                            progress_bar = st.progress(0)
                            
                            # Show extracted frames (if any)
                            
                            
                            entries = os.listdir(frames_dir)  
  
                            # Sort by modification time  
                            sorted_entries_by_mtime = sorted(entries, key=lambda entry: os.path.getmtime(os.path.join(frames_dir, entry)))

                            url = "https://ngc-genai-proxy-stage.pwcinternal.com/chat/completions"  
                            headers = {'Authorization': 'Bearer sk-Tc05RYjXNEaHEiCGpcmVqg'}
                            # Loop through all files in the directory 
                            # image_arr = []
                            image_arr = []
                            imagepath_arr = [] 
                            Path(f"data/pdf/{video_path.stem}").mkdir(parents=True, exist_ok=True)
                            # Create an instance of FPDF class  
                            pdf = FPDF()  
                            
                            # Add a page to the PDF  
                            pdf.add_page()  
                            
                            # Save the PDF with a name (e.g., blank.pdf)  
                            pdf.output(f"data/pdf/{video_path.stem}/user_guide.pdf")

                            for filename in sorted_entries_by_mtime:  
                                # Construct full file path  
                                file_path = os.path.join(frames_dir, filename)  

                                # Check if it is a file and has an image extension  
                                if os.path.isfile(file_path) and filename.lower().endswith(('.jpg')):  
                                    try:  
                                        # Open the image file  
                                        with open(f"{file_path}", 'rb') as image_file:
                            
                                            base64_encoded_image = base64.b64encode(image_file.read())
                                            base64_image_string = base64_encoded_image.decode('utf-8')
                                            image_arr.append(base64_image_string)
                                            imagepath_arr.append(file_path)
                                        print(f"Processing image: {file_path}")  

                                    except Exception as e:  
                                        print(f"Could not open {filename}: {e}")
                            # Generate PDF using OpenAI
                            pdf_path = f'data/pdf/{video_path.stem}/user_guide.pdf'
                            separator = ', '
                            #transcription = "Hi, this is Tom from the M&A Path team. I'm showing you how to create a project in M&A Path. Firstly, you click on the new project button, which brings up a modal. You enter the information of including project name, engagement lead and other fields. And when complete, you can click the Create button. "
                            st.info(f"{separator.join(imagepath_arr)}")
                            pdf_contents = [{
                                                "type": "text",
                                                "text": f"Remove similar looking images from the images list {separator.join(imagepath_arr)} and consider contents of one of the duplicate images and unique images and return code that I can use for my python fpdf package that I can pass to the package to generate a well-styled multi page pdf in {target_language}?  I want the code to include an detail explanation of each of the images represents and I want to include each image in the pdf as well and the content . The pdf format must be same as image data/template/sample_template.jpg. Images and contents do not overlap. I don't want any extra detail in your response.  I literally want to be able to pass your response into my fpdf package. the generated pdf name will be user_guide.pdf and the file path will be {pdf_path}. PDF should have a header and footer. The Project name is M&A path. The Heading in each page will be in red and boldand the description of the image will be in black. each page will have only one image and details description of the image. Add the line # -*- coding: iso-8859-1 -*- at the top of the pdf code."
                                            }]
                            for image_data in image_arr:
                                pdf_content = {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/gif;base64,{str(image_data)}"
                                            }
                                        }
                                pdf_contents.append(pdf_content)

                            data_pdf = {
                                    "messages": [
                                        {
                                            "role": "user",
                                            "content": pdf_contents

                                        }
                                    ],
                                    "model": "azure.gpt-4o"
                                } 

                            response = requests.post(url, headers=headers, json=data_pdf, verify=False)
                            data_resp = json.loads(response.content)
                            #st.info(data_resp['choices'][0]['message']['content'].replace('python\n', ''))


                            code = data_resp['choices'][0]['message']['content'].replace('python\n', '').replace('```','')

                            with open(f"data/pdf/{video_path.stem}/generated_code.py", "w") as file:
                                file.write(code)
                            # Step 2: Execute the code using subprocess
                            subprocess.run(["venv/Scripts/python.exe", f"data/pdf/{video_path.stem}/generated_code.py"])
                            
                            #Inform the user
                            print("PDF generated successfully") 
                            progress_bar.progress(75)
                            st.success(f"PDF created at {pdf_path}")  

                            # Read the PDF file content  
                            with open(pdf_path, 'rb') as file:  
                                pdf_data = file.read()  

                            st.download_button(
                                label="⬇️ Download User Guide",
                                data=pdf_data,
                                file_name=f"user_guide_{target_language}.{output_format.lower()}",
                                mime="application/pdf" if output_format == "PDF" else "text/html"
                            )
                            progress_bar.progress(100)
                        
                    except Exception as e:
                        st.error(f"Error generating guide: {str(e)}")
                

if __name__ == "__main__":
    main()
