import logging
from pathlib import Path
from typing import Dict
import sys
from googletrans import Translator

# Add detailed error checking
def check_torch():
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"PyTorch installation location: {torch.__file__}")
        return True
    except ImportError as e:
        print(f"Failed to import PyTorch: {e}")
        return False

def check_whisper():
    try:
        import whisper
        print(f"Whisper installation location: {whisper.__file__}")
        return True
    except ImportError as e:
        print(f"Failed to import Whisper: {e}")
        return False

# Run checks before class definition
print("Python version:", sys.version)
print("\nChecking dependencies:")
torch_ok = check_torch()
whisper_ok = check_whisper()

if not all([torch_ok, whisper_ok]):
    raise ImportError("Required dependencies are not properly installed")

import torch
import whisper

class Transcriber:
    """Handles speech-to-text conversion using Whisper or Wav2Vec2."""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model_name = config['audio']['model']
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Initialize the model
        self.model = self._load_model()
        
    def _load_model(self):
        """Load the specified speech-to-text model."""
        try:
            if self.model_name == "whisper":
                print("Loading Whisper model...")
                model = whisper.load_model("base", device=self.device)
                print("Whisper model loaded successfully")
            else:
                raise NotImplementedError("Wav2Vec2 not yet implemented")
                
            self.logger.info(f"Loaded {self.model_name} model successfully on {self.device}")
            return model
            
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            print(f"Detailed error: {str(e)}")
            raise
            
    def transcribe(self, target_language, audio_path: Path) -> Dict[str, str]:
        """Transcribe audio file to text."""
        try:
            translator = Translator()  
            if self.model_name == "whisper":
                result = self.model.transcribe(str(audio_path))
                translation = translator.translate(result['text'], src='en', dest=target_language)
                transcription = {
                    'text': translation.text,
                    'language': result.get('language', target_language)
                }
            else:
                # Implementation for Wav2Vec2 would go here
                raise NotImplementedError("Wav2Vec2 not yet implemented")
                
            self.logger.info(f"Transcription completed successfully")
            return translation.text
            
        except Exception as e:
            self.logger.error(f"Error during transcription: {str(e)}")
            raise 