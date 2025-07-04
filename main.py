#!/usr/bin/env python3
"""
TTS Tester GUI - Main Entry Point
A comprehensive GUI for testing Coqui TTS models with speaker tagging and timing.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from gui.tts_tester_gui import TTSTesterGUI

def main():
    """Main entry point for the TTS Tester GUI"""
    try:
        app = TTSTesterGUI()
        app.mainloop()
    except Exception as e:
        print(f"Error starting TTS Tester GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 