from pathlib import Path

def load_knowledge():
    path = Path("knowledge.txt")
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()[:8000]
