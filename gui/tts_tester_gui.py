"""
TTS Tester GUI - Main Application Window
Handles the main application interface and coordinates all components.
"""

import os
import sys
import threading
import traceback
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import json
import torch

from .components.speaker_tag_dialog import SpeakerTagDialog
from .components.theme_manager import ThemeManager
from .services.tts_service import TTSService
from .services.speaker_service import SpeakerService

# Constants
AUDIO_OUT_PATH_COQUI = os.path.join(os.path.dirname(__file__), '..', 'coqui_test.wav')
DEFAULT_TEXT = "The quick brown fox jumps over the lazy dog, yet every now and then, peculiar voices echo through the canyon. Hyperbolic statements and subtle sarcasm make linguistics uniquely complex. She sells sea shells by the seashore, while he thoroughly thought through the theory of thermodynamics. Does the artificial speaker articulate acronyms like NASA, AI, and GPU naturally? Consider how rhythm, emphasis, and intonation change with punctuation — like commas, ellipses... or dashes. Ultimately, the true test is whether it sounds convincingly human."

class TTSTesterGUI(tk.Tk):
    """Main TTS Tester GUI Application"""
    
    def __init__(self):
        super().__init__()
        self.title("TTS Tester GUI")
        self.geometry("700x700")
        self.resizable(False, False)
        
        # Initialize services
        self.tts_service = TTSService()
        # Initialize speaker service with correct file path
        speaker_tags_file = os.path.join(os.path.dirname(__file__), '..', 'speaker_tags.json')
        self.speaker_service = SpeakerService(speaker_tags_file)
        self.theme_manager = ThemeManager()
        
        # Apply dark theme
        self.theme_manager.apply_dark_theme(self)
        
        # Initialize state
        self.coqui_models = []
        self.coqui_speakers = []
        self.coqui_languages = []
        self.selected_model = None
        self.selected_speaker = None
        self.selected_language = None
        self.tts_engine = None
        self.is_playing = False
        
        # Load data
        self.speaker_service.load_speaker_tags()
        
        # Create UI
        self.create_widgets()
        
        # Debug: Log loaded speaker tags (after widgets are created)
        debug_info = self.speaker_service.debug_info()
        self.log(f"📁 Speaker tags file: {debug_info['tags_file']}")
        self.log(f"✅ File exists: {debug_info['file_exists']}")
        self.log(f"📊 Models with tags: {debug_info['models_count']}")
        self.log(f"🎤 Total speakers: {debug_info['total_speakers']}")
        self.log(f"🏷️  Total tags: {debug_info['total_tags']}")
        self.log(f"📦 Downloaded models: {len(debug_info['downloaded_models'])}")
        self.log(f"📋 Available models: {len(debug_info['available_models'])}")
        self.log(f"🏷️  Tag definitions: {debug_info['tag_definitions_count']}")
        if debug_info['models']:
            self.log(f"📋 Models with tags: {', '.join(debug_info['models'])}")
        if debug_info['downloaded_models']:
            self.log(f"✅ Downloaded: {', '.join(debug_info['downloaded_models'])}")
        if debug_info['available_tags']:
            self.log(f"🏷️  Available tags: {', '.join(debug_info['available_tags'])}")
        
        # Load models
        self.load_coqui_models()
        
        # Print GPU status
        print(torch.cuda.is_available())
        print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU")

    def create_widgets(self):
        """Create all GUI widgets"""
        # Engine selection
        engine_frame = ttk.Frame(self)
        engine_frame.pack(pady=10, fill='x')
        ttk.Label(engine_frame, text="TTS Engine:").pack(side='left', padx=5)
        self.engine_var = tk.StringVar(value="Coqui TTS")
        self.engine_menu = ttk.Combobox(engine_frame, textvariable=self.engine_var, state="readonly",
                                        values=["Coqui TTS", "Edge TTS (coming soon)", "pyttsx3 (coming soon)"])
        self.engine_menu.pack(side='left', padx=5)
        self.engine_menu.bind('<<ComboboxSelected>>', self.on_engine_change)

        # GPU Device selection
        gpu_frame = ttk.Frame(self)
        gpu_frame.pack(pady=5, fill='x')
        ttk.Label(gpu_frame, text="GPU Device:").pack(side='left', padx=5)
        self.gpu_var = tk.StringVar(value="CPU")
        self.gpu_menu = ttk.Combobox(gpu_frame, textvariable=self.gpu_var, state="readonly")
        self.gpu_menu.pack(side='left', padx=5)
        self.load_gpu_devices()

        # Model selection (Coqui)
        model_frame = ttk.Frame(self)
        model_frame.pack(pady=5, fill='x')
        ttk.Label(model_frame, text="Coqui Model:").pack(side='left', padx=5)
        self.model_var = tk.StringVar()
        self.model_menu = ttk.Combobox(model_frame, textvariable=self.model_var, state="readonly")
        self.model_menu.pack(side='left', padx=5, fill='x', expand=True)
        self.model_menu.bind('<<ComboboxSelected>>', self.on_model_change)
        
        # Model management button
        self.model_btn = ttk.Button(model_frame, text="Manage Models", command=self.open_model_management)
        self.model_btn.pack(side='right', padx=5)

        # Speaker selection (Coqui)
        speaker_frame = ttk.Frame(self)
        speaker_frame.pack(pady=5, fill='x')
        ttk.Label(speaker_frame, text="Speaker:").pack(side='left', padx=5)
        self.speaker_var = tk.StringVar()
        self.speaker_menu = ttk.Combobox(speaker_frame, textvariable=self.speaker_var, state="readonly")
        self.speaker_menu.pack(side='left', padx=5, fill='x', expand=True)
        self.speaker_menu.bind('<<ComboboxSelected>>', self.on_speaker_change)
        
        # Speaker tag management button
        self.tag_btn = ttk.Button(speaker_frame, text="Manage Tags", command=self.open_speaker_tag_dialog)
        self.tag_btn.pack(side='right', padx=5)
        
        # Refresh speakers button
        self.refresh_speakers_btn = ttk.Button(speaker_frame, text="🔄 Refresh", command=self.refresh_speaker_list)
        self.refresh_speakers_btn.pack(side='right', padx=5)
        
        # Speaker filter toggle
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=2, fill='x')
        self.show_untagged_only = tk.BooleanVar()
        self.filter_checkbox = ttk.Checkbutton(filter_frame, text="Show only untagged speakers", 
                                              variable=self.show_untagged_only, 
                                              command=self.on_filter_toggle)
        self.filter_checkbox.pack(side='left', padx=5)

        # Language selection (Coqui)
        language_frame = ttk.Frame(self)
        language_frame.pack(pady=5, fill='x')
        ttk.Label(language_frame, text="Language:").pack(side='left', padx=5)
        self.language_var = tk.StringVar()
        self.language_menu = ttk.Combobox(language_frame, textvariable=self.language_var, state="readonly")
        self.language_menu.pack(side='left', padx=5, fill='x', expand=True)

        # Speed
        speed_frame = ttk.Frame(self)
        speed_frame.pack(pady=5, fill='x')
        ttk.Label(speed_frame, text="Speed:").pack(side='left', padx=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_entry = ttk.Entry(speed_frame, textvariable=self.speed_var, width=6)
        self.speed_entry.pack(side='left', padx=5)

        # Text input
        text_frame = ttk.Frame(self)
        text_frame.pack(pady=10, fill='x')
        
        # Text input header with reset button
        text_header_frame = ttk.Frame(text_frame)
        text_header_frame.pack(fill='x', padx=5)
        ttk.Label(text_header_frame, text="Input Text:").pack(side='left')
        self.reset_text_btn = ttk.Button(text_header_frame, text="Reset to Default", command=self.reset_text_to_default)
        self.reset_text_btn.pack(side='right')
        
        self.text_input = scrolledtext.ScrolledText(text_frame, height=7, wrap='word',
                                                   bg=self.theme_manager.colors['entry_bg'],
                                                   fg=self.theme_manager.colors['entry_fg'],
                                                   insertbackground=self.theme_manager.colors['fg'],
                                                   selectbackground=self.theme_manager.colors['listbox_select_bg'],
                                                   selectforeground=self.theme_manager.colors['listbox_select_fg'])
        self.text_input.pack(fill='x', padx=5)
        self.text_input.insert('1.0', DEFAULT_TEXT)

        # Synthesize and Play buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        self.synth_btn = ttk.Button(btn_frame, text="Synthesize", command=self.synthesize)
        self.synth_btn.pack(side='left', padx=10)
        self.play_btn = ttk.Button(btn_frame, text="Play", command=self.play_audio)
        self.play_btn.pack(side='left', padx=10)
        self.play_btn.config(state='disabled')
        self.is_playing = False

        # Quick speaker tagging frame
        quick_tag_frame = ttk.LabelFrame(self, text="Speaker Tagging")
        quick_tag_frame.pack(pady=5, fill='x', padx=10)
        
        # Current speaker info
        current_speaker_frame = ttk.Frame(quick_tag_frame)
        current_speaker_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(current_speaker_frame, text="Current Speaker:").pack(side='left', padx=5)
        self.current_speaker_label = ttk.Label(current_speaker_frame, text="None", font=('Arial', 9, 'bold'))
        self.current_speaker_label.pack(side='left', padx=5)
        
        # Tags status
        tags_status_frame = ttk.Frame(quick_tag_frame)
        tags_status_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(tags_status_frame, text="Current Tags:").pack(side='left', padx=5)
        self.tags_status_label = ttk.Label(tags_status_frame, text="No tags", font=('Arial', 9, 'italic'))
        self.tags_status_label.pack(side='left', padx=5)
        
        # Quick tag assignment
        quick_tag_controls = ttk.Frame(quick_tag_frame)
        quick_tag_controls.pack(fill='x', padx=5, pady=5)
        ttk.Label(quick_tag_controls, text="Add Tag:").pack(side='left', padx=5)
        self.quick_tag_var = tk.StringVar()
        self.quick_tag_menu = ttk.Combobox(quick_tag_controls, textvariable=self.quick_tag_var, width=20)
        self.quick_tag_menu.pack(side='left', padx=5)
        self.quick_tag_btn = ttk.Button(quick_tag_controls, text="Add Tag", command=self.quick_add_tag)
        self.quick_tag_btn.pack(side='left', padx=5)
        self.remove_tag_btn = ttk.Button(quick_tag_controls, text="Remove Tag", command=self.quick_remove_tag)
        self.remove_tag_btn.pack(side='left', padx=5)

        # Log/output area
        log_frame = ttk.LabelFrame(self, text="Log / Output")
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.log_area = scrolledtext.ScrolledText(log_frame, height=12, wrap='word', state='disabled',
                                                 bg=self.theme_manager.colors['entry_bg'],
                                                 fg=self.theme_manager.colors['entry_fg'],
                                                 insertbackground=self.theme_manager.colors['fg'],
                                                 selectbackground=self.theme_manager.colors['listbox_select_bg'],
                                                 selectforeground=self.theme_manager.colors['listbox_select_fg'])
        self.log_area.pack(fill='both', expand=True)
        
        # Configure text tags for colored logging
        self.log_area.tag_configure('success', foreground='#4ade80')  # Green
        self.log_area.tag_configure('error', foreground='#f87171')    # Red
        self.log_area.tag_configure('timing', foreground='#fbbf24')   # Yellow
        self.log_area.tag_configure('info', foreground='#60a5fa')     # Blue

    def load_gpu_devices(self):
        """Load available GPU devices"""
        devices = ["CPU"]
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                device_name = torch.cuda.get_device_name(i)
                devices.append(f"GPU {i}: {device_name}")
        self.gpu_menu['values'] = devices
        self.gpu_var.set(devices[0])

    def log(self, msg):
        """Log message with color coding"""
        self.log_area.config(state='normal')
        
        # Add color coding for different message types
        if msg.startswith('✅'):
            self.log_area.insert('end', msg + '\n', 'success')
        elif msg.startswith('❌'):
            self.log_area.insert('end', msg + '\n', 'error')
        elif msg.startswith('⏱️'):
            self.log_area.insert('end', msg + '\n', 'timing')
        elif msg.startswith('📁') or msg.startswith('📊') or msg.startswith('🚀'):
            self.log_area.insert('end', msg + '\n', 'info')
        else:
            self.log_area.insert('end', msg + '\n')
        
        self.log_area.see('end')
        self.log_area.config(state='disabled')

    def load_coqui_models(self):
        """Load Coqui TTS models with download status"""
        try:
            from TTS.api import TTS
            self.log("Loading Coqui models...")
            
            # Get all available models
            available_models = TTS().list_models()
            english_models = [m for m in available_models if m.startswith('tts_models/en/') or m.startswith('tts_models/multilingual/')]
            
            # Update available models in speaker service and save to JSON
            self.speaker_service.update_available_models(english_models)
            self.speaker_service.save_speaker_tags()
            
            # Organize models by download status
            downloaded_models = self.speaker_service.get_downloaded_models()
            undownloaded_models = self.speaker_service.get_undownloaded_models()
            
            organized_models = []
            
            # Add downloaded models section
            if downloaded_models:
                organized_models.append("--- Downloaded Models ---")
                organized_models.extend(downloaded_models)
            
            # Add undownloaded models section
            if undownloaded_models:
                organized_models.append("--- Available Models (Not Downloaded) ---")
                organized_models.extend(undownloaded_models)
            
            self.coqui_models = english_models
            self.model_menu['values'] = organized_models
            
            # Set first downloaded model as default, or first available model
            if downloaded_models:
                self.model_var.set(downloaded_models[0])
            elif english_models:
                self.model_var.set(english_models[0])
            
            if self.model_var.get():
                self.on_model_change()
            
            self.log(f"📊 Downloaded models: {len(downloaded_models)}")
            self.log(f"📦 Available models: {len(undownloaded_models)}")
            self.log(f"📋 Total models: {len(english_models)}")
            
        except Exception as e:
            self.log(f"Error loading Coqui models: {e}\n{traceback.format_exc()}")

    def on_engine_change(self, event=None):
        """Handle engine selection change"""
        engine = self.engine_var.get()
        if engine == "Coqui TTS":
            self.model_menu.config(state='readonly')
            self.speaker_menu.config(state='readonly')
            self.language_menu.config(state='readonly')
            self.speed_entry.config(state='normal')
            self.gpu_menu.config(state='readonly')
        else:
            self.model_menu.config(state='disabled')
            self.speaker_menu.config(state='disabled')
            self.language_menu.config(state='disabled')
            self.speed_entry.config(state='disabled')
            self.gpu_menu.config(state='disabled')
            self.log("Only Coqui TTS is implemented in this version.")

    def on_model_change(self, event=None):
        """Handle model selection change"""
        model = self.model_var.get()
        if not model or model.startswith("---"):
            return
        self.selected_model = model
        self.log(f"Loading model: {model}")
        def load_model_info():
            try:
                from TTS.api import TTS
                tts = TTS(model_name=model)
                
                # Mark model as downloaded if successfully loaded
                if self.speaker_service.mark_model_downloaded(model):
                    self.log(f"✅ Marked '{model}' as downloaded")
                    # Save changes to JSON
                    self.speaker_service.save_speaker_tags()
                    # Refresh model list to update organization
                    self.load_coqui_models()
                
                # Store the TTS engine for filter checking
                self.tts_engine = tts
                
                # Load speakers
                if tts.is_multi_speaker:
                    speakers = tts.speakers
                    if speakers and isinstance(speakers, (list, tuple)) and len(speakers) > 0:
                        self.coqui_speakers = speakers
                        self.log(f"Loaded {len(speakers)} speakers for multi-speaker model.")
                    else:
                        self.coqui_speakers = [model]  # Fallback to model name
                        self.log("Multi-speaker model detected but no speakers found (using model name as fallback).")
                else:
                    self.coqui_speakers = [model]  # Use model name for single-speaker
                    self.log("Single-speaker model (using model name as speaker identifier).")
                self.update_speaker_menu()
                
                # Load languages
                languages = getattr(tts, 'languages', None)
                if languages:
                    self.coqui_languages = languages
                    self.language_menu['values'] = languages
                    self.language_var.set(languages[0])
                    self.log(f"Loaded {len(languages)} languages.")
                else:
                    self.coqui_languages = []
                    self.language_menu['values'] = []
                    self.language_var.set('')
                    self.log("Single-language model.")
                    
            except Exception as e:
                self.log(f"❌ Error loading model info: {e}\n{traceback.format_exc()}")
        threading.Thread(target=load_model_info, daemon=True).start()

    def update_speaker_menu(self):
        """Update speaker menu with tagged speakers, respecting filter toggle for multi-speaker models"""
        if not self.coqui_speakers:
            self.speaker_menu['values'] = []
            self.speaker_var.set('')
            return

        # If filter is enabled and model is multi-speaker, only show untagged speakers
        if hasattr(self, 'selected_model') and hasattr(self, 'show_untagged_only') and self.selected_model and self.show_untagged_only.get():
            # Only filter if multi-speaker
            if hasattr(self, 'tts_engine') and self.tts_engine and hasattr(self.tts_engine, 'is_multi_speaker') and self.tts_engine.is_multi_speaker:
                untagged = self.speaker_service.get_untagged_speakers(self.selected_model, self.coqui_speakers)
                self.speaker_menu['values'] = untagged
                if untagged:
                    self.speaker_var.set(untagged[0])
                else:
                    self.speaker_var.set('')
                self.update_quick_tagging_controls()
                return
        # Default: show all speakers
        self.speaker_menu['values'] = self.coqui_speakers
        if self.speaker_menu['values']:
            self.speaker_var.set(self.speaker_menu['values'][0])
        else:
            self.speaker_var.set('')
        self.update_quick_tagging_controls()

    def on_filter_toggle(self):
        """Handle filter toggle state change"""
        self.update_speaker_menu()

    def refresh_speaker_list(self):
        """Refresh the speaker list, respecting the current filter settings"""
        if not self.selected_model:
            self.log("No model selected. Please select a model first.")
            return
            
        self.log("🔄 Refreshing speaker list...")
        
        # Reload the current model to get fresh speaker information
        try:
            from TTS.api import TTS
            tts = TTS(model_name=self.selected_model)
            
            # Store the TTS engine for filter checking
            self.tts_engine = tts
            
            # Reload speakers
            if tts.is_multi_speaker:
                speakers = tts.speakers
                if speakers and isinstance(speakers, (list, tuple)) and len(speakers) > 0:
                    self.coqui_speakers = speakers
                    self.log(f"✅ Refreshed: Loaded {len(speakers)} speakers for multi-speaker model.")
                else:
                    self.coqui_speakers = [self.selected_model]  # Fallback to model name
                    self.log("⚠️ Multi-speaker model detected but no speakers found (using model name as fallback).")
            else:
                self.coqui_speakers = [self.selected_model]  # Use model name for single-speaker
                self.log("✅ Refreshed: Single-speaker model (using model name as speaker identifier).")
            
            # Update the speaker menu with current filter settings
            self.update_speaker_menu()
            
        except Exception as e:
            self.log(f"❌ Error refreshing speaker list: {e}")
            self.log(f"📋 Error details: {traceback.format_exc()}")

    def update_quick_tagging_controls(self):
        """Update the quick tagging controls based on current speaker"""
        current_display = self.speaker_var.get()
        
        # Convert display name back to actual speaker name
        current_speaker = ""
        if current_display == "Single Speaker":
            current_speaker = ""
        else:
            current_speaker = current_display
        
        # Update current speaker label
        if current_display:
            self.current_speaker_label.config(text=current_display)
        else:
            self.current_speaker_label.config(text="None")
        
        # Update tags status
        if current_speaker is not None:
            tags = self.speaker_service.get_speaker_tags(self.selected_model, current_speaker)
            if tags:
                self.tags_status_label.config(text=", ".join(tags))
            else:
                self.tags_status_label.config(text="No tags")
        else:
            self.tags_status_label.config(text="No tags")
        
        # Update quick tag dropdown
        self.update_quick_tag_dropdown()
        
        # Update button states based on speaker selection
        if current_display:
            self.quick_tag_btn.config(state='normal')
            self.remove_tag_btn.config(state='normal')
        else:
            self.quick_tag_btn.config(state='disabled')
            self.remove_tag_btn.config(state='disabled')

    def update_quick_tag_dropdown(self):
        """Update the quick tag dropdown with available tags"""
        # Get all available tags (model-agnostic)
        all_tags = self.speaker_service.get_all_tags()
        
        # Add "Create New Tag" option
        all_options = ["Create New Tag..."] + sorted(all_tags)
        self.quick_tag_menu['values'] = all_options
        
        # Set default to first option
        if all_options:
            self.quick_tag_var.set(all_options[0])

    def quick_add_tag(self):
        """Quickly add a tag to the current speaker"""
        current_display = self.speaker_var.get()
        selected_tag = self.quick_tag_var.get()
        
        if not current_display:
            messagebox.showwarning("No Speaker", "Please select a speaker first.")
            return
        
        if not selected_tag:
            messagebox.showwarning("No Tag", "Please select a tag first.")
            return
        
        # Convert display name back to actual speaker name
        current_speaker = ""
        if current_display == "Single Speaker":
            current_speaker = ""
        else:
            current_speaker = current_display
        
        # Handle "Create New Tag" option
        if selected_tag == "Create New Tag...":
            new_tag_name = simpledialog.askstring("Create Tag", "Enter new tag name:")
            if not new_tag_name or not new_tag_name.strip():
                return
            selected_tag = new_tag_name.strip()
            
            # Add tag definition with default values
            self.speaker_service.add_tag_definition(selected_tag, f"Tag: {selected_tag}", "#808080")
        
        # Add tag via speaker service
        self.speaker_service.add_tag_to_speaker(self.selected_model, current_speaker, selected_tag)
        # Save changes to JSON
        self.speaker_service.save_speaker_tags()
        self.update_quick_tagging_controls()
        self.log(f"Added tag '{selected_tag}' to speaker '{current_display}'")

    def quick_remove_tag(self):
        """Quickly remove a tag from the current speaker"""
        current_display = self.speaker_var.get()
        selected_tag = self.quick_tag_var.get()
        
        if not current_display:
            messagebox.showwarning("No Speaker", "Please select a speaker first.")
            return
        
        if not selected_tag or selected_tag == "Create New Tag...":
            messagebox.showwarning("No Tag", "Please select a tag to remove.")
            return
        
        # Convert display name back to actual speaker name
        current_speaker = ""
        if current_display == "Single Speaker":
            current_speaker = ""
        else:
            current_speaker = current_display
        
        # Remove tag via speaker service
        if self.speaker_service.remove_tag_from_speaker(self.selected_model, current_speaker, selected_tag):
            # Save changes to JSON
            self.speaker_service.save_speaker_tags()
            self.update_quick_tagging_controls()
            self.log(f"Removed tag '{selected_tag}' from speaker '{current_display}'")
        else:
            messagebox.showwarning("Tag Not Found", f"Speaker '{current_display}' doesn't have tag '{selected_tag}'")

    def on_speaker_change(self, event=None):
        """Handle speaker selection change"""
        self.update_quick_tagging_controls()

    def open_speaker_tag_dialog(self):
        """Open dialog to manage speaker tags"""
        if not self.coqui_speakers:
            messagebox.showwarning("No Speakers", "No speakers available for tagging.")
            return
        
        dialog = SpeakerTagDialog(self, self.selected_model, self.coqui_speakers, self.speaker_service)
        if dialog.result:
            self.speaker_service.save_speaker_tags()
            self.update_speaker_menu()
            self.log(f"Updated speaker tags for {self.selected_model}")
            
    def open_model_management(self):
        """Open dialog to manage model download status"""
        from tkinter import simpledialog
        
        # Get current model
        current_model = self.model_var.get()
        if not current_model or current_model.startswith("---"):
            messagebox.showwarning("No Model", "Please select a model first.")
            return
        
        # Check current status
        is_downloaded = self.speaker_service.is_model_downloaded(current_model)
        status_text = "downloaded" if is_downloaded else "not downloaded"
        
        # Ask user what to do
        action = messagebox.askyesno(
            "Manage Model Status",
            f"Model: {current_model}\n"
            f"Current status: {status_text}\n\n"
            f"Would you like to mark this model as {'not downloaded' if is_downloaded else 'downloaded'}?"
        )
        
        if action:
            if is_downloaded:
                # Mark as not downloaded
                if self.speaker_service.mark_model_not_downloaded(current_model):
                    self.log(f"📦 Marked '{current_model}' as not downloaded")
            else:
                # Mark as downloaded
                if self.speaker_service.mark_model_downloaded(current_model):
                    self.log(f"✅ Marked '{current_model}' as downloaded")
            
            # Save changes
            self.speaker_service.save_speaker_tags()
            
            # Refresh model list
            self.load_coqui_models()
            
            self.log(f"Updated model status for {current_model}")

    def synthesize(self):
        """Synthesize audio from text"""
        engine = self.engine_var.get()
        if engine != "Coqui TTS":
            self.log("Only Coqui TTS is implemented in this version.")
            return
        model = self.model_var.get()
        speaker = self.speaker_var.get() if self.speaker_var.get() else None
        language = self.language_var.get() if self.language_var.get() else None
        speed = self.speed_var.get()
        text = self.text_input.get('1.0', 'end').strip()
        if not text:
            messagebox.showwarning("Input Required", "Please enter text to synthesize.")
            return
        self.log(f"Synthesizing with model: {model}, speaker: {speaker}, language: {language}, speed: {speed}")
        self.play_btn.config(state='disabled')
        
        # Stop any current playback and release the audio file
        try:
            import pygame
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass
        
        def do_synth():
            try:
                from TTS.api import TTS
                import time
                
                # Start timing
                start_time = time.time()
                self.log(f"Starting synthesis at {time.strftime('%H:%M:%S')}")
                
                # Determine device
                device = "cpu"
                if self.gpu_var.get() != "CPU":
                    device = "cuda"
                
                tts = TTS(model_name=model)
                # Log available attributes for debugging
                self.log(f"TTS object attributes: {[attr for attr in dir(tts) if not attr.startswith('_')]}")
                
                # Try to set device - Coqui TTS handles this internally
                # The device parameter can be passed to the TTS constructor or set later
                if device == "cuda":
                    self.log("Using CUDA device for synthesis")
                else:
                    self.log("Using CPU device for synthesis")
                
                # Ensure the output file is not locked by trying to remove it first
                try:
                    if os.path.exists(AUDIO_OUT_PATH_COQUI):
                        os.remove(AUDIO_OUT_PATH_COQUI)
                        time.sleep(0.1)  # Small delay to ensure file is released
                except:
                    pass
                
                kwargs = dict(text=text, file_path=AUDIO_OUT_PATH_COQUI)
                
                # Add speaker if available and model is multi-speaker
                # Check if the model is actually multi-speaker using TTS object properties
                if speaker and tts.is_multi_speaker and speaker != "Single Speaker":
                    kwargs['speaker'] = speaker
                
                # Add language if available and model is multi-lingual
                if language and self.coqui_languages:
                    kwargs['language'] = language
                
                if speed:
                    kwargs['speed'] = speed
                
                # Start synthesis timing
                synthesis_start = time.time()
                self.log(f"Starting TTS synthesis...")
                
                tts.tts_to_file(**kwargs)
                
                # End synthesis timing
                synthesis_end = time.time()
                synthesis_time = synthesis_end - synthesis_start
                
                if os.path.exists(AUDIO_OUT_PATH_COQUI):
                    # End total timing
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    # Get file size
                    file_size = os.path.getsize(AUDIO_OUT_PATH_COQUI)
                    file_size_mb = file_size / (1024 * 1024)
                    
                    self.log(f"✅ Synthesis completed successfully!")
                    self.log(f"📁 Audio saved to: {AUDIO_OUT_PATH_COQUI}")
                    self.log(f"📊 File size: {file_size_mb:.2f} MB")
                    self.log(f"⏱️  TTS synthesis time: {synthesis_time:.2f} seconds")
                    self.log(f"⏱️  Total time (including setup): {total_time:.2f} seconds")
                    self.log(f"🚀 Synthesis speed: {file_size_mb/synthesis_time:.2f} MB/s")
                    
                    self.play_btn.config(state='normal')
                    self.play_btn.config(text="Play")
                    self.is_playing = False
                else:
                    end_time = time.time()
                    total_time = end_time - start_time
                    self.log(f"❌ Synthesis failed: Audio file was not created at {AUDIO_OUT_PATH_COQUI}")
                    self.log(f"⏱️  Time elapsed before failure: {total_time:.2f} seconds")
            except Exception as e:
                end_time = time.time()
                total_time = end_time - start_time
                self.log(f"❌ Synthesis failed: {e}")
                self.log(f"⏱️  Time elapsed before error: {total_time:.2f} seconds")
                self.log(f"📋 Error details: {traceback.format_exc()}")
                self.play_btn.config(state='disabled')
                self.play_btn.config(text="Play")
                self.is_playing = False
        threading.Thread(target=do_synth, daemon=True).start()

    def play_audio(self):
        """Play the synthesized audio"""
        if self.is_playing:
            # Stop playback
            self.stop_audio()
            return
            
        filepath = AUDIO_OUT_PATH_COQUI
        if not os.path.exists(filepath):
            self.log(f"Audio file not found: {filepath}")
            self.play_btn.config(state='disabled')
            return
        self.log(f"Playing audio: {filepath}")
        
        # Switch to Stop button
        self.is_playing = True
        self.play_btn.config(text="Stop")
        
        def do_play():
            try:
                import pygame
                # Initialize mixer if not already initialized
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() and self.is_playing:
                    pass
                # Switch back to Play button
                self.is_playing = False
                self.play_btn.config(text="Play")
                self.log("Playback finished.")
            except Exception as e:
                self.log(f"Playback failed: {e}\n{traceback.format_exc()}")
                self.is_playing = False
                self.play_btn.config(text="Play")
        threading.Thread(target=do_play, daemon=True).start()

    def reset_text_to_default(self):
        """Reset the text input to the default text"""
        self.text_input.delete('1.0', tk.END)
        self.text_input.insert('1.0', DEFAULT_TEXT)
        self.log("🔄 Text reset to default")

    def stop_audio(self):
        """Stop current audio playback"""
        try:
            import pygame
            pygame.mixer.music.stop()
            self.is_playing = False
            self.play_btn.config(text="Play")
            self.log("Playback stopped.")
        except Exception as e:
            self.log(f"Error stopping playback: {e}")
            self.is_playing = False
            self.play_btn.config(text="Play") 