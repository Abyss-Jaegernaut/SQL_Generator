import os
import sys
import tkinter as tk
from tkinter import messagebox

from controllers.app_controller import AppController
from data.storage import Storage
from ui.main_window import MainWindow

def run_app() -> None:
    try:
        root = tk.Tk()
        root.title("SQL Generator CRUD")
        root.geometry("600x550")
        
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
