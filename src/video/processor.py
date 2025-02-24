import cv2
from googletrans import Translator
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, List, Union
from pytube import YouTube
import requests
from moviepy.editor import VideoFileClip  
import os 
from typing import Dict
import streamlit as st

import re
try:
    from moviepy.editor import VideoFileClip
except ImportError as e:
    raise ImportError(
        "Failed to import moviepy. Please install it with: pip install moviepy==1.0.3"
    ) from e
import os

class VideoProcessor:
    """Handles video processing operations including YouTube download, audio and frame extraction."""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.supported_formats = config['video']['supported_formats']
        self.youtube_patterns = config['video']['youtube']['url_patterns']
        
    def is_youtube_url(self, url: str) -> bool:
        """Check if the provided URL is a valid YouTube URL."""
        return any(pattern in url for pattern in self.youtube_patterns)
    
    def download_youtube_video(self, url: str) -> Path:
        """Download YouTube video and return the path to downloaded file."""
        try:
            if not self.is_youtube_url(url):
                raise ValueError("Invalid YouTube URL")
            
            output_dir = Path("data/raw/youtube")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            yt = YouTube(url)
            preferred_quality = self.config['video']['youtube']['preferred_quality']
            
            # Get the video stream with preferred quality or best available
            stream = (yt.streams
                     .filter(progressive=True, file_extension='mp4')
                     .order_by('resolution')
                     .desc()
                     .first())
            
            # Download the video
            video_path = output_dir / f"{yt.title}.mp4"
            stream.download(output_path=str(output_dir), filename=video_path.name)
            
            self.logger.info(f"Successfully downloaded YouTube video: {video_path}")
            return video_path
            
        except Exception as e:
            self.logger.error(f"Error downloading YouTube video: {str(e)}")
            raise
    
    def compress_video(self, input_path: Path, max_size_mb: int = 200) -> Path:
        """Compress video to target size while maintaining reasonable quality."""
        try:
            output_dir = Path("data/processed/compressed")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"compressed_{input_path.name}"
            
            # Get original video size in MB
            original_size = os.path.getsize(input_path) / (1024 * 1024)
            
            if original_size <= max_size_mb:
                return input_path
            
            # Calculate target bitrate (in bits per second)
            clip = VideoFileClip(str(input_path))
            duration = clip.duration
            target_size = max_size_mb * 8 * 1024 * 1024  # Convert MB to bits
            target_bitrate = int(target_size / duration)
            
            # Compress video using ffmpeg-python
            import ffmpeg
            
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(stream, str(output_path),
                                 video_bitrate=target_bitrate,
                                 audio_bitrate='128k',
                                 **{'vcodec': 'libx264',
                                    'acodec': 'aac',
                                    'preset': 'medium'})
            
            ffmpeg.run(stream, overwrite_output=True)
            
            clip.close()
            
            self.logger.info(f"Video compressed from {original_size:.1f}MB to "
                           f"{os.path.getsize(output_path)/(1024*1024):.1f}MB")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error compressing video: {str(e)}")
            raise
    
    def process_input(self, input_path: Union[str, Path], max_size_mb: int = 200) -> Path:
        """Process input which can be either a local file path or YouTube URL."""
        try:
            # If input is a URL, download the video first
            if isinstance(input_path, str) and self.is_youtube_url(input_path):
                video_path = self.download_youtube_video(input_path)
            else:
                video_path = Path(input_path)
            
            print(f"video_path , {video_path}")
            # Validate the video file
            #self.validate_video(video_path)
            
            # Compress video if needed
            compressed_path = self.compress_video(video_path, max_size_mb)
            
            return compressed_path
            
        except Exception as e:
            self.logger.error(f"Error processing input: {str(e)}")
            raise
    
    def validate_video(self, video_path: Path) -> bool:
        """Validate if the video format is supported and not corrupted."""
        try:
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            if video_path.suffix[1:] not in self.supported_formats:
                raise ValueError(f"Unsupported video format: {video_path.suffix}")
            
            # Check if video is readable using ffmpeg
            import ffmpeg
            probe = ffmpeg.probe(str(video_path))
            
            # Verify video stream exists
            video_streams = [stream for stream in probe['streams'] 
                            if stream['codec_type'] == 'video']
            if not video_streams:
                raise ValueError("No video stream found in file")
            
            self.logger.info(f"Video validated successfully: {video_path}")
            return True
            
        except ffmpeg.Error as e:
            self.logger.error(f"Video validation failed: {str(e)}")
            raise ValueError(f"Invalid or corrupted video file: {video_path}")
    
    def extract_audio(self, video_path: Path) -> Path:
        """Extract audio from video file."""
        try:
            
            # Convert to absolute paths
            video_path = Path(video_path).resolve()
            base_dir = Path().resolve()
            output_dir = base_dir / "data" / "processed" / "audio"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = output_dir / f"{video_path.stem}.wav"
            
            video = VideoFileClip(str(video_path))  

            # Extract the audio  
            audio = video.audio  

            # Write the audio to a file  
            audio.write_audiofile(str(output_path))

            
            self.logger.info(f"Audio extracted successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error extracting audio: {str(e)}")
            raise
    
    def extract_frames(self, video_path: Path) -> List[Path]:
        """Extract frames from video at specified intervals."""
        if not self.config['video']['frame_extraction']['enabled']:
            return []
            
        try:
            output_dir = Path("data/processed/frames") / video_path.stem
            output_dir.mkdir(parents=True, exist_ok=True)
            
            cap = cv2.VideoCapture(str(video_path))
            interval = self.config['video']['frame_extraction']['interval_seconds']
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps * interval)
            
            frame_paths = []
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_count % frame_interval == 0:
                    frame_path = output_dir / f"frame_{frame_count}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    frame_paths.append(frame_path)
                    
                frame_count += 1
            
            cap.release()
            self.logger.info(f"Extracted {len(frame_paths)} frames")
            return frame_paths
            
        except Exception as e:
            self.logger.error(f"Error extracting frames: {str(e)}")
            raise
    
    def extract_audio_segments(self, video_path, intervals):  
          
        try:
            # Load the video file  
            video = VideoFileClip(video_path)
            base_dir = Path().resolve()
            
            # Iterate over the specified intervals  
            for i, (start_time, end_time) in enumerate(intervals):  
                # Extract the audio segment  
                audio_segment = video.audio.subclip(start_time, end_time)  
                video_path = Path(video_path).resolve()
                # Define the output path  
                output_path = base_dir / "data" / "processed" / "audio" / f"{video_path.stem}"
                output_path.mkdir(parents=True, exist_ok=True)
                
                audio_path = output_path / f'audio_segment_{i}.mp3'  
                
                # Write the audio segment to a file  
                audio_segment.write_audiofile(audio_path)  
            return output_path
        except Exception as e:
            self.logger.error(f"Error extracting audio: {str(e)}")
            raise
    
    def transcribe(self, audio_path: Path) -> Dict[str, str]:
        """Transcribe audio file to text."""
        try:
            if self.model_name == "whisper":
                result = self.model.transcribe(str(audio_path))
                transcription = {
                    'text': result['text'],
                    'language': result.get('language', 'en')
                }
            else:
                # Implementation for Wav2Vec2 would go here
                raise NotImplementedError("Wav2Vec2 not yet implemented")
                
            self.logger.info(f"Transcription completed successfully")
            return transcription
            
        except Exception as e:
            self.logger.error(f"Error during transcription: {str(e)}")
            raise 