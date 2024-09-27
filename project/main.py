import argparse
import spacy
import os
import re
import json
import contractions
from thefuzz import fuzz
from pathlib import Path

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Mapping for leetspeak to regular characters
leet_map = {
    '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't',
    '@': 'a', '$': 's', '!': 'i', '*': '', '#': '', '(': 'c'
}

def readTextFromFile(file_path: str) -> str:
    """Read text from a file."""
    with open(file_path, 'r') as f:
        return f.read()
    
def readJsonFromFile(file_path: str):
    with open(file_path, "r") as f:
        return json.load(f)
    
def fuzzyReplace(words, keywords, threshold=75):
    for i in range(len(words)):
        for word in keywords:
            if fuzz.ratio(words[i], word) >= threshold:
                words[i] = word
                break

def cleanTextAndTokenize(text, keywords: set, threshold=75) -> list:
    # Expand contractions
    expanded_text = contractions.fix(text.lower())
    
    # Tokenize the text
    tokens = nlp(expanded_text, disable=["parser", "tagger", "ner", "lemmatizer", "textcats"])
    words = []
    
    # Remove punctuation tokens
    for token in tokens:
        # Check if the token is alphanumeric (contains letters or digits)
        if not re.fullmatch(r'^[\W_]+$', token.text):  # Matches tokens with only special characters
            words.append(token.text)  # Append the actual text representation of the token
    
    fuzzyReplace(words, keywords, threshold)
    return words

def ruleBasedDetection(tokens, keywords: set):
    # Detect toxicity using rule-based regex patterns.
    for i in tokens:
        if i in keywords:
            return True
    return False

def aiBasedDetection(text, nlp):
    # Detect toxicity using spaCy's AI-based model.
    doc = nlp(text)

    # Assuming the model's 'cats' attribute gives the category probabilities
    if 'toxic' in doc.cats and doc.cats['toxic'] > 0.5:
        return True  # Toxic based on AI model
    
    return False

def detectToxicity(text, keywords: set, nlp, threshold=75):
    # Hybrid approach combining rule-based and AI-based toxicity detection.
    # Step 1: Clean the text
    tokens = cleanTextAndTokenize(text, keywords, threshold)
    
    # Step 2: Rule-based detection
    if ruleBasedDetection(tokens, keywords):
        return True  # Mark as toxic if rule-based approach detects it
    
    # Step 3: AI-based detection
    return aiBasedDetection(" ".join(tokens), nlp)

def main():
    """Main function to run toxicity detection on test cases."""
    source_dir = Path(__file__).parent.resolve()
    asset_dir = source_dir.parent.joinpath("assets")
    test_cases = list(readJsonFromFile(asset_dir.joinpath("test_cases.json")))
    toxic_keywords = set(readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    essay = readTextFromFile(source_dir.parent.joinpath("data/essay.txt").resolve())
    
    for i in test_cases:
        comment = i["comment"]
        expected_result = i["expected"]
        is_toxic = detectToxicity(comment, toxic_keywords, nlp)
        actual_result = "Toxic" if is_toxic else "Non-Toxic"
        
        print("[{0}] ({1}): {2}".format(actual_result, expected_result, comment))

if __name__ == "__main__":
    main()
