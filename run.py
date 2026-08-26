import os
import sys
import subprocess
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    # Locate virtual environment Python if available
    venv_python = os.path.join(backend_dir, ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    print("==================================================")
    print(" Starting E-commerce Chatbot App")
    print("==================================================")
    
    print("\n[1/2] Starting Backend (FastAPI)...")
    backend_cmd = [venv_python, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]
    backend_process = subprocess.Popen(backend_cmd, cwd=backend_dir)

    print("[2/2] Starting Frontend (Next.js)...")
    npm_bin = "npm.cmd" if os.name == "nt" else "npm"
    frontend_cmd = [npm_bin, "run", "dev"]
    frontend_process = subprocess.Popen(frontend_cmd, cwd=frontend_dir)

    print("\n--------------------------------------------------")
    print(" Status:")
    print("   - Backend API:  http://localhost:8000")
    print("   - API Docs:     http://localhost:8000/docs")
    print("   - Frontend UI:  http://localhost:3000")
    print("--------------------------------------------------")
    print("Press Ctrl+C at any time to stop both processes.\n")

    try:
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print("Backend process terminated unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("Frontend process terminated unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        if backend_process.poll() is None:
            backend_process.terminate()
        if frontend_process.poll() is None:
            frontend_process.terminate()
        print("Servers stopped.")

if __name__ == "__main__":
    main()
