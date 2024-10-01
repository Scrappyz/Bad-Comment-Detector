import argparse
import spacy
import os
import re
import json
import contractions
import ahocorasick
from thefuzz import fuzz
from pathlib import Path

import parser

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Mapping for leetspeak to regular characters
leet_map = {
    '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't',
    '@': 'a', '$': 's', '(': 'c'
}

wilcards = {
    '*', '#'
}

def readTextFromFile(file_path: str) -> str:
    """Read text from a file."""
    with open(file_path, 'r') as f:
        return f.read()
    
def readJsonFromFile(file_path: str):
    with open(file_path, "r") as f:
        return json.load(f)
    
def findMatchingSubstrings(text, word_list, wildcards: str) -> dict:
    substrings = {}
    wildcards_set = set()
    
    # Add wildcards to set to be able to compare multiple wildcards
    for i in wildcards:
        wildcards_set.add(i)

    # Loop through the word list
    for word in word_list:
        i = 0
        j = 0
        substr = "" # Temporary variable to store the found substring
        
        # Loop until whole text is traversed
        while i < len(text):
            
            # If both `i` and `j` point to the same character, it means a possible substring is found.
            # Increment both `i` and `j` so they will traverse with each other.
            if text[i] == word[j] or text[i] in wildcards_set:
                substr += text[i]
                i += 1
                j += 1
            else: # Otherwise, reset `j` and `substr`
                i = i - j + 1
                j = 0
                substr = ""
                
            # If `j` reaches the end of `word`, it means a substring was found.
            if j == len(word):
                substrings[substr] = word
                substr = ""
                i += 1
                j = 0

    return dict(reversed(list(substrings.items())))
    
def normalizeWildcards(text: str) -> str:
    normalized = ""
    for i in text:
        if i in wilcards:
            normalized += '*'
            continue
            
        normalized += i
        
    return normalized

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
    cleaned = normalizeWildcards(cleaned)
    print("3.) ", cleaned)
    
    matches = findMatchingSubstrings(cleaned, word_set, "*")
    
    for k, v in matches.items():
        cleaned = cleaned.replace(k, v)
    
    print("4.) ", cleaned)
    
    return cleaned

def ruleBasedDetection(tokens, keywords: set):
    # Detect toxicity using rule-based regex patterns.
    # automaton = ahocorasick.Automaton(ahocorasick.STORE_INTS)
    # for i in keywords:
    #     automaton.add_word(i)
        
    # automaton.make_automaton()
    
    for i in tokens:
        if str(i) in keywords:
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
    test_cases = list(readJsonFromFile(asset_dir.joinpath("test_cases.json")))
    toxic_keywords = set(readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    essay = readTextFromFile(source_dir.parent.joinpath("data/essay.txt").resolve())
    
    text = "You f#ck1ng fuc a$$h0l5"
    cleaned = cleanText(text, toxic_keywords)
    print(cleaned)

def main_test():
    """Main function to run toxicity detection on test cases."""
    source_dir = Path(__file__).parent.resolve()
    asset_dir = source_dir.parent.joinpath("assets")
    test_cases = list(readJsonFromFile(asset_dir.joinpath("test_cases.json")))
    toxic_keywords = set(readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    
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
