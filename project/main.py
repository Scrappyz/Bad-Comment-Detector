import json
from pathlib import Path

def getRephrasals(path: str) -> dict:
    f = open(path)
    data = json.load(f)
    rephrasals = {}
    for k, v in data.items():
        key = k.lower()
        for i in v:
            rephrasals[i.lower()] = key
    return rephrasals

def rephraseComment(comment: str, rephrasals: dict) -> str:
    include = {"\'"}
    rephrased_comment = ""
    word = ""
    for i in range(len(comment)):
        ch = comment[i]
        if not ch.isalpha() and ch not in include:
            if len(word) > 0:
                if word in rephrasals:
                    word = rephrasals[word]
                rephrased_comment += word
                word = ""
            rephrased_comment += ch
            continue
        word += ch.lower()
        
    if len(word) > 0:
        if word in rephrasals:
            word = rephrasals[word]
        rephrased_comment += word
        word = ""
        
    return rephrased_comment

def main():
    current_dir = Path(__file__).parent.resolve()
    rephrasals = getRephrasals(Path.joinpath(current_dir, "rephrase.json"))
    print(rephraseComment("Fuck you, you shouldn't do that", rephrasals))

if __name__ == "__main__":
    main()