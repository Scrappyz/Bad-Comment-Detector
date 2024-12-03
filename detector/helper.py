import csv
import json
from pathlib import Path

def readTextFromFile(file_path) -> str:
    """Read text from a file."""
    with open(file_path, 'r') as f:
        return f.read()
    
def readJsonFromFile(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def readCSVFromFile(file_path):
    with open(file_path, mode='r', encoding="utf8") as f:
        lines = []
        csvFile = csv.reader(f)
        for line in csvFile:
            lines.append(line)
        return lines

def writeJsonToFile(file_path, j):
    if type(j) != json:
        j = json.dumps(j, indent=4)
        
    with open(file_path, 'w') as f:
        f.write(j)
        
def appendToCSVFile(file_path, arr: list):
    if not arr:
        return
            
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if type(arr[0]) == list:
            for i in arr:
                writer.writerow(i)
        else:
            writer.writerow(i)
            
def writeToCSVFile(file_path, arr, fieldnames=[]):
    if not arr:
        return
    
    if type(arr[0]) == dict:
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(arr)
    else:
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(arr)
            
def readCommentsFromFile(file_path) -> list:
    with open(file_path, "r") as f:
        return f.read().splitlines()