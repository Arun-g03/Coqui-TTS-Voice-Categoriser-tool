"""
Speaker Service Component
Handles speaker tagging operations and persistence.
"""

import os
import json
from typing import Dict, List, Set

class SpeakerService:
    """Service for managing tag-centric speaker organization and model download status"""
    
    def __init__(self, tags_file="speaker_tags.json"):
        self.tags_file = tags_file
        self.speaker_tags = {}  # {model_name: {speaker: set(tags)}} - for backward compatibility
        self.tag_definitions = {}  # {tag_name: {description, color, speakers: {model: [speakers]}}}
        self.downloaded_models = set()  # Set of downloaded model names
        self.available_models = []  # List of all available models
        self.load_speaker_tags()
        
    def load_speaker_tags(self):
        """Load speaker tags and model status from JSON file"""
        try:
            if os.path.exists(self.tags_file):
                with open(self.tags_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Handle new tag-centric format (v1.3+)
                    if "_metadata" in data and "_tags" in data:
                        tags_data = data.get("_tags", {})
                        if tags_data and any("speakers" in tag_data for tag_data in tags_data.values()):
                            # New tag-centric format
                            self.tag_definitions = data.get("_tags", {})
                            self.downloaded_models = set(data.get("_models", {}).get("downloaded", []))
                            self.available_models = data.get("_models", {}).get("available", [])
                            
                            # Build speaker_tags for backward compatibility
                            self.speaker_tags = {}
                            for tag_name, tag_data in self.tag_definitions.items():
                                speakers_data = tag_data.get("speakers", {})
                                for model_name, speakers in speakers_data.items():
                                    if model_name not in self.speaker_tags:
                                        self.speaker_tags[model_name] = {}
                                    for speaker in speakers:
                                        if speaker not in self.speaker_tags[model_name]:
                                            self.speaker_tags[model_name][speaker] = set()
                                        self.speaker_tags[model_name][speaker].add(tag_name)
                        
                        # Handle new model-agnostic format (v1.2)
                        elif "_speakers" in data:
                            # Convert v1.2 to v1.3 format
                            self.tag_definitions = data.get("_tags", {})
                            speakers_data = data.get("_speakers", {})
                            
                            # Convert to tag-centric format
                            for tag_name in self.tag_definitions:
                                self.tag_definitions[tag_name]["speakers"] = {}
                            
                            for model_name, speakers in speakers_data.items():
                                for speaker, tags in speakers.items():
                                    for tag in tags:
                                        if tag in self.tag_definitions:
                                            if model_name not in self.tag_definitions[tag]["speakers"]:
                                                self.tag_definitions[tag]["speakers"][model_name] = []
                                            self.tag_definitions[tag]["speakers"][model_name].append(speaker)
                            
                            # Build speaker_tags for backward compatibility
                            self.speaker_tags = {}
                            for model_name, speakers in speakers_data.items():
                                self.speaker_tags[model_name] = {}
                                for speaker, tags in speakers.items():
                                    self.speaker_tags[model_name][speaker] = set(tags)
                            
                            # Load model status
                            models_data = data.get("_models", {})
                            self.downloaded_models = set(models_data.get("downloaded", []))
                            self.available_models = models_data.get("available", [])
                        
                        # Handle old format with metadata (v1.1)
                        elif "speaker_tags" in data:
                            # Old format - convert to new format
                            self.speaker_tags = {}
                            speaker_tags_data = data.get("speaker_tags", {})
                            for model_name, speakers in speaker_tags_data.items():
                                self.speaker_tags[model_name] = {}
                                for speaker, tags in speakers.items():
                                    self.speaker_tags[model_name][speaker] = set(tags)
                            
                            # Initialize tag definitions from existing tags
                            all_tags = set()
                            for speakers in self.speaker_tags.values():
                                for tags in speakers.values():
                                    all_tags.update(tags)
                            
                            self.tag_definitions = {tag: {"description": f"Tag: {tag}", "color": "#808080", "speakers": {}} for tag in all_tags}
                            
                            # Convert to tag-centric format
                            for tag_name in self.tag_definitions:
                                self.tag_definitions[tag_name]["speakers"] = {}
                            
                            for model_name, speakers in self.speaker_tags.items():
                                for speaker, tags in speakers.items():
                                    for tag in tags:
                                        if model_name not in self.tag_definitions[tag]["speakers"]:
                                            self.tag_definitions[tag]["speakers"][model_name] = []
                                        self.tag_definitions[tag]["speakers"][model_name].append(speaker)
                            
                            # Load model status
                            models_data = data.get("_models", {})
                            self.downloaded_models = set(models_data.get("downloaded", []))
                            self.available_models = models_data.get("available", [])
                        
                        else:
                            # Legacy format - convert to new format
                            self.speaker_tags = {}
                            for model_name, speakers in data.items():
                                self.speaker_tags[model_name] = {}
                                for speaker, tags in speakers.items():
                                    self.speaker_tags[model_name][speaker] = set(tags)
                            
                            # Initialize tag definitions from existing tags
                            all_tags = set()
                            for speakers in self.speaker_tags.values():
                                for tags in speakers.values():
                                    all_tags.update(tags)
                            
                            self.tag_definitions = {tag: {"description": f"Tag: {tag}", "color": "#808080", "speakers": {}} for tag in all_tags}
                            
                            # Convert to tag-centric format
                            for tag_name in self.tag_definitions:
                                self.tag_definitions[tag_name]["speakers"] = {}
                            
                            for model_name, speakers in self.speaker_tags.items():
                                for speaker, tags in speakers.items():
                                    for tag in tags:
                                        if model_name not in self.tag_definitions[tag]["speakers"]:
                                            self.tag_definitions[tag]["speakers"][model_name] = []
                                        self.tag_definitions[tag]["speakers"][model_name].append(speaker)
                            
                            # Initialize with legacy data
                            self.downloaded_models = set(self.speaker_tags.keys())
                            self.available_models = list(self.speaker_tags.keys())
            else:
                self.speaker_tags = {}
                self.tag_definitions = {}
                self.downloaded_models = set()
                self.available_models = []
        except Exception as e:
            print(f"Error loading speaker tags: {e}")
            self.speaker_tags = {}
            self.tag_definitions = {}
            self.downloaded_models = set()
            self.available_models = []
            
    def save_speaker_tags(self):
        """Save speaker tags and model status to JSON file"""
        try:
            # Prepare data in new tag-centric format
            data = {
                "_metadata": {
                    "version": "1.3",
                    "description": "TTS Tester data with tag-centric organization - one tag to many models/speakers"
                },
                "_models": {
                    "downloaded": list(self.downloaded_models),
                    "available": self.available_models
                },
                "_tags": {}
            }
            
            # Save tag definitions with their speaker associations
            for tag_name, tag_data in self.tag_definitions.items():
                data["_tags"][tag_name] = {
                    "description": tag_data.get("description", f"Tag: {tag_name}"),
                    "color": tag_data.get("color", "#808080"),
                    "speakers": tag_data.get("speakers", {})
                }
                    
            with open(self.tags_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving speaker tags: {e}")
            
    def add_tag_to_speaker(self, model_name: str, speaker: str, tag: str) -> bool:
        """Add a tag to a speaker"""
        if not model_name or not speaker or not tag:
            return False
            
        # Initialize model if it doesn't exist
        if model_name not in self.speaker_tags:
            self.speaker_tags[model_name] = {}
            
        # Initialize speaker if it doesn't exist
        if speaker not in self.speaker_tags[model_name]:
            self.speaker_tags[model_name][speaker] = set()
            
        # Add tag to speaker
        self.speaker_tags[model_name][speaker].add(tag)
        
        # Update tag-centric structure
        if tag not in self.tag_definitions:
            self.tag_definitions[tag] = {
                "description": f"Tag: {tag}",
                "color": "#808080",
                "speakers": {}
            }
        
        if model_name not in self.tag_definitions[tag]["speakers"]:
            self.tag_definitions[tag]["speakers"][model_name] = []
        
        if speaker not in self.tag_definitions[tag]["speakers"][model_name]:
            self.tag_definitions[tag]["speakers"][model_name].append(speaker)
        
        return True
        
    def remove_tag_from_speaker(self, model_name: str, speaker: str, tag: str) -> bool:
        """Remove a tag from a speaker"""
        if (model_name in self.speaker_tags and 
            speaker in self.speaker_tags[model_name] and 
            tag in self.speaker_tags[model_name][speaker]):
            self.speaker_tags[model_name][speaker].discard(tag)
            
            # Update tag-centric structure
            if tag in self.tag_definitions and model_name in self.tag_definitions[tag]["speakers"]:
                if speaker in self.tag_definitions[tag]["speakers"][model_name]:
                    self.tag_definitions[tag]["speakers"][model_name].remove(speaker)
                    
                    # Remove empty model entries
                    if not self.tag_definitions[tag]["speakers"][model_name]:
                        del self.tag_definitions[tag]["speakers"][model_name]
            
            return True
        return False
        
    def get_speaker_tags(self, model_name: str, speaker: str) -> Set[str]:
        """Get all tags for a speaker"""
        if (model_name in self.speaker_tags and 
            speaker in self.speaker_tags[model_name]):
            return self.speaker_tags[model_name][speaker].copy()
        return set()
        
    def get_all_tags_for_model(self, model_name: str) -> Set[str]:
        """Get all unique tags used for a model"""
        all_tags = set()
        if model_name in self.speaker_tags:
            for speaker_tags in self.speaker_tags[model_name].values():
                all_tags.update(speaker_tags)
        return all_tags
        
    def get_speakers_with_tag(self, model_name: str, tag: str) -> List[str]:
        """Get all speakers that have a specific tag"""
        speakers = []
        if model_name in self.speaker_tags:
            for speaker, tags in self.speaker_tags[model_name].items():
                if tag in tags:
                    speakers.append(speaker)
        return speakers
        
    def remove_speaker(self, model_name: str, speaker: str) -> bool:
        """Remove a speaker and all their tags"""
        if (model_name in self.speaker_tags and 
            speaker in self.speaker_tags[model_name]):
            del self.speaker_tags[model_name][speaker]
            return True
        return False
        
    def remove_model(self, model_name: str) -> bool:
        """Remove a model and all its speakers"""
        if model_name in self.speaker_tags:
            del self.speaker_tags[model_name]
            return True
        return False
        
    def get_all_models(self) -> List[str]:
        """Get all model names"""
        return list(self.speaker_tags.keys())
        
    def get_all_speakers_for_model(self, model_name: str) -> List[str]:
        """Get all speakers for a model"""
        if model_name in self.speaker_tags:
            return list(self.speaker_tags[model_name].keys())
        return []
        
    def get_tagged_speakers(self, model_name: str) -> List[str]:
        """Get all speakers that have at least one tag"""
        tagged_speakers = []
        if model_name in self.speaker_tags:
            for speaker, tags in self.speaker_tags[model_name].items():
                if tags:  # If speaker has any tags
                    tagged_speakers.append(speaker)
        return tagged_speakers
        
    def get_untagged_speakers(self, model_name: str, all_speakers: List[str]) -> List[str]:
        """Get all speakers that have no tags"""
        tagged_speakers = set(self.get_tagged_speakers(model_name))
        return [speaker for speaker in all_speakers if speaker not in tagged_speakers]
        
    def get_speaker_tag_count(self, model_name: str, speaker: str) -> int:
        """Get the number of tags for a speaker"""
        return len(self.get_speaker_tags(model_name, speaker))
        
    def get_model_tag_count(self, model_name: str) -> int:
        """Get the total number of tags used in a model"""
        return len(self.get_all_tags_for_model(model_name))
        
    def debug_info(self) -> Dict:
        """Get debug information about loaded tags"""
        return {
            'tags_file': self.tags_file,
            'file_exists': os.path.exists(self.tags_file),
            'models_count': len(self.speaker_tags),
            'models': list(self.speaker_tags.keys()),
            'total_speakers': sum(len(speakers) for speakers in self.speaker_tags.values()),
            'total_tags': sum(len(tags) for speakers in self.speaker_tags.values() for tags in speakers.values()),
            'downloaded_models': list(self.downloaded_models),
            'available_models': self.available_models,
            'tag_definitions_count': len(self.tag_definitions),
            'available_tags': list(self.tag_definitions.keys())
        }
        
    def mark_model_downloaded(self, model_name: str) -> bool:
        """Mark a model as downloaded"""
        if model_name not in self.downloaded_models:
            self.downloaded_models.add(model_name)
            return True
        return False
        
    def mark_model_not_downloaded(self, model_name: str) -> bool:
        """Mark a model as not downloaded"""
        if model_name in self.downloaded_models:
            self.downloaded_models.discard(model_name)
            return True
        return False
        
    def is_model_downloaded(self, model_name: str) -> bool:
        """Check if a model is marked as downloaded"""
        return model_name in self.downloaded_models
        
    def get_downloaded_models(self) -> List[str]:
        """Get list of downloaded models"""
        return list(self.downloaded_models)
        
    def get_undownloaded_models(self) -> List[str]:
        """Get list of available but not downloaded models"""
        return [model for model in self.available_models if model not in self.downloaded_models]
        
    def update_available_models(self, models: List[str]):
        """Update the list of available models"""
        self.available_models = models
        
    def get_all_tags(self) -> List[str]:
        """Get all available tag names"""
        return list(self.tag_definitions.keys())
        
    def get_tag_definition(self, tag_name: str) -> Dict:
        """Get definition for a specific tag"""
        return self.tag_definitions.get(tag_name, {})
        
    def add_tag_definition(self, tag_name: str, description: str = "", color: str = "#808080"):
        """Add a new tag definition"""
        self.tag_definitions[tag_name] = {
            "description": description,
            "color": color,
            "speakers": {}
        }
        
    def remove_tag_definition(self, tag_name: str) -> bool:
        """Remove a tag definition and all its usages"""
        if tag_name in self.tag_definitions:
            # Remove from definitions
            del self.tag_definitions[tag_name]
            
            # Remove from all speakers
            for model_name in self.speaker_tags:
                for speaker in self.speaker_tags[model_name]:
                    self.speaker_tags[model_name][speaker].discard(tag_name)
            
            return True
        return False
        
    def update_tag_definition(self, tag_name: str, description: str = None, color: str = None):
        """Update a tag definition"""
        if tag_name in self.tag_definitions:
            if description is not None:
                self.tag_definitions[tag_name]["description"] = description
            if color is not None:
                self.tag_definitions[tag_name]["color"] = color
                
    def get_speakers_by_tag(self, tag_name: str) -> Dict[str, List[str]]:
        """Get all speakers that have a specific tag, organized by model"""
        result = {}
        if tag_name in self.tag_definitions:
            result = self.tag_definitions[tag_name].get("speakers", {}).copy()
        return result
        
    def get_all_speakers_with_tags(self) -> Dict[str, Dict[str, List[str]]]:
        """Get all speakers with their tags, organized by model"""
        result = {}
        for model_name, speakers in self.speaker_tags.items():
            result[model_name] = {}
            for speaker, tags in speakers.items():
                result[model_name][speaker] = list(tags)
        return result 