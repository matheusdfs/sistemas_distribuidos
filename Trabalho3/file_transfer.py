# file_transfer.py
import Pyro5.api

@Pyro5.api.expose
class FileTransferService:
    def __init__(self, files_dir):
        self.files_dir = files_dir

    def get_file(self, filename):
        try:
            with open(f"{self.files_dir}/{filename}", "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def save_file(self, filename, content):
        with open(f"{self.files_dir}/{filename}", "wb") as f:
            f.write(content)
        print(f"[Transferência] Arquivo '{filename}' salvo.")
