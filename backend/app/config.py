import os
import shutil
from pathlib import Path
from pydantic import BaseModel, Field

# Determine project root and .env path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

def load_env_variables():
    """Loads .env file into os.environ if it exists."""
    if ENV_PATH.is_file():
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=ENV_PATH, override=False)
        except ImportError:
            # Fallback manual parser
            try:
                with open(ENV_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ[k.strip()] = v.strip().strip("'\"")
            except Exception:
                pass

# Initial load
load_env_variables()

class Settings(BaseModel):
    def reload_env(self):
        load_env_variables()

    @property
    def DEEPSEEK_API_KEY(self) -> str:
        self.reload_env()
        return os.getenv("DEEPSEEK_API_KEY", "").strip()

    @property
    def DEEPSEEK_BASE_URL(self) -> str:
        self.reload_env()
        return os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()

    @property
    def DEEPSEEK_MODEL(self) -> str:
        self.reload_env()
        return os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    @property
    def PANDOC_PATH(self) -> str:
        return os.getenv("PANDOC_PATH", "").strip()

    def get_pandoc_bin(self) -> str:
        if self.PANDOC_PATH and shutil.which(self.PANDOC_PATH):
            return self.PANDOC_PATH
        which_path = shutil.which("pandoc")
        if which_path:
            return which_path
        
        # Check standard Windows paths
        win_candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Pandoc\pandoc.exe"),
            r"C:\Program Files\Pandoc\pandoc.exe",
            r"C:\Program Files (x86)\Pandoc\pandoc.exe",
        ]
        for p in win_candidates:
            if os.path.exists(p):
                return p
        
        # Linux / WSL candidates
        linux_candidates = [
            "/usr/bin/pandoc",
            "/usr/local/bin/pandoc",
        ]
        for p in linux_candidates:
            if os.path.exists(p):
                return p
                
        return "pandoc"

settings = Settings()
