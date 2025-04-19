import os
import subprocess
import sys
import venv
from pathlib import Path

VENV_DIR = "venv"
REQUIREMENTS_FILE = "requirements.txt"
MAIN_SCRIPT = "main.py"
TSINGHUA_PIP_SOURCE = "https://pypi.tuna.tsinghua.edu.cn/simple"

def is_venv_active():
    """Check if a virtual environment is currently active."""
    return sys.prefix != sys.base_prefix

def create_venv():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path(VENV_DIR)
    if not venv_path.exists():
        print(f"Creating virtual environment in {VENV_DIR}...")
        venv.create(venv_path, with_pip=True)
        return True
    else:
        print(f"Virtual environment already exists in {VENV_DIR}.")
        return False

def get_venv_python():
    """Get the path to the Python executable in the virtual environment."""
    if os.name == "nt":  # Windows
        return Path(VENV_DIR) / "Scripts" / "python.exe"
    else:  # macOS/Linux
        return Path(VENV_DIR) / "bin" / "python"

def install_requirements():
    """Install dependencies from requirements.txt using Tsinghua PyPI mirror."""
    print(f"Installing dependencies from {REQUIREMENTS_FILE} with Tsinghua mirror...")
    pip_cmd = [
        str(get_venv_python()),
        "-m",
        "pip",
        "install",
        "-r",
        REQUIREMENTS_FILE,
        "-i",
        TSINGHUA_PIP_SOURCE,
    ]
    try:
        subprocess.run(pip_cmd, check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

def run_main_script():
    """Run the main.py script in the virtual environment."""
    # Check for local/.env
    env_path = Path("local") / ".env"
    if not env_path.exists():
        print(f"Warning: {env_path} not found. Ensure environment variables are set.")
    
    print(f"Running {MAIN_SCRIPT} in virtual environment...")
    main_cmd = [str(get_venv_python()), MAIN_SCRIPT]
    try:
        subprocess.run(main_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run {MAIN_SCRIPT}: {e}")
        sys.exit(1)

def main():
    # Check if we're already in a virtual environment
    if is_venv_active():
        print("Virtual environment is already active. Running main.py directly...")
        run_main_script()
        return

    # Create virtual environment if it doesn't exist
    venv_created = create_venv()

    # Install dependencies
    if venv_created:
        install_requirements()

    # Run main.py
    run_main_script()

if __name__ == "__main__":
    main()