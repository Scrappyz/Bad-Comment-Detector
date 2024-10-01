import argparse
import spacy
import os
import re
import json
import contractions
from thefuzz import fuzz
from pathlib import Path

import parser

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

# Turns non-alphabets into any one character regex pattern
def toRegex(text: str) -> str:
    s = ""
    for i in text.lower():
        if ord(i) >= ord('a') and ord(i) <= ord('z') or i == ' ':
            s += i
            continue
        
        if i == '.':
            s += '\\'
        
        s += '.'
        
    return s

# replaces words with bad words
def fuzzyReplace(words, keywords, threshold=65):
    for i in range(len(words)):
        if words[i].find('*') < 0:
            continue
        
        for word in keywords:
            if fuzz.ratio(words[i], word) >= threshold:
                # print(words[i] + ", " + word)
                words[i] = word
                break
            
def replaceNonAlphabets(text: str, replace_with: str) -> str:
    s = ""
    for i in text.lower():
        if ord(i) >= ord('a') and ord(i) <= ord('z') or i == ' ':
            s += i
            continue
        
        s += replace_with
        
    return s

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

    return substrings

def revertWildcards(text: str, original_text: str) -> str:
    new_str = ""
    for i in range(len(text)):
        if text[i] == '*':
            new_str += original_text[i]
            continue
        
        new_str += text[i]
        
    return new_str

def replaceNonAlphabetWithWildcard(words):
    str = ""
    for i in range(len(words)):
        str = ""
        for j in range(len(words[i])):
            if ord(words[i][j]) >= ord('a') and ord(words[i][j]) <= ord('z'):
                str += words[i][j]
            else:
                str += '*'
        words[i] = str
    return words

def getOriginalComment(text, keywords: set, threshold=65):
    # Expand contractions
    expanded_text = contractions.fix(text.lower())
    
    # Tokenize the text
    tokens = nlp(expanded_text, disable=["parser", "tagger", "ner", "lemmatizer", "textcats"])
    words = []

    for token in tokens:
        words.append(token.text)

    return words

# returns bad words
def cleanTextAndTokenize(text, keywords: set, threshold=65) -> list:
    # Expand contractions
    expanded_text = contractions.fix(text.lower())
    
    # Tokenize the text
    tokens = nlp(expanded_text, disable=["parser", "tagger", "ner", "lemmatizer", "textcats"])
    words = []
    
    # Remove punctuation tokens
    for token in tokens:
        # print("Token: ", token)
        # Check if the token is alphanumeric (contains letters or digits)
        # if not re.fullmatch(r'^[\W_]+$', token.text):  # Matches tokens with only special characters
        #     words.append(token.text)  # Append the actual text representation of the token
        words.append(token.text)

    replaceNonAlphabetWithWildcard(words)
    for word in words:
        print("Current: " + word)
    
    # fuzzyReplace(words, keywords, threshold)

    badWordsList = list(keywords)

    for i in range(len(words)):
        # if words[i].find('*') < 0:
        #     continue
        words[i] = parser.fuzzyMatchWord(words[i], badWordsList)

    for word in words:
        print("Fuzzy: " + word)

    for i in range(len(words)):
        words[i] = parser.parseBadWord(words[i], badWordsList)
    
    # for i in range(len(words)):
    #     for badword in keywords:
    #         if words[i].find(badword) > -1:
    #             words[i] = badword

    for word in words:
        print("Regex: " + word)
    
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

def detectToxicity(text, keywords: set, nlp, threshold=65):
    # Hybrid approach combining rule-based and AI-based toxicity detection.
    # Step 1: Clean the text
    tokens = cleanTextAndTokenize(text, keywords, threshold)
    originalTokens = getOriginalComment(text, keywords, threshold)
    
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
    
    for i in test_cases:
        comment = i["comment"]
        expected_result = i["expected"]
        is_toxic = detectToxicity(comment, toxic_keywords, nlp)
        actual_result = "Toxic" if is_toxic else "Non-Toxic"
        
        print("[{0}] ({1}): {2}".format(actual_result, expected_result, comment))

def main_test():
    """Main function to run toxicity detection on test cases."""
    source_dir = Path(__file__).parent.resolve()
    asset_dir = source_dir.parent.joinpath("assets")
    test_cases = list(readJsonFromFile(asset_dir.joinpath("test_cases.json")))
    toxic_keywords = set(readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    # essay = readTextFromFile(source_dir.parent.joinpath("data/essay.txt").resolve())
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
