import argparse
import spacy
import os
import numpy as np
import re
import json
from pathlib import Path
# from deep_translator import GoogleTranslator

leet_map = {
    '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't',
    '@': 'a', '$': 's', '!': 'i', '*': '', '#': '', '(': 'c'
}

# Toxic keywords for the rule-based approach
toxic_keywords = [
    r'\bidiot\b', r'\bdumb\b', r'\bannoying\b', r'\bstupid\b',
    r'\bshut\s?up\b', r'\bjerk\b', r'\bfool\b', r'\btrash\b'
]

def getTestCases(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f.read())

def readTextFromFile(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()
    
# Data cleaning function
def cleanText(text):
    # Lowercase the text
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    
    # Remove user mentions (@username)
    text = re.sub(r'\@\w+', '', text)
    
    # Remove special characters, numbers, extra whitespace (keep punctuation minimally)
    text = re.sub(r"[^a-z\s']", '', text)

    # Normalize repeated characters (e.g., "stuuuupid" -> "stupid")
    text = re.sub(r'(.)\1+', r'\1\1', text)

    # Replace common leetspeak characters with their alphabetic equivalents
    leet_map = {
        '4': 'a', '3': 'e', '1': 'i', '0': 'o', '!': 'i', '|': 'i', '$': 's', '@': 'a'
    }
    for leet_char, alphabet in leet_map.items():
        text = text.replace(leet_char, alphabet)

    # Strip any extra whitespace
    text = text.strip()
    
    return text

# Rule-based detection function
def ruleBasedDetection(text):
    for keyword in toxic_keywords:
        if re.search(keyword, text, re.IGNORECASE):
            return True  # Found a toxic keyword
    return False

# AI-based detection using spaCy's text classifier
def aiBasedDetection(text, nlp):
    doc = nlp(text)
    # Assuming the model's 'cats' attribute gives the category probabilities
    if 'toxic' in doc.cats and doc.cats['toxic'] > 0.5:
        return True  # Toxic based on AI model
    return False

# Hybrid approach: Combine both methods
def detectToxicity(text, nlp):
    # Step 1: Clean the text
    cleaned_text = cleanText(text)
    
    # Step 2: Rule-based detection
    if ruleBasedDetection(cleaned_text):
        return True  # Mark as toxic if rule-based approach detects it
    
    # Step 3: AI-based detection
    return aiBasedDetection(cleaned_text, nlp)

def main():
    parser = argparse.ArgumentParser(description='Detect bad comment.')
    parser.add_argument('-t', '--text', type=str, nargs=1,
                         help='bad comment.')
    parser.add_argument('-f', '--file', metavar='file', type=str, nargs=1,
                         help='file input.')
    
    args = parser.parse_args()
    
    # Argument values
    text = ''
    current_dir = os.getcwd()
    file_path = ''
    
    if args.file:
        file_path = Path(current_dir).joinpath(args.file[0]).resolve()
        text = readTextFromFile(file_path)
        
    if args.text:
        text = args.text[0]
        
    nlp = spacy.load("en_core_web_md")
        
    for comment in comments:
        if detectToxicity(comment, nlp):
            print(f"Toxic: {comment}")
        else:
            print(f"Non-Toxic: {comment}")

if __name__ == "__main__":
    main()
