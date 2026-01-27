from __future__ import annotations

import tkinter as tk
from ui.license_page import LicensePage


class LicenseDialog(tk.Toplevel):
    """Dialog wrapper around LicensePage."""

    def __init__(self, master, controller) -> None:
        super().__init__(master)
        self.controller = controller
        self.title("Activation de Licence")
        self.geometry("500x480")
        self.resizable(False, False)
        
        self.transient(master)
        self.grab_set()

        # Place the LicensePage frame
        self.page = LicensePage(self, controller, on_success=self._on_success)
        self.page.pack(fill="both", expand=True)

        self.success = False
        
        # Center manually without complex withdraw logic
        self.update_idletasks()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (500/2)
        y = (hs/2) - (480/2)
        self.geometry('+%d+%d' % (x, y))

    def _on_success(self):
        self.success = True
        self.destroy()
