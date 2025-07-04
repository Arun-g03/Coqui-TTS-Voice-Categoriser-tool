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
        columns = ('speaker', 'tags')
        self.speakers_tree = ttk.Treeview(speakers_frame, columns=columns, show='tree headings', height=15)
        self.speakers_tree.heading('speaker', text='Speaker')
        self.speakers_tree.heading('tags', text='Tags')
        self.speakers_tree.column('speaker', width=200)
        self.speakers_tree.column('tags', width=300)
        
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
        
        # Add tag section
        add_tag_frame = ttk.LabelFrame(right_frame, text="Add Tag")
        add_tag_frame.pack(fill='x', padx=5, pady=5)
        
        # Tag input
        tag_input_frame = ttk.Frame(add_tag_frame)
        tag_input_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(tag_input_frame, text="Tag Name:").pack(side='left')
        self.new_tag_var = tk.StringVar()
        tag_entry = ttk.Entry(tag_input_frame, textvariable=self.new_tag_var)
        tag_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Add tag button
        add_tag_btn = ttk.Button(add_tag_frame, text="Add Tag", command=self.add_tag_to_speaker)
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
            tags = self.speaker_service.get_speaker_tags(self.model_name, speaker)
            tags_str = ", ".join(tags) if tags else "No tags"
            self.speakers_tree.insert('', 'end', values=(speaker, tags_str))
            
    def populate_existing_tags(self):
        """Populate the existing tags listbox"""
        self.existing_tags_listbox.delete(0, tk.END)
        all_tags = self.speaker_service.get_all_tags_for_model(self.model_name)
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
            # Apply search filter
            if search_text and search_text not in speaker.lower():
                continue
                
            # Apply tag filter
            tags = self.speaker_service.get_speaker_tags(self.model_name, speaker)
            if filter_type == "tagged" and not tags:
                continue
            elif filter_type == "untagged" and tags:
                continue
                
            tags_str = ", ".join(tags) if tags else "No tags"
            self.speakers_tree.insert('', 'end', values=(speaker, tags_str))
            
    def on_filter_change(self):
        """Handle filter radio button change"""
        self.on_search_change()
        
    def on_speaker_select(self, event):
        """Handle speaker selection"""
        selection = self.speakers_tree.selection()
        if selection:
            item = self.speakers_tree.item(selection[0])
            speaker = item['values'][0]
            self.selected_speaker_label.config(text=speaker)
            self.update_current_tags_display(speaker)
        else:
            self.selected_speaker_label.config(text="None")
            self.current_tags_listbox.delete(0, tk.END)
            
    def update_current_tags_display(self, speaker):
        """Update the current tags display for a speaker"""
        self.current_tags_listbox.delete(0, tk.END)
        tags = self.speaker_service.get_speaker_tags(self.model_name, speaker)
        for tag in sorted(tags):
            self.current_tags_listbox.insert(tk.END, tag)
            
    def add_tag_to_speaker(self):
        """Add a new tag to the selected speaker"""
        speaker = self.selected_speaker_label.cget("text")
        tag = self.new_tag_var.get().strip()
        
        if speaker == "None":
            messagebox.showwarning("No Speaker", "Please select a speaker first.")
            return
            
        if not tag:
            messagebox.showwarning("No Tag", "Please enter a tag name.")
            return
            
        # Add tag
        self.speaker_service.add_tag_to_speaker(self.model_name, speaker, tag)
        
        # Update displays
        self.update_current_tags_display(speaker)
        self.populate_speakers_tree()
        self.populate_existing_tags()
        
        # Clear input
        self.new_tag_var.set("")
        
        # Reselect current speaker
        for item in self.speakers_tree.get_children():
            if self.speakers_tree.item(item)['values'][0] == speaker:
                self.speakers_tree.selection_set(item)
                break
                
    def add_existing_tag(self):
        """Add an existing tag to the selected speaker"""
        speaker = self.selected_speaker_label.cget("text")
        selection = self.existing_tags_listbox.curselection()
        
        if speaker == "None":
            messagebox.showwarning("No Speaker", "Please select a speaker first.")
            return
            
        if not selection:
            messagebox.showwarning("No Tag", "Please select a tag to add.")
            return
            
        tag = self.existing_tags_listbox.get(selection[0])
        
        # Add tag
        self.speaker_service.add_tag_to_speaker(self.model_name, speaker, tag)
        
        # Update displays
        self.update_current_tags_display(speaker)
        self.populate_speakers_tree()
        
        # Reselect current speaker
        for item in self.speakers_tree.get_children():
            if self.speakers_tree.item(item)['values'][0] == speaker:
                self.speakers_tree.selection_set(item)
                break
                
    def remove_selected_tag(self):
        """Remove the selected tag from the current speaker"""
        speaker = self.selected_speaker_label.cget("text")
        selection = self.current_tags_listbox.curselection()
        
        if speaker == "None":
            messagebox.showwarning("No Speaker", "Please select a speaker first.")
            return
            
        if not selection:
            messagebox.showwarning("No Tag", "Please select a tag to remove.")
            return
            
        tag = self.current_tags_listbox.get(selection[0])
        
        # Remove tag
        if self.speaker_service.remove_tag_from_speaker(self.model_name, speaker, tag):
            # Update displays
            self.update_current_tags_display(speaker)
            self.populate_speakers_tree()
            
            # Reselect current speaker
            for item in self.speakers_tree.get_children():
                if self.speakers_tree.item(item)['values'][0] == speaker:
                    self.speakers_tree.selection_set(item)
                    break
        else:
            messagebox.showwarning("Tag Not Found", f"Speaker '{speaker}' doesn't have tag '{tag}'")
            
    def save_changes(self):
        """Save changes and close dialog"""
        self.result = True
        self.destroy()
        
    def cancel(self):
        """Cancel changes and close dialog"""
        self.result = False
        self.destroy() 