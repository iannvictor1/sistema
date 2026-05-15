import os
import sys
import time
import socket
import webbrowser
import subprocess
import urllib.error
import urllib.request


# =========================
# PATHS (script vs exe)
# =========================

def get_runtime_dir() -> str:
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS
        return os.path.join(os.path.dirname(sys.executable), "_internal")
    return os.path.dirname(os.path.abspath(__file__))


def get_work_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_launcher_command(mode: str) -> list[str]:
    """
    Garante que funcione tanto no:
    - python run_system.py
    - run_system.exe
    """
    if getattr(sys, "frozen", False):
        return [sys.executable, mode]
    return [sys.executable, os.path.abspath(__file__), mode]


RUNTIME_DIR = get_runtime_dir()
WORK_DIR = get_work_dir()


# =========================
# UTIL
# =========================

def porta_em_uso(porta: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", porta)) == 0


def esperar_porta(porta: int, timeout: int = 90) -> bool:
    inicio = time.time()
    while time.time() - inicio < timeout:
        if porta_em_uso(porta):
            return True
        time.sleep(0.5)
    return False


def backend_do_sistema_respondendo() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as response:
            if response.status != 200:
                return False
            return b"Sistema rodando" in response.read(300)
    except (OSError, urllib.error.URLError):
        return False


def esperar_backend_sistema(timeout: int = 90) -> bool:
    inicio = time.time()
    while time.time() - inicio < timeout:
        if backend_do_sistema_respondendo():
            return True
        time.sleep(0.5)
    return False


# =========================
# BACKEND (FastAPI)
# =========================

def rodar_backend() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


# =========================
# FRONTEND (Streamlit)
# =========================

def rodar_frontend() -> None:
    from streamlit.web.cli import main as stcli

    frontend_path = os.path.join(RUNTIME_DIR, "frontend", "app.py")

    if not os.path.exists(frontend_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {frontend_path}")

    sys.argv = [
        "streamlit",
        "run",
        frontend_path,
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]

    sys.exit(stcli())


# =========================
# LAUNCHER (coordena tudo)
# =========================

def rodar_launcher() -> None:
    backend = None
    frontend = None

    # Sobe backend
    if not porta_em_uso(8000):
        backend = subprocess.Popen(get_launcher_command("--backend"), cwd=WORK_DIR)
    elif not backend_do_sistema_respondendo():
        raise RuntimeError(
            "A porta 8000 ja esta em uso, mas nao parece ser o backend deste sistema. "
            "Feche o processo que esta usando a porta 8000 e abra o sistema novamente."
        )

    if not esperar_backend_sistema(timeout=30):
        raise RuntimeError("Backend nao subiu corretamente na porta 8000.")

    # Sobe frontend
    if not porta_em_uso(8501):
        frontend = subprocess.Popen(get_launcher_command("--frontend"), cwd=WORK_DIR)

    if not esperar_porta(8501, timeout=90):
        raise RuntimeError("Frontend não subiu na porta 8501.")

    # Abre navegador UMA VEZ
    webbrowser.open("http://127.0.0.1:8501")

    try:
        if backend:
            backend.wait()
        if frontend:
            frontend.wait()
    except KeyboardInterrupt:
        if backend:
            backend.terminate()
        if frontend:
            frontend.terminate()


# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    if "--backend" in sys.argv:
        rodar_backend()
    elif "--frontend" in sys.argv:
        rodar_frontend()
    else:
        rodar_launcher()
