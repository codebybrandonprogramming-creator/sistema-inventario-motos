import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class GitAutoPushHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        try:
            print("\nDetectado cambio. Procesando...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Auto-commit: cambios detectados"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("Cambios subidos a GitHub.")
        except subprocess.CalledProcessError:
            print("No hay cambios nuevos para subir.")

if __name__ == "__main__":
    path = "."
    event_handler = GitAutoPushHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("🔵 Sistema automático activado.")
    print("Cada vez que guardes un archivo, se subirá solo a GitHub.")
    print("Para detenerlo presiona CTRL + C.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
