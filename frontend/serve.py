from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os


ROOT = Path(__file__).resolve().parent / "dist"


# Serves index.html for frontend routes like /login and /requirements.
class SpaHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        requested = ROOT / path.lstrip("/")
        if requested.exists():
            return str(requested)

        if "." not in Path(path).name:
            return str(ROOT / "index.html")

        return str(requested)


if __name__ == "__main__":
    os.chdir(ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", 5174), SpaHandler)
    print("Serving frontend at http://127.0.0.1:5174")
    server.serve_forever()
