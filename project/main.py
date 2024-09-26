import argparse
import spacy
import os
import re
import json
from thefuzz import fuzz
from pathlib import Path

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Mapping for leetspeak to regular characters
leet_map = {
    '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't',
    '@': 'a', '$': 's', '!': 'i', '*': '', '#': '', '(': 'c'
}

# Toxic keywords for rule-based detection with more flexibility
toxic_keywords = {'fuck', 'shit', 'asshole', 'idiot', 'dumb', 'annoying', 'stupid', 'shut up', 'jerk', 'fool', 'trash'}

def getTestCases(path) -> list:
    """Load test cases from a JSON file."""
    with open(path, "r") as f:
        return json.load(f)

def readTextFromFile(file_path: str) -> str:
    """Read text from a file."""
    with open(file_path, 'r') as f:
        return f.read()
    
def fuzzyReplace(words, keywords, threshold=75):
    for i in range(len(words)):
        for word in keywords:
            if fuzz.ratio(words[i], word) >= threshold:
                words[i] = word
                break

def cleanTextAndTokenize(text) -> list:
    tokens = nlp(text, disable=["parser", "tagger", "ner", "lemmatizer", "textcats"])
    words = []
    for token in tokens:
        # Check if the token is alphanumeric (contains letters or digits)
        if not re.fullmatch(r'^[\W_]+$', token.text):  # Matches tokens with only special characters
            words.append(token.text)  # Append the actual text representation of the token
    
    fuzzyReplace(words, toxic_keywords, 50)
    return words

def ruleBasedDetection(text):
    """Detect toxicity using rule-based regex patterns."""
    for keyword in toxic_keywords:
        if re.search(keyword, text, re.IGNORECASE):
            return True  # Found a toxic keyword
    return False

def aiBasedDetection(text, nlp):
    """Detect toxicity using spaCy's AI-based model."""
    doc = nlp(text)

    # Assuming the model's 'cats' attribute gives the category probabilities
    if 'toxic' in doc.cats and doc.cats['toxic'] > 0.5:
        return True  # Toxic based on AI model
    
    return False

def detectToxicity(text, nlp):
    """Hybrid approach combining rule-based and AI-based toxicity detection."""
    # Step 1: Clean the text
    cleaned_text = cleanText(text)
    
    # Step 2: Rule-based detection
    if ruleBasedDetection(cleaned_text):
        return True  # Mark as toxic if rule-based approach detects it
    
    # Step 3: AI-based detection
    return aiBasedDetection(cleaned_text, nlp)

def main():
    """Main function to run toxicity detection on test cases."""
    source_dir = Path(__file__).parent.resolve()
    test_cases = getTestCases(source_dir.parent.joinpath("assets/test_cases.json"))
    essay = readTextFromFile(source_dir.parent.joinpath("data/essay.txt").resolve())
    
    # for i in test_cases:
    #     comment = i["comment"]
    #     expected_result = i["expected"]
    #     is_toxic = detectToxicity(comment, nlp)
    #     actual_result = "Toxic" if is_toxic else "Non-Toxic"
        
    #     print("[{0}] ({1}): {2}".format(actual_result, expected_result, comment))
    
    words = cleanTextAndTokenize(essay)
    for i in words:
        print(i)

if __name__ == "__main__":
    main()
