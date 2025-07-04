"""
Theme Manager Component
Handles dark theme styling for the TTS Tester GUI.
"""

import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """Manages dark theme styling for the application"""
    
    def __init__(self):
        # Dark theme colors - matching original exactly
        self.colors = {
            'bg': '#2b2b2b',           # Dark background
            'fg': '#ffffff',            # White text
            'accent': '#4a9eff',        # Blue accent
            'button_bg': '#404040',     # Button background
            'button_fg': '#ffffff',     # Button text
            'entry_bg': '#3c3c3c',      # Entry background
            'entry_fg': '#ffffff',      # Entry text
            'listbox_bg': '#3c3c3c',    # Listbox background
            'listbox_fg': '#ffffff',    # Listbox text
            'listbox_select_bg': '#4a9eff',  # Listbox selection background
            'listbox_select_fg': '#ffffff',  # Listbox selection text
            'tree_bg': '#3c3c3c',       # Treeview background
            'tree_fg': '#ffffff',       # Treeview text
            'tree_select_bg': '#4a9eff', # Treeview selection background
            'tree_select_fg': '#ffffff', # Treeview selection text
            'frame_bg': '#2b2b2b',      # Frame background
            'label_bg': '#2b2b2b',      # Label background
            'label_fg': '#ffffff',      # Label text
        }
        
    def apply_dark_theme(self, root):
        """Apply dark theme to the root window and all widgets"""
        # Configure root window
        root.configure(bg=self.colors['bg'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme as base like original
        
        # Configure common styles - matching original exactly
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabelframe', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', 
                       background=self.colors['button_bg'], 
                       foreground=self.colors['button_fg'],
                       borderwidth=1,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', self.colors['accent']), ('pressed', '#3a7bd5')],
                 foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])
        
        # Configure entry and combobox
        style.configure('TEntry', 
                       fieldbackground=self.colors['entry_bg'],
                       foreground=self.colors['entry_fg'],
                       borderwidth=1,
                       focuscolor=self.colors['accent'])
        style.configure('TCombobox', 
                       fieldbackground=self.colors['entry_bg'],
                       foreground=self.colors['entry_fg'],
                       background=self.colors['entry_bg'],
                       borderwidth=1,
                       focuscolor=self.colors['accent'])
        style.map('TCombobox',
                 fieldbackground=[('readonly', self.colors['entry_bg'])],
                 selectbackground=[('readonly', self.colors['listbox_select_bg'])],
                 selectforeground=[('readonly', self.colors['listbox_select_fg'])])
        
        # Configure scrollbar
        style.configure('Vertical.TScrollbar',
                       background=self.colors['button_bg'],
                       troughcolor=self.colors['bg'],
                       borderwidth=0,
                       arrowcolor=self.colors['fg'])
        style.map('Vertical.TScrollbar',
                 background=[('active', self.colors['accent']), ('pressed', '#3a7bd5')])
        
        # Configure Treeview
        style.configure('Treeview', 
                       background=self.colors['tree_bg'],
                       foreground=self.colors['tree_fg'],
                       fieldbackground=self.colors['tree_bg'])
        style.configure('Treeview.Heading',
                       background=self.colors['button_bg'],
                       foreground=self.colors['button_fg'])
        style.map('Treeview',
                 background=[('selected', self.colors['tree_select_bg'])],
                 foreground=[('selected', self.colors['tree_select_fg'])])
        
        # Configure Checkbutton and Radiobutton
        style.configure('TCheckbutton', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TRadiobutton', background=self.colors['bg'], foreground=self.colors['fg'])
        
        # Apply theme to all existing widgets recursively
        self._apply_theme_recursive(root)
        
    def _apply_theme_recursive(self, widget):
        """Recursively apply theme to all widgets"""
        try:
            # Apply theme based on widget type
            if isinstance(widget, tk.Listbox):
                widget.configure(
                    bg=self.colors['listbox_bg'],
                    fg=self.colors['listbox_fg'],
                    selectbackground=self.colors['listbox_select_bg'],
                    selectforeground=self.colors['listbox_select_fg'],
                    insertbackground=self.colors['fg']
                )
            elif isinstance(widget, tk.Text):
                widget.configure(
                    bg=self.colors['entry_bg'],
                    fg=self.colors['entry_fg'],
                    insertbackground=self.colors['fg'],
                    selectbackground=self.colors['listbox_select_bg'],
                    selectforeground=self.colors['listbox_select_fg']
                )
            elif isinstance(widget, tk.Entry):
                widget.configure(
                    bg=self.colors['entry_bg'],
                    fg=self.colors['entry_fg'],
                    insertbackground=self.colors['fg'],
                    selectbackground=self.colors['listbox_select_bg'],
                    selectforeground=self.colors['listbox_select_fg']
                )
            elif isinstance(widget, tk.Label):
                widget.configure(
                    bg=self.colors['bg'],
                    fg=self.colors['fg']
                )
            elif isinstance(widget, tk.Button):
                widget.configure(
                    bg=self.colors['button_bg'],
                    fg=self.colors['button_fg'],
                    activebackground=self.colors['accent'],
                    activeforeground='#ffffff'
                )
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=self.colors['bg'])
            elif isinstance(widget, tk.Toplevel):
                widget.configure(bg=self.colors['bg'])
                
        except Exception:
            # Ignore errors for widgets that don't support certain configurations
            pass
            
        # Recursively apply to children
        for child in widget.winfo_children():
            self._apply_theme_recursive(child)
            
    def get_colors(self):
        """Get the current theme colors"""
        return self.colors.copy() 