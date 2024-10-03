import json

def readTextFromFile(file_path: str) -> str:
    """Read text from a file."""
    with open(file_path, 'r') as f:
        return f.read()
    
def readJsonFromFile(file_path: str):
    with open(file_path, "r") as f:
        return json.load(f)