# TTS Tester GUI

A comprehensive GUI application purpose built for testing Coqui TTS models and grouping them via tags

## 🚀 Features

- **🎤 TTS Synthesis**: Test Coqui TTS models with real-time synthesis
- **🏷️ Tag-Centric Organization**: Flexible tagging system with one tag to many models/speakers
- **⏱️ Performance Metrics**: Detailed timing and file size analysis
- **📊 Model Management**: Track downloaded vs available models
- **🔊 Audio Playback**: Integrated audio playback with pygame
- **🎯 GPU Support**: CUDA device selection for accelerated synthesis
- **📝 Speaker Tagging**: Organize speakers with custom tags and descriptions

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- CUDA-compatible GPU (optional, for acceleration)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd TTs_Testing_Tkinter

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Development Installation
```bash
# Install in development mode
pip install -e .

# Install with additional audio features
pip install -e .[audio]

# Install with development tools
pip install -e .[dev]
```

## 🎯 Usage

### Basic Usage
1. **Select TTS Engine**: Choose "Coqui TTS" (other engines coming soon)
2. **Choose GPU Device**: Select CPU or available GPU for synthesis
3. **Load Model**: Select from available Coqui TTS models
4. **Configure Speaker**: Choose speaker and language if available
5. **Enter Text**: Type or paste text to synthesize
6. **Synthesize**: Click "Synthesize" to generate audio
7. **Play Audio**: Use the "Play" button to hear the result

### Speaker Tagging
- **Quick Tagging**: Use the quick tag controls in the main interface
- **Detailed Management**: Open the tag management dialog for advanced operations
- **Tag Organization**: Tags are model-agnostic and reusable across models
- **Visual Feedback**: Tags have colors and descriptions for better organization

### Model Management
- **Download Tracking**: Models are automatically marked as downloaded when successfully loaded
- **Manual Management**: Use "Manage Models" to manually mark download status
- **Organized Display**: Models are separated into downloaded and available sections

## 🏗️ Architecture

```
TTs_Testing_Tkinter/
├── main.py                          # Main entry point
├── gui/
│   ├── tts_tester_gui.py           # Main GUI application
│   ├── components/
│   │   ├── speaker_tag_dialog.py   # Speaker tag management dialog
│   │   └── theme_manager.py        # Dark theme management
│   └── services/
│       ├── tts_service.py          # TTS synthesis operations
│       └── speaker_service.py      # Tag-centric speaker management
├── speaker_tags.json               # Tag definitions and speaker associations
├── requirements.txt                # Python dependencies
├── setup.py                       # Package installation
└── LICENSE                        # MIT License
```

## 🏷️ Tag-Centric System

The application uses a tag-centric organization where:

- **Tags are Primary**: Tags exist independently of models
- **One-to-Many**: Each tag can be associated with multiple speakers across multiple models
- **Reusable**: Tags can be used across different TTS models
- **Flexible**: Add new models without recreating tags

### JSON Structure
```json
{
  "_metadata": { "version": "1.3" },
  "_models": { "downloaded": [...], "available": [...] },
  "_tags": {
    "Female": {
      "description": "Female voice characteristics",
      "color": "#ff69b4",
      "speakers": {
        "model1": ["speaker1", "speaker2"],
        "model2": ["speaker3"]
      }
    }
  }
}
```

## 🎨 Customization

### Adding New Tags
```python
# Programmatically add tags
speaker_service.add_tag_definition("NewTag", "Description", "#color")
speaker_service.add_tag_to_speaker("model", "speaker", "NewTag")
```

### Customizing Theme
```python
# Modify colors in gui/components/theme_manager.py
self.colors = {
    'bg': '#your_color',
    'fg': '#your_color',
    # ... other colors
}
```

### Extending Features
- **New Components**: Add to `gui/components/`
- **New Services**: Add to `gui/services/`
- **New Features**: Extend `gui/tts_tester_gui.py`

## 📊 Performance Features

- **Synthesis Timing**: Measures TTS synthesis time
- **File Size Analysis**: Tracks output file size
- **Speed Metrics**: Calculates synthesis speed (MB/s)
- **GPU Utilization**: Shows CUDA device usage
- **Memory Tracking**: Monitors resource usage

## 🔧 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
flake8 .
```

### Building Distribution
```bash
python setup.py sdist bdist_wheel
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Coqui TTS**: For the excellent TTS library
- **PyTorch**: For GPU acceleration support
- **Pygame**: For audio playback functionality
- **Tkinter**: For the GUI framework

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check the documentation
- Review the code examples

---

**TTS Tester GUI** - Making TTS model testing easy and organized! 🎤✨ 