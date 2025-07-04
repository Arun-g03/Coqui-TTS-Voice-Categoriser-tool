"""
TTS Service Component
Handles TTS synthesis operations and model management.
"""

import os
import time
import threading
import traceback

class TTSService:
    """Service for handling TTS operations"""
    
    def __init__(self):
        self.current_model = None
        self.tts_engine = None
        
    def load_model(self, model_name, device="cpu"):
        """Load a TTS model"""
        try:
            from TTS.api import TTS
            
            # Determine device
            if device != "cpu":
                device = "cuda"
                
            # Load the model
            self.tts_engine = TTS(model_name=model_name)
            self.current_model = model_name
            
            return True, "Model loaded successfully"
            
        except Exception as e:
            return False, f"Error loading model: {e}"
            
    def synthesize_text(self, text, output_path, speaker=None, language=None, speed=1.0):
        """Synthesize text to audio"""
        if not self.tts_engine:
            return False, "No TTS engine loaded"
            
        try:
            # Prepare synthesis parameters
            kwargs = {
                'text': text,
                'file_path': output_path,
                'speed': speed
            }
            
            # Add speaker if provided
            if speaker:
                kwargs['speaker'] = speaker
                
            # Add language if provided
            if language:
                kwargs['language'] = language
                
            # Perform synthesis
            start_time = time.time()
            self.tts_engine.tts_to_file(**kwargs)
            synthesis_time = time.time() - start_time
            
            # Check if file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                file_size_mb = file_size / (1024 * 1024)
                
                return True, {
                    'synthesis_time': synthesis_time,
                    'file_size_mb': file_size_mb,
                    'synthesis_speed': file_size_mb / synthesis_time if synthesis_time > 0 else 0
                }
            else:
                return False, "Audio file was not created"
                
        except Exception as e:
            return False, f"Synthesis failed: {e}"
            
    def get_model_info(self, model_name):
        """Get information about a model"""
        try:
            from TTS.api import TTS
            
            # Create temporary TTS instance to get model info
            tts = TTS(model_name=model_name)
            
            info = {
                'speakers': getattr(tts, 'speakers', None),
                'languages': getattr(tts, 'languages', None),
                'model_name': model_name
            }
            
            return True, info
            
        except Exception as e:
            return False, f"Error getting model info: {e}"
            
    def list_available_models(self):
        """List all available TTS models"""
        try:
            from TTS.api import TTS
            
            # Get all available models
            available_models = TTS().list_models()
            
            # Filter for English and multilingual models
            english_models = [
                m for m in available_models 
                if m.startswith('tts_models/en/') or m.startswith('tts_models/multilingual/')
            ]
            
            return True, english_models
            
        except Exception as e:
            return False, f"Error listing models: {e}"
            
    def cleanup(self):
        """Clean up TTS resources"""
        self.tts_engine = None
        self.current_model = None 