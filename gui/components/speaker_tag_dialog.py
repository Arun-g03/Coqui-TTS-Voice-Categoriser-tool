"""
Speaker Tag Dialog Component
Handles the detailed speaker tag management interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json

class SpeakerTagDialog(tk.Toplevel):
    """Dialog for managing speaker tags"""
    
    def __init__(self, parent, model_name, speakers, speaker_service):
        super().__init__(parent)
        self.parent = parent
        self.model_name = model_name
        self.speakers = speakers
        self.speaker_service = speaker_service
        self.result = False
        
        self.title(f"Speaker Tag Management - {model_name}")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Apply theme
        self.configure(bg='#2d3748')
        
        self.create_widgets()
        self.load_data()
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel - Speakers and their tags
        left_frame = ttk.LabelFrame(main_frame, text="Speakers and Tags")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Filter frame
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill='x', padx=5, pady=2)
        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="All", variable=self.filter_var, 
                       value="all", command=self.on_filter_change).pack(side='left')
        ttk.Radiobutton(filter_frame, text="Tagged", variable=self.filter_var, 
                       value="tagged", command=self.on_filter_change).pack(side='left')
        ttk.Radiobutton(filter_frame, text="Untagged", variable=self.filter_var, 
                       value="untagged", command=self.on_filter_change).pack(side='left')
        
        # Speakers listbox
        speakers_frame = ttk.Frame(left_frame)
        speakers_frame.pack(fill='both', expand=True, padx=5, pady=5)
        ttk.Label(speakers_frame, text="Speakers:").pack(anchor='w')
        
        # Create Treeview for speakers and their tags
        columns = ('speaker', 'tags', 'rating')
        self.speakers_tree = ttk.Treeview(speakers_frame, columns=columns, show='tree headings', height=15)
        self.speakers_tree.heading('speaker', text='Speaker')
        self.speakers_tree.heading('tags', text='Tags')
        self.speakers_tree.heading('rating', text='Rating')
        self.speakers_tree.column('speaker', width=150)
        self.speakers_tree.column('tags', width=250)
        self.speakers_tree.column('rating', width=80)
        
        # Scrollbar for speakers tree
        speakers_scrollbar = ttk.Scrollbar(speakers_frame, orient='vertical', command=self.speakers_tree.yview)
        self.speakers_tree.configure(yscrollcommand=speakers_scrollbar.set)
        
        self.speakers_tree.pack(side='left', fill='both', expand=True)
        speakers_scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.speakers_tree.bind('<<TreeviewSelect>>', self.on_speaker_select)
        
        # Right panel - Tag management
        right_frame = ttk.LabelFrame(main_frame, text="Tag Management")
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Selected speaker info
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(info_frame, text="Selected Speaker:").pack(anchor='w')
        self.selected_speaker_label = ttk.Label(info_frame, text="None", font=('Arial', 10, 'bold'))
        self.selected_speaker_label.pack(anchor='w')
        
        # Rating section
        rating_frame = ttk.LabelFrame(right_frame, text="Speaker Rating")
        rating_frame.pack(fill='x', padx=5, pady=5)
        
        # Current rating display
        rating_display_frame = ttk.Frame(rating_frame)
        rating_display_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(rating_display_frame, text="Current Rating:").pack(side='left')
        self.current_rating_label = ttk.Label(rating_display_frame, text="No rating", font=('Arial', 9, 'italic'))
        self.current_rating_label.pack(side='left', padx=(5, 0))
        
        # Rating input
        rating_input_frame = ttk.Frame(rating_frame)
        rating_input_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(rating_input_frame, text="Rating (0.0-5.0):").pack(side='left')
        self.rating_var = tk.DoubleVar(value=0.0)
        self.rating_entry = ttk.Entry(rating_input_frame, textvariable=self.rating_var, width=8)
        self.rating_entry.pack(side='left', padx=(5, 0))
        
        # Rating buttons
        rating_buttons_frame = ttk.Frame(rating_frame)
        rating_buttons_frame.pack(fill='x', padx=5, pady=5)
        self.set_rating_btn = ttk.Button(rating_buttons_frame, text="Set Rating", command=self.set_speaker_rating)
        self.set_rating_btn.pack(side='left', padx=(0, 5))
        self.remove_rating_btn = ttk.Button(rating_buttons_frame, text="Remove Rating", command=self.remove_speaker_rating)
        self.remove_rating_btn.pack(side='left')
        
        # Current tags
        current_tags_frame = ttk.LabelFrame(right_frame, text="Current Tags")
        current_tags_frame.pack(fill='x', padx=5, pady=5)
        
        self.current_tags_listbox = tk.Listbox(current_tags_frame, height=6, selectmode='single')
        current_tags_scrollbar = ttk.Scrollbar(current_tags_frame, orient='vertical', command=self.current_tags_listbox.yview)
        self.current_tags_listbox.configure(yscrollcommand=current_tags_scrollbar.set)
        
        self.current_tags_listbox.pack(side='left', fill='both', expand=True)
        current_tags_scrollbar.pack(side='right', fill='y')
        
        # Tag removal button
        remove_tag_btn = ttk.Button(current_tags_frame, text="Remove Selected Tag", command=self.remove_selected_tag)
        remove_tag_btn.pack(pady=5)
        
        # Tag Definitions section (Global tag management)
        tag_definitions_frame = ttk.LabelFrame(right_frame, text="Tag Definitions")
        tag_definitions_frame.pack(fill='x', padx=5, pady=5)
        
        # New tag definition input
        new_tag_frame = ttk.Frame(tag_definitions_frame)
        new_tag_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(new_tag_frame, text="New Tag:").pack(side='left')
        self.new_tag_def_var = tk.StringVar()
        new_tag_entry = ttk.Entry(new_tag_frame, textvariable=self.new_tag_def_var)
        new_tag_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Add tag definition button
        add_tag_def_btn = ttk.Button(tag_definitions_frame, text="Create Tag Definition", command=self.add_tag_definition)
        add_tag_def_btn.pack(pady=5)
        
        # Add tag section (for adding tags to selected speaker)
        add_tag_frame = ttk.LabelFrame(right_frame, text="Add Tag to Speaker")
        add_tag_frame.pack(fill='x', padx=5, pady=5)
        
        # Tag input
        tag_input_frame = ttk.Frame(add_tag_frame)
        tag_input_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(tag_input_frame, text="Tag Name:").pack(side='left')
        self.new_tag_var = tk.StringVar()
        tag_entry = ttk.Entry(tag_input_frame, textvariable=self.new_tag_var)
        tag_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Add tag button
        add_tag_btn = ttk.Button(add_tag_frame, text="Add Tag to Speaker", command=self.add_tag_to_speaker)
        add_tag_btn.pack(pady=5)
        
        # Existing tags section
        existing_tags_frame = ttk.LabelFrame(right_frame, text="Existing Tags")
        existing_tags_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Existing tags listbox
        self.existing_tags_listbox = tk.Listbox(existing_tags_frame, height=8, selectmode='single')
        existing_tags_scrollbar = ttk.Scrollbar(existing_tags_frame, orient='vertical', command=self.existing_tags_listbox.yview)
        self.existing_tags_listbox.configure(yscrollcommand=existing_tags_scrollbar.set)
        
        self.existing_tags_listbox.pack(side='left', fill='both', expand=True)
        existing_tags_scrollbar.pack(side='right', fill='y')
        
        # Add existing tag button
        add_existing_btn = ttk.Button(existing_tags_frame, text="Add Selected Tag", command=self.add_existing_tag)
        add_existing_btn.pack(pady=5)
        
        # Bottom buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        save_btn = ttk.Button(button_frame, text="Save Changes", command=self.save_changes)
        save_btn.pack(side='right', padx=(5, 0))
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side='right')
        
    def load_data(self):
        """Load speakers and tags data"""
        self.populate_speakers_tree()
        self.populate_existing_tags()
        
    def populate_speakers_tree(self):
        """Populate the speakers treeview"""
        # Clear existing items
        for item in self.speakers_tree.get_children():
            self.speakers_tree.delete(item)
        
        # Add speakers
        for speaker in self.speakers:
            # Display "Single Speaker" for empty speaker names
            display_name = "Single Speaker" if speaker == "" else speaker
            tags = self.speaker_service.get_speaker_tags(self.model_name, speaker)
            tags_str = ", ".join(tags) if tags else "No tags"
            rating = self.speaker_service.get_speaker_rating(self.model_name, speaker)
            rating_str = f"{rating:.1f}" if rating > 0.0 else "No rating"
            self.speakers_tree.insert('', 'end', values=(display_name, tags_str, rating_str))
            
    def populate_existing_tags(self):
        """Populate the existing tags listbox"""
        self.existing_tags_listbox.delete(0, tk.END)
        # Show all available tags, not just the ones used in current model
        all_tags = self.speaker_service.get_all_tags()
        for tag in sorted(all_tags):
            self.existing_tags_listbox.insert(tk.END, tag)
            
    def on_search_change(self, *args):
        """Handle search text change"""
        search_text = self.search_var.get().lower()
        filter_type = self.filter_var.get()
        
        # Clear and repopulate tree
        for item in self.speakers_tree.get_children():
            self.speakers_tree.delete(item)
        
        for speaker in self.speakers:
            # Display "Single Speaker" for empty speaker names
            display_name = "Single Speaker" if speaker == "" else speaker
            
            # Apply search filter
            if search_text and search_text not in display_name.lower():
                continue
                
            # Apply tag filter
            tags = self.speaker_service.get_speaker_tags(self.model_name, speaker)
            if filter_type == "tagged" and not tags:
                continue
            elif filter_type == "untagged" and tags:
                continue
                
            tags_str = ", ".join(tags) if tags else "No tags"
            rating = self.speaker_service.get_speaker_rating(self.model_name, speaker)
            rating_str = f"{rating:.1f}" if rating > 0.0 else "No rating"
            self.speakers_tree.insert('', 'end', values=(display_name, tags_str, rating_str))
            
    def on_filter_change(self):
        """Handle filter radio button change"""
        self.on_search_change()
        
    def on_speaker_select(self, event):
        """Handle speaker selection"""
        selection = self.speakers_tree.selection()
        if selection:
            item = self.speakers_tree.item(selection[0])
            display_name = item['values'][0]
            
            # Convert display name back to actual speaker name
            if display_name == "Single Speaker":
                actual_speaker = ""
            else:
                actual_speaker = display_name
            
            self.selected_speaker_label.config(text=display_name)
            self.update_current_tags_display(actual_speaker)
            self.update_current_rating_display(actual_speaker)
        else:
            self.selected_speaker_label.config(text="None")
            self.current_tags_listbox.delete(0, tk.END)
            self.current_rating_label.config(text="No rating")
            self.rating_var.set(0.0)
            
    def update_current_tags_display(self, speaker):
        """Update the current tags display for a speaker"""
        self.current_tags_listbox.delete(0, tk.END)
        tags = self.speaker_service.get_speaker_tags(self.model_name, speaker)
        for tag in sorted(tags):
            self.current_tags_listbox.insert(tk.END, tag)
            
    def add_tag_to_speaker(self):
        """Add a new tag to the selected speaker"""
        display_name = self.selected_speaker_label.cget("text")
        tag = self.new_tag_var.get().strip()
        
        if display_name == "None":
            messagebox.showwarning("No Speaker", "Please select a speaker first.")
            return
            
        if not tag:
            messagebox.showwarning("No Tag", "Please enter a tag name.")
            return
        
        # Convert display name back to actual speaker name
        if display_name == "Single Speaker":
            actual_speaker = ""
        else:
            actual_speaker = display_name
            
        # Add tag
        self.speaker_service.add_tag_to_speaker(self.model_name, actual_speaker, tag)
        
        # Update displays
        self.update_current_tags_display(actual_speaker)
        self.populate_speakers_tree()
        self.populate_existing_tags()
        
        # Clear input
        self.new_tag_var.set("")
        
        # Reselect current speaker
        for item in self.speakers_tree.get_children():
            if self.speakers_tree.item(item)['values'][0] == display_name:
                self.speakers_tree.selection_set(item)
                break
                
    def add_existing_tag(self):
        """Add an existing tag to the selected speaker"""
        display_name = self.selected_speaker_label.cget("text")
        selection = self.existing_tags_listbox.curselection()
        
        if display_name == "None":
            messagebox.showwarning("No Speaker", "Please select a speaker first.")
            return
            
        if not selection:
            messagebox.showwarning("No Tag", "Please select a tag to add.")
            return
        
        # Convert display name back to actual speaker name
        if display_name == "Single Speaker":
            actual_speaker = ""
        else:
            actual_speaker = display_name
            
        tag = self.existing_tags_listbox.get(selection[0])
        
        # Add tag
        self.speaker_service.add_tag_to_speaker(self.model_name, actual_speaker, tag)
        
        # Update displays
        self.update_current_tags_display(actual_speaker)
        self.populate_speakers_tree()
        
        # Reselect current speaker
        for item in self.speakers_tree.get_children():
            if self.speakers_tree.item(item)['values'][0] == display_name:
                self.speakers_tree.selection_set(item)
                break
                
    def remove_selected_tag(self):
        """Remove the selected tag from the current speaker"""
        display_name = self.selected_speaker_label.cget("text")
        selection = self.current_tags_listbox.curselection()
        
        if display_name == "None":
            messagebox.showwarning("No Speaker", "Please select a speaker first.")
            return
            
        if not selection:
            messagebox.showwarning("No Tag", "Please select a tag to remove.")
            return
        
        # Convert display name back to actual speaker name
        if display_name == "Single Speaker":
            actual_speaker = ""
        else:
            actual_speaker = display_name
            
        tag = self.current_tags_listbox.get(selection[0])
        
        # Remove tag
        if self.speaker_service.remove_tag_from_speaker(self.model_name, actual_speaker, tag):
            # Update displays
            self.update_current_tags_display(actual_speaker)
            self.populate_speakers_tree()
            
            # Reselect current speaker
            for item in self.speakers_tree.get_children():
                if self.speakers_tree.item(item)['values'][0] == display_name:
                    self.speakers_tree.selection_set(item)
                    break
        else:
            messagebox.showwarning("Tag Not Found", f"Speaker '{display_name}' doesn't have tag '{tag}'")
            
    def add_tag_definition(self):
        """Add a new global tag definition"""
        tag_name = self.new_tag_def_var.get().strip()
        if not tag_name:
            messagebox.showwarning("No Tag Name", "Please enter a tag name.")
            return
        # Prevent model names or single letters (optional)
        if "/" in tag_name or len(tag_name) == 1:
            messagebox.showwarning("Invalid Tag", "Tag names cannot be model names or single letters.")
            return
        if tag_name in self.speaker_service.get_all_tags():
            messagebox.showwarning("Tag Exists", f"Tag '{tag_name}' already exists.")
            return
        self.speaker_service.add_tag_definition(tag_name, f"Tag: {tag_name}", "#808080")
        self.populate_existing_tags()
        self.new_tag_def_var.set("")
        messagebox.showinfo("Success", f"Tag definition '{tag_name}' created successfully.")
            
    def save_changes(self):
        """Save changes and close dialog"""
        self.result = True
        self.destroy()
        
    def cancel(self):
        """Cancel changes and close dialog"""
        self.result = False
        self.destroy()
    
    def set_speaker_rating(self):
        """Set rating for the selected speaker"""
        display_name = self.selected_speaker_label.cget("text")
        rating = self.rating_var.get()
        
        if display_name == "None":
            messagebox.showwarning("No Speaker", "Please select a speaker first.")
            return
            
        if rating < 0.0 or rating > 5.0:
            messagebox.showwarning("Invalid Rating", "Rating must be between 0.0 and 5.0.")
            return
        
        # Convert display name back to actual speaker name
        if display_name == "Single Speaker":
            actual_speaker = ""
        else:
            actual_speaker = display_name
            
        # Set rating
        if self.speaker_service.set_speaker_rating(self.model_name, actual_speaker, rating):
            # Update displays
            self.update_current_rating_display(actual_speaker)
            self.populate_speakers_tree()
            
            # Reselect current speaker
            for item in self.speakers_tree.get_children():
                if self.speakers_tree.item(item)['values'][0] == display_name:
                    self.speakers_tree.selection_set(item)
                    break
                    
            messagebox.showinfo("Success", f"Rating set to {rating:.1f} for speaker '{display_name}'")
        else:
            messagebox.showerror("Error", "Failed to set rating.")
    
    def remove_speaker_rating(self):
        """Remove rating for the selected speaker"""
        display_name = self.selected_speaker_label.cget("text")
        
        if display_name == "None":
            messagebox.showwarning("No Speaker", "Please select a speaker first.")
            return
        
        # Convert display name back to actual speaker name
        if display_name == "Single Speaker":
            actual_speaker = ""
        else:
            actual_speaker = display_name
            
        # Remove rating
        if self.speaker_service.remove_speaker_rating(self.model_name, actual_speaker):
            # Update displays
            self.update_current_rating_display(actual_speaker)
            self.populate_speakers_tree()
            self.rating_var.set(0.0)
            
            # Reselect current speaker
            for item in self.speakers_tree.get_children():
                if self.speakers_tree.item(item)['values'][0] == display_name:
                    self.speakers_tree.selection_set(item)
                    break
                    
            messagebox.showinfo("Success", f"Rating removed for speaker '{display_name}'")
        else:
            messagebox.showwarning("No Rating", f"Speaker '{display_name}' doesn't have a rating to remove.")
    
    def update_current_rating_display(self, speaker):
        """Update the current rating display for a speaker"""
        rating = self.speaker_service.get_speaker_rating(self.model_name, speaker)
        if rating > 0.0:
            self.current_rating_label.config(text=f"{rating:.1f}/5.0")
            self.rating_var.set(rating)
        else:
            self.current_rating_label.config(text="No rating")
            self.rating_var.set(0.0) 