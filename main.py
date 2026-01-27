import os
import sys
import tkinter as tk
from tkinter import messagebox

from controllers.app_controller import AppController
from data.storage import Storage
from ui.main_window import MainWindow
from ui.theme_manager import ThemeManager
from utils.update_manager import check_for_updates
from version import VERSION

def run_app() -> None:
    try:
        root = tk.Tk()
        root.title("SQL Generator CRUD")
        
        # Adaptive UI: Calculate size based on screen (80% of screen width/height, capped)
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        
        width = min(1200, int(screen_w * 0.85))
        height = min(800, int(screen_h * 0.85))
        
        # Center the window
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.minsize(900, 650) # Prevent window from being too small
        
        # Set window icon
        icon_path = "icon.ico"
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        
        if os.path.exists(icon_path):
            try:
                root.iconbitmap(icon_path)
            except:
                pass

        storage = Storage(db_path="sql_generator.db")
        controller = AppController(storage=storage)
        
        # Apply theme early
        theme_manager = ThemeManager()
        theme_manager.apply_theme(controller.get_theme(), root)
        
        # Check for updates in background
        check_for_updates(VERSION)

        def launch_main():
            # Clear root
            for widget in root.winfo_children():
                widget.destroy()
            
            # Reset menu if any
            root.config(menu="")
            MainWindow(master=root, controller=controller)

        if not controller.is_activated():
            from ui.license_page import LicensePage
            page = LicensePage(root, controller, on_success=launch_main)
            page.pack(fill="both", expand=True)
        else:
            launch_main()

        root.mainloop()
    except Exception as e:
        try:
            messagebox.showerror("Erreur Critique", f"Impossible de lancer l'application.\n{e}")
        except:
            print(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_app()
