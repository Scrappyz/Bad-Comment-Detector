import csv
import json

def readTextFromFile(file_path: str) -> str:
    """Read text from a file."""
    with open(file_path, 'r') as f:
        return f.read()
    
def readJsonFromFile(file_path: str):
    with open(file_path, "r") as f:
        return json.load(f)

def readCSVFromFile(file_path):
    with open(file_path, mode='r', encoding="utf8") as f:
        lines = []
        csvFile = csv.reader(f)
        for line in csvFile:
            lines.append(line)
        return lines