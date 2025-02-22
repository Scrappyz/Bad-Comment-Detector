import ahocorasick
import contractions
import string
import re
import spacy
from pathlib import Path
from thefuzz import fuzz

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

def normalizeWildcards(text: str, wildcard: str, wildcard_set: set, end_excludes={'.', ',', '!'}) -> str:
    if type(wildcard_set) == str:
        wildcard_set = set(wildcard_set)
        
    normalized = ""
    for i in range(len(text)):
        ch = text[i]
        if ch in wildcard_set:
            if text[i] in end_excludes and (i >= len(text)-1 or text[i+1] == ' '):
                normalized += ch
                continue
            normalized += wildcard
            continue
            
        normalized += ch
        
    return normalized
  
def fuzzyMatchReplace(word, word_list, threshold, remove_duplicates=False) -> str:
    if not word:
        return ""
    
    # Remove duplicate characters in a row (e.g. "hello" -> "helo")
    if not remove_duplicates:
        temp = word
    else:
        temp = word[0]
        for i in word:
            if i == temp[-1]:
                continue
            temp += i
        
    for i in word_list:
        if fuzz.ratio(temp, i) >= threshold:
            return i
          
    return word
  
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
    # Remove newlines
    text = re.sub(r'[\r\n]+', '', text)
    
    # Remove HTML
    text = re.sub(r"http\S+", "", text)
    
    # Remove trailing whitespace
    text = re.sub(r'\s{2,}', ' ', text).strip()
    
    # Remove non-ascii characters
    printable_chars = set(string.printable)
    text = "".join(filter(lambda x: x in printable_chars, text))
    
    # Remove non-alphabet words (e.g. "$100" or "2024")
    text = " ".join([word for word in text.split() if re.search(r'[a-zA-Z]', word)])
    
    # Set to lowercase
    text = text.lower()
    
    # Expand contractions (e.g. "you're" -> "you are")
    text = contractions.fix(text)
    
    # Replace all wildcards to a single wildcard (e.g. "f#dg*" -> "f*dg*")
    text = re.sub(r"[^a-zA-Z.,!\s]", "*", text)
    text = normalizeWildcards(text, "*", set(".,!"), set(".,!"))
    
    # Replace all keywords to their proper wording (e.g. "f*dge" -> "fudge")
    matches = findMatchingSubstringsWithWildcardsAndReplacement(text, word_set, "*")
    for k, v in matches.items():
        text = text.replace(k, v)
    
    # Remove all stopwords
    tokens = tokenizer(text)
    tokens = [i.text for i in tokens if i.text not in stopword_set]
    
    # Replace all extended words (e.g. "niiiiggaa" -> "nigga")
    cleaned = []
    for i in tokens:
        cleaned.append(fuzzyMatchReplace(str(i), word_set, 88, True))
    
    cleaned = " ".join(cleaned)
    
    return cleaned

def main():
    nlp = spacy.load("en_core_web_md", disable=["parser", "ner", "tagger", "lemmatizer", "textcat"])
    print(cleanText("F$ck", {"nigga", "fuck"}, {}, nlp))

if __name__ == "__main__":
    main()
