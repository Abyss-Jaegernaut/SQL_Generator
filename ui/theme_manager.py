import tkinter as tk
from tkinter import ttk

class Theme:
    def __init__(self, name, bg, fg, accent, border, tree_bg, tree_fg, tree_selected_bg, tree_selected_fg, 
                 syntax_colors, input_bg=None, button_bg=None, card_bg=None):
        self.name = name
        self.bg = bg
        self.fg = fg
        self.accent = accent
        self.border = border
        self.tree_bg = tree_bg
        self.tree_fg = tree_fg
        self.tree_selected_bg = tree_selected_bg
        self.tree_selected_fg = tree_selected_fg
        self.syntax_colors = syntax_colors
        self.input_bg = input_bg if input_bg else tree_bg
        self.button_bg = button_bg if button_bg else border
        self.card_bg = card_bg if card_bg else bg

THEMES = {
    "Abyss": Theme(
        name="Abyss",
        bg="#0f172a",          # Very dark blue background
        fg="#f8fafc",          # Almost white text
        accent="#6366f1",      # Indigo accent
        border="#1e293b",      # Subtle borders
        tree_bg="#1e293b",     # Darker area for lists/trees
        tree_fg="#cbd5e1",
        tree_selected_bg="#334155",
        tree_selected_fg="#ffffff",
        syntax_colors={
            "keyword": "#c678dd",    # Purple
            "identifier": "#e5c07b", # Gold
            "type": "#61afef",       # Bright Blue
            "string": "#98c379",     # Green
            "comment": "#5c6370",    # Gray
        },
        input_bg="#1e293b",
        button_bg="#1e293b",
        card_bg="#1e293b"
    ),
    "Sombre": Theme(
        name="Sombre",
        bg="#18181b",
        fg="#fafafa",
        accent="#3f3f46",
        border="#27272a",
        tree_bg="#18181b",
        tree_fg="#d4d4d8",
        tree_selected_bg="#3f3f46",
        tree_selected_fg="#ffffff",
        syntax_colors={
            "keyword": "#3b82f6",    # Blue
            "identifier": "#f59e0b", # Amber
            "type": "#60a5fa",       # Light Blue
            "string": "#10b981",     # Teal
            "comment": "#64748b",    # Slate
        },
        input_bg="#09090b"
    ),
    "Violet": Theme(
        name="Violet",
        bg="#130a21",          # Deep dark purple
        fg="#f3e8ff",          # Purple 100
        accent="#d946ef",      # Fuchsia 500
        border="#4a044e",      # Fuchsia 950/Dark border
        tree_bg="#221236",     # Dark purple layer
        tree_fg="#e9d5ff",     # Purple 200
        tree_selected_bg="#701a75",
        tree_selected_fg="#ffffff",
        syntax_colors={
            "keyword": "#e879f9",
            "identifier": "#fcd34d",
            "type": "#60a5fa",
            "string": "#4ade80",
            "comment": "#705275",
        },
        input_bg="#221236"
    ),
    "Orange": Theme(
        name="Orange",
        bg="#1c110a",          # Very dark brown/orange
        fg="#ffedd5",          # Orange 100
        accent="#f97316",      # Orange 500
        border="#431407",      # Orange 950
        tree_bg="#351a10",     # Dark brown layer
        tree_fg="#fdba74",     # Orange 300
        tree_selected_bg="#9a3412",
        tree_selected_fg="#ffffff",
        syntax_colors={
            "keyword": "#fb923c",
            "identifier": "#fbbf24",
            "type": "#38bdf8",
            "string": "#a3e635",
            "comment": "#786158",
        },
        input_bg="#351a10"
    ),
    "Jaune": Theme(
        name="Jaune",
        bg="#1a1608",         # Dark olive/yellow
        fg="#fefce8",         # Yellow 50
        accent="#eab308",     # Yellow 500
        border="#422006",     # Brownish border
        tree_bg="#2e260e",    # Olive layer
        tree_fg="#fde047",    # Yellow 300
        tree_selected_bg="#854d0e",
        tree_selected_fg="#ffffff",
        syntax_colors={
            "keyword": "#facc15",
            "identifier": "#fbbf24",
            "type": "#60a5fa",
            "string": "#a3e635",
            "comment": "#635f45",
        },
        input_bg="#2e260e"
    ),
    "Clair": Theme(
        name="Clair",
        bg="#f1f5f9",
        fg="#0f172a",
        accent="#3b82f6",
        border="#e2e8f0",
        tree_bg="#ffffff",
        tree_fg="#1e293b",
        tree_selected_bg="#dbeafe",
        tree_selected_fg="#1e3a8a",
        syntax_colors={
            "keyword": "#0000ff",    # Classic Blue
            "identifier": "#267f99", # Teal/Navy
            "type": "#795e26",       # Brown/Gold
            "string": "#a31515",     # Dark Red
            "comment": "#008000",    # Classic Green
        },
        button_bg="#ffffff"
    ),
}

class ThemeManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            # Default to Clair as requested
            cls._instance.current_theme = THEMES["Clair"]
        return cls._instance

    def apply_theme(self, theme_name, root):
        if theme_name not in THEMES:
            theme_name = "Clair"
        
        theme = THEMES[theme_name]
        self.current_theme = theme
        
        style = ttk.Style()
        
        # Base theme setup
        current_themes = style.theme_names()
        if "clam" in current_themes:
            style.theme_use("clam")

        # Configure generic classes
        style.configure("TFrame", background=theme.bg)
        style.configure("TLabelframe", background=theme.bg, foreground=theme.accent, font=("Segoe UI", 10, "bold"), bordercolor=theme.border)
        style.configure("TLabelframe.Label", background=theme.bg, foreground=theme.accent)
        
        style.configure("TLabel", background=theme.bg, foreground=theme.fg, font=("Segoe UI", 9))
        
        # Button styling
        style.configure("TButton", 
                        background=theme.button_bg, 
                        foreground=theme.fg, 
                        bordercolor=theme.border,
                        focuscolor=theme.accent,
                        relief="flat",
                        padding=(15, 8),
                        font=("Segoe UI", 9, "bold"))
        
        style.map("TButton",
                  background=[('active', theme.accent), ('pressed', theme.accent)],
                  foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])

        # Specific accent button style
        style.configure("Accent.TButton", background=theme.accent, foreground="#ffffff")

        # Checkbutton (ttk) - though we are using tk.Checkbutton for procedures
        style.configure("TCheckbutton", background=theme.bg, foreground=theme.fg, font=("Segoe UI", 9))
        style.map("TCheckbutton", background=[('active', theme.bg)])
        
        # Entry and Combobox
        style.configure("TEntry", 
                        fieldbackground=theme.input_bg, 
                        foreground=theme.fg, 
                        insertcolor=theme.fg,
                        bordercolor=theme.border,
                        lightcolor=theme.border,
                        darkcolor=theme.border,
                        padding=5)
        
        style.configure("TCombobox", 
                        fieldbackground=theme.input_bg, 
                        foreground=theme.fg, 
                        selectbackground=theme.accent,
                        padding=5)

        # TSpinbox
        style.configure("TSpinbox", 
                        fieldbackground=theme.input_bg, 
                        background=theme.input_bg,
                        foreground=theme.fg, 
                        arrowcolor=theme.fg, 
                        bordercolor=theme.border,
                        lightcolor=theme.border,
                        darkcolor=theme.border,
                        padding=2)
        style.map("TSpinbox",
                  fieldbackground=[('readonly', theme.input_bg)],
                  background=[('readonly', theme.input_bg)],
                  foreground=[('readonly', theme.fg)])

        # Treeview
        style.configure("Treeview", 
                        background=theme.tree_bg, 
                        foreground=theme.tree_fg, 
                        fieldbackground=theme.tree_bg,
                        font=("Segoe UI", 9), 
                        rowheight=30,
                        borderwidth=0)
        style.map("Treeview", 
                  background=[('selected', theme.tree_selected_bg)],
                  foreground=[('selected', theme.tree_selected_fg)])
        style.configure("Treeview.Heading", 
                        background=theme.border,
                        foreground=theme.fg,
                        relief="flat",
                        padding=5,
                        font=("Segoe UI", 9, "bold"))

        # Scrollbar
        style.configure("TScrollbar", gripcount=0, background=theme.border, darkcolor=theme.bg, lightcolor=theme.bg, bordercolor=theme.bg, troughcolor=theme.bg)

        # Root background
        root.configure(bg=theme.bg)
        
        self.refresh_theme(root)

    def refresh_theme(self, widget=None):
        """Apply the currently selected theme to the widget and all its children."""
        if widget is None:
            # We don't have a direct reference to root here if not passed, 
            # but usually it's passed.
            return
        self._update_all_widgets(widget, self.current_theme)

    def _update_all_widgets(self, widget, theme):
        try:
            classname = widget.winfo_class()
            
            if classname == "Text":
                widget.configure(
                    bg="#0a0f1d" if theme.name == "Abyss" else theme.input_bg, 
                    fg=theme.fg, 
                    insertbackground=theme.fg, 
                    relief="flat", 
                    padx=10,
                    pady=10,
                    highlightbackground=theme.border,
                    highlightcolor=theme.accent,
                    highlightthickness=1
                )
                # Re-apply syntax highlighting if it's the Preview Frame
                # Since we don't have direct access to the SQLPreviewFrame instance easily here,
                # the apply_theme caller in MainWindow and SQLPreviewFrame itself will handle it.
                
            elif classname == "Frame":
                widget.configure(bg=theme.bg)
            elif classname == "Label":
                widget.configure(bg=theme.bg, fg=theme.fg)
            elif classname == "Canvas":
                widget.configure(bg=theme.bg, highlightthickness=0)
            elif classname == "Listbox":
                widget.configure(
                    bg=theme.input_bg, # Pure white for Clair
                    fg=theme.fg, 
                    selectbackground=theme.accent, 
                    selectforeground="#ffffff",
                    highlightthickness=1,
                    highlightbackground=theme.border,
                    relief="flat" if theme.name != "Clair" else "sunken",
                    font=("Segoe UI", 10)
                )
            elif classname == "Checkbutton":
                # Standard tk.Checkbutton
                widget.configure(
                    bg=theme.bg, 
                    fg=theme.fg, 
                    selectcolor=theme.input_bg if theme.name != "Clair" else "#ffffff",
                    activebackground=theme.bg,
                    activeforeground=theme.accent,
                    font=("Segoe UI", 9)
                )
            elif classname == "Menu":
                 widget.configure(bg=theme.bg, fg=theme.fg, activebackground=theme.accent, activeforeground="#ffffff")
        except:
            pass

        for child in widget.winfo_children():
            self._update_all_widgets(child, theme)
