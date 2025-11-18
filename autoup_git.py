import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

IGNORAR = [
    '.git',
    '__pycache__',
    'autoup_git.py',
    '.idea',
    '.vscode',
    'instance',
    '.env'
]

class GitAutoPushHandler(FileSystemEventHandler):
    def on_any_event(self, event):

        # Ignorar archivos/carpetas que no deben activar commits
        for ignore in IGNORAR:
            if ignore in event.src_path.replace("\\", "/"):
                return

        try:
            print("\nDetectado cambio. Procesando...")

            # Añadir archivos al staging
            subprocess.run(["git", "add", "."], check=True)

            # Verificar si realmente hay cambios
            estado = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if estado.stdout.strip() == "":
                print("No hay cambios nuevos para subir.")
                return

            # Commit
            subprocess.run(["git", "commit", "-m", "Auto-commit: cambios detectados"], check=True)

            # Push
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
    print("Cada vez que guardes un archivo REAL del proyecto, se subirá a GitHub.")
    print("Para detenerlo presiona CTRL + C.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

