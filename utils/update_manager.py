import urllib.request
import json
import webbrowser
import threading
from tkinter import messagebox

# URL where the version.json will be hosted
VERSION_CHECK_URL = "https://raw.githubusercontent.com/Abyss-Jaegernaut/SQL_Generator/main/version.json" 

def check_for_updates(current_version):
    """Checks for updates in a background thread."""
    thread = threading.Thread(target=lambda: _perform_check(current_version))
    thread.daemon = True
    thread.start()

def _perform_check(current_version):
    try:
        # Request with a User-Agent to avoid being blocked by some servers
        req = urllib.request.Request(
            VERSION_CHECK_URL, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("version")
            download_url = data.get("url")
            
            if latest_version and _is_newer(latest_version, current_version):
                if messagebox.askyesno("Mise à jour disponible", 
                    f"Une nouvelle version ({latest_version}) est disponible.\n"
                    f"Version actuelle : {current_version}\n\n"
                    "Souhaitez-vous ouvrir la page de téléchargement ?"):
                    webbrowser.open(download_url)
    except Exception:
        # Fail silently if offline or server error
        pass

def _is_newer(latest, current):
    """Simple version comparison."""
    try:
        l_parts = [int(p) for p in latest.split('.')]
        c_parts = [int(p) for p in current.split('.')]
        return l_parts > c_parts
    except:
        return latest > current
