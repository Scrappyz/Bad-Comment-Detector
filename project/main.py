import json
from pathlib import Path

# Gets contractions.json content into a dict.
# Parameters:
# `path`: Path to the contractions JSON file.
def getContractions(path: str) -> dict:
    f = open(path)
    data = json.load(f)
    contractions = {}
    for k, v in data.items():
        key = k.lower()
        for i in v:
            contractions[i.lower()] = key
    return contractions

# Expands contractions like "don't" -> "do not".    
def expandContractions(comment: str, contractions: dict) -> str:
    include = {"\'"}
    cleaned_comment = ""
    word = ""
    for i in range(len(comment)):
        ch = comment[i]
        if not ch.isalpha() and ch not in include:
            if len(word) > 0:
                if word in contractions:
                    word = contractions[word]
                cleaned_comment += word
                word = ""
            cleaned_comment += ch
            continue
        word += ch.lower()
        
    if len(word) > 0:
        if word in contractions:
            word = contractions[word]
        cleaned_comment += word
        word = ""
        
    return cleaned_comment

def main():
    current_dir = Path(__file__).parent.resolve()
    contractions = getContractions(Path.joinpath(current_dir, "resources/contractions.json"))
    print(expandContractions("Fuck you, you shouldn't do that", contractions))

if __name__ == "__main__":
    main()