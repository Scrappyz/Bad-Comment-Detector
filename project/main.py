import argparse
import spacy
import os
import re
import contractions
from thefuzz import fuzz
from pathlib import Path

import parser
import helper

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Mapping for leetspeak to regular characters
leet_map = {
    '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't',
    '@': 'a', '$': 's', '(': 'c'
}

wildcards = {
    '*', '#'
}

def cleanText(text: str, word_set) -> str:
    text = contractions.fix(text)
    
    print("1.) ", text)
    cleaned = ""
    for i in text.lower():
        if i in leet_map:
            cleaned += leet_map[i]
            continue
        
        cleaned += i
    
    print("2.) ", cleaned)
    cleaned = parser.normalizeWildcards(cleaned, wildcards)
    print("3.) ", cleaned)
    
    matches = parser.findMatchingSubstringsWithWildcardsAndReplacement(cleaned, word_set, "*")
    
    for k, v in matches.items():
        cleaned = cleaned.replace(k, v)
    
    print("4.) ", cleaned)
    
    return cleaned

def ruleBasedDetection(tokens, keywords: set):
    # Detect toxicity using rule-based regex patterns.
    
    for i in tokens:
        if parser.isSubstring(str(i), keywords):
            return True
    return False

def aiBasedDetection(text, nlp):
    # Detect toxicity using spaCy's AI-based model.
    doc = nlp(text)

    # Assuming the model's 'cats' attribute gives the category probabilities
    if 'toxic' in doc.cats and doc.cats['toxic'] > 0.5:
        return True  # Toxic based on AI model
    
    return False

def detectToxicity(text, keywords: set, nlp, threshold=65):
    # Hybrid approach combining rule-based and AI-based toxicity detection.
    # Step 1: Clean the text
    tokens = nlp(cleanText(text, keywords))
    
    # Step 2: Rule-based detection
    if ruleBasedDetection(tokens, keywords):
        return True  # Mark as toxic if rule-based approach detects it
    
    return False
    # Step 3: AI-based detection
    # return aiBasedDetection(" ".join(tokens), nlp)

def main():
    """Main function to run toxicity detection on test cases."""
    source_dir = Path(__file__).parent.resolve()
    asset_dir = source_dir.parent.joinpath("assets")
    test_cases = list(helper.readJsonFromFile(asset_dir.joinpath("test_cases.json")))
    toxic_keywords = set(helper.readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    essay = helper.readTextFromFile(source_dir.parent.joinpath("data/essay.txt").resolve())
    
    text = "You f#ck1ng fuc a$$h0l5"
    cleaned = cleanText(text, toxic_keywords)
    print(cleaned)

def main_test():
    """Main function to run toxicity detection on test cases."""
    source_dir = Path(__file__).parent.resolve()
    asset_dir = source_dir.parent.joinpath("assets")
    test_cases = list(helper.readJsonFromFile(asset_dir.joinpath("test_cases.json")))
    toxic_keywords = set(helper.readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    
    score = 0
    total = 0
    pass_test_case = False
    # print(fuzz.ratio("a**hole", "asshole"));

    for i in test_cases:
        total += 1
        comment = i["comment"]
        expected_result = i["expected"]
        is_toxic = detectToxicity(comment, toxic_keywords, nlp)
        actual_result = "Toxic" if is_toxic else "Non-Toxic"
        if actual_result == expected_result:
            pass_test_case = True
            score += 1
        else:
            pass_test_case = False
        print("[{3}] Result: {0}, Expected: {1}, Comment: {2}".format(actual_result, expected_result, comment, pass_test_case))
    
    print("Score: " + str(score) + "/" + str(total))
if __name__ == "__main__":
    main_test()
