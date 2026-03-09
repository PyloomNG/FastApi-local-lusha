# Run script for local development (without Docker)
import subprocess
import sys
import os

def main():
    # Create venv if not exists
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

    # Install dependencies
    print("Installing dependencies...")
    subprocess.run(["./venv/Scripts/pip", "install", "-r", "requirements.txt"], check=True)

    # Run uvicorn
    print("Starting server...")
    subprocess.run(["./venv/Scripts/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

if __name__ == "__main__":
    main()
