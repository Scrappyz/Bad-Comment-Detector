import ahocorasick
import contractions
import string
import re
import spacy
from pathlib import Path

import helper

def findAllSubstrings(s, word_list, max=-1) -> set:
  if type(word_list) == set:
    word_list = list(word_list)
    
  automaton = ahocorasick.Automaton()
  # print("Base: " + s)
  for i in range(len(word_list)):
    automaton.add_word(word_list[i], i)
    
  automaton.make_automaton()
  found_words = set()
  count = 0
  
  for _, idx in automaton.iter(s):
    found_words.add(word_list[idx])
    count += 1
    if max >= 0 and count >= max:
      break
    
  return found_words

def isSubstring(s, word_list, min=1):
  if min < 1:
    min = len(word_list)
    
  words = findAllSubstrings(s, word_list, min)
  
  # print(words)
  return len(words) >= min

def normalizeWildcards(text: str, wildcard_set: set) -> str:
    normalized = ""
    for i in text:
        if i in wildcard_set:
            normalized += '*'
            continue
            
        normalized += i
        
    return normalized
  
def findMatchingSubstringsWithWildcardsAndReplacement(text, word_list, wildcards: str) -> dict:
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
  
def cleanText(text: str, word_set, stopword_set, tokenizer) -> str:
    # Mapping for leetspeak to regular characters
    leet_map = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't',
        '@': 'a', '$': 's', '(': 'c'
    }

    wildcards = {
        '*', '#'
    }
    
    # Remove HTML
    text = re.sub(r"http\S+", "", text)
    
    # Remove trailing whitespace
    text = text.strip()
    
    # Remove non-ascii characters
    printable_chars = set(string.printable)
    text = "".join(filter(lambda x: x in printable_chars, text))
    
    text = contractions.fix(text)
    
    # print("1.) ", text)
    cleaned = ""
    for i in text.lower():
        if i in leet_map:
            cleaned += leet_map[i]
            continue
        
        cleaned += i
        
    tokens = tokenizer(cleaned)
    cleaned = " ".join([i.text for i in tokens if i.text not in stopword_set])
    
    cleaned = normalizeWildcards(cleaned, wildcards)
    
    matches = findMatchingSubstringsWithWildcardsAndReplacement(cleaned, word_set, "*")
    
    for k, v in matches.items():
        cleaned = cleaned.replace(k, v)
    
    return cleaned

def main():
  print(isSubstring("bigbird", ["bird", "big"]))

if __name__ == "__main__":
  main()
