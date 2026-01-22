import os
import sys
import tkinter as tk

from controllers.app_controller import AppController
from data.storage import Storage
from ui.main_window import MainWindow


def run_app() -> None:
    """Initialize application dependencies and start the tkinter loop."""
    root = tk.Tk()
    root.title("SQL Generator CRUD")
    
    # Set window icon if available
    icon_path = "icon.ico"
    if getattr(sys, 'frozen', False):
        # If running as bundle (PyInstaller)
        try:
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        except AttributeError:
            # _MEIPASS might not exist in some contexts
            icon_path = "icon.ico"
    
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            # Silently ignore icon loading issues
            pass

    try:
        storage = Storage(db_path="sql_generator.db")
        controller = AppController(storage=storage)

        # Show activation dialog on startup if not activated
        if not controller.is_activated():
            from ui.license_dialog import LicenseDialog
            dialog = LicenseDialog(root, controller)
            root.wait_window(dialog)

        MainWindow(master=root, controller=controller)
        root.mainloop()
    except Exception as e:
        # Display critical error to user before exiting
        try:
            tk.messagebox.showerror("Erreur Critique", f"L'application n'a pas pu démarrer.\nErreur: {str(e)}")
        except:
            # If GUI fails completely, at least print to console
            print(f"Critical error: {e}")
        finally:
            sys.exit(1)


if __name__ == "__main__":
    run_app()