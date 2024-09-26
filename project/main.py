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
    
def fuzzyReplace(text, toxic_keywords, threshold=75) -> str:
    words = text.split()
    for i in range(len(words)):
        for toxic_word in toxic_keywords:
            if fuzz.ratio(words[i], toxic_word) >= threshold:
                words[i] = toxic_word
                break
    
    return " ".join(words)

def cleanText(text):
    """Clean the input text for better toxicity detection."""
    # Lowercase the text
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    
    # Remove user mentions (@username)
    text = re.sub(r'\@\w+', '', text)

    # Normalize repeated characters (e.g., "stuuuupid" -> "stupid")
    text = re.sub(r'(.)\1+', r'\1\1', text)

    # Replace leetspeak characters carefully
    for leet_char, alphabet in leet_map.items():
        text = text.replace(leet_char, alphabet)
    
    # After replacing leetspeak characters, remove unwanted symbols
    text = re.sub(r'[^a-z\s]', '', text)  # Keep only letters and spaces

    # Strip any extra whitespace
    text = text.strip()
    
    return text

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
    # source_dir = Path(__file__).parent.resolve()
    # test_cases = getTestCases(source_dir.parent.joinpath("assets/test_cases.json"))
    
    # for i in test_cases:
    #     comment = i["comment"]
    #     expected_result = i["expected"]
    #     is_toxic = detectToxicity(comment, nlp)
    #     actual_result = "Toxic" if is_toxic else "Non-Toxic"
        
    #     print("[{0}] ({1}): {2}".format(actual_result, expected_result, comment))
    
    print(fuzzyReplace("you fck", toxic_keywords))

if __name__ == "__main__":
    main()
