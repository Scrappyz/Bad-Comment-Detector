import argparse
import spacy
import contractions
from pathlib import Path

import parser
import helper

def cleanText(text: str, word_set) -> str:
    # Mapping for leetspeak to regular characters
    leet_map = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't',
        '@': 'a', '$': 's', '(': 'c'
    }

    wildcards = {
        '*', '#'
    }

    text = contractions.fix(text)
    
    # print("1.) ", text)
    cleaned = ""
    for i in text.lower():
        if i in leet_map:
            cleaned += leet_map[i]
            continue
        
        cleaned += i
    
    # print("2.) ", cleaned)
    cleaned = parser.normalizeWildcards(cleaned, wildcards)
    # print("3.) ", cleaned)
    
    matches = parser.findMatchingSubstringsWithWildcardsAndReplacement(cleaned, word_set, "*")
    
    for k, v in matches.items():
        cleaned = cleaned.replace(k, v)
    
    # print("4.) ", cleaned)
    
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
    if 'toxic' in doc.cats and doc.cats['toxic'] > 0.75:
        return True  # Toxic based on AI model
    
    return False

def detectToxicity(text, keywords: set, nlp, localNLP, ai=True, threshold=65):
    # Hybrid approach combining rule-based and AI-based toxicity detection.
    # Step 1: Clean the text
    cleanedText = cleanText(text, keywords)
    tokens = nlp(cleanedText)
    
    # Step 2: Rule-based detection
    if ruleBasedDetection(tokens, keywords):
        return True  # Mark as toxic if rule-based approach detects it
    
    # Step 3: AI-based detection
    if ai:
        return aiBasedDetection(cleanedText, localNLP)
    # return aiBasedDetection(" ".join(tokens), nlp)
    return False

def main():
    source_dir = Path(__file__).parent.resolve()
    asset_dir = source_dir.parent.joinpath("assets")
    test_cases = list(helper.readJsonFromFile(asset_dir.joinpath("test_cases.json")))
    toxic_keywords = set(helper.readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    
    parser = argparse.ArgumentParser("Bad Comment Detector")
    parser.add_argument("-t", dest="text", metavar="Text", nargs='+', type=str, help="Comment to detect", required=False)
    parser.add_argument("--no-ai", dest="ai", action="store_false", required=False, help="Disable AI filter")
    
    args = parser.parse_args()
    
    if args.ai:
        nlp = spacy.load("en_core_web_md")
        localNLP = spacy.load("../output/model-last")
        # print("With AI")
    else:
        nlp = spacy.load("en_core_web_md", disable=["parser", "ner", "tagger", "lemmatizer", "textcat"])
    
    if args.text:
        for i in args.text:
            if args.ai:
                print("[Toxic]: " + i if detectToxicity(i, toxic_keywords, nlp, localNLP, args.ai) else "[Non-toxic]: " + i)
            else:
                print("[Toxic]: " + i if detectToxicity(i, toxic_keywords, nlp, None, args.ai) else "[Non-toxic]: " + i)
    else:
        main_test(test_cases, toxic_keywords, nlp, localNLP)
    

def main_test(test_cases, toxic_keywords, nlp, localNLP):
    # Main function to run toxicity detection on test cases.
    source_dir = Path(__file__).parent.resolve()
    
    score = 0
    total = 0
    pass_test_case = False
    # print(fuzz.ratio("a**hole", "asshole"));

    for i in test_cases:
        total += 1
        comment = i["comment"]
        expected_result = i["expected"]
        is_toxic = detectToxicity(comment, toxic_keywords, nlp, localNLP)
        actual_result = "Toxic" if is_toxic else "Non-Toxic"
        if actual_result == expected_result:
            pass_test_case = True
            score += 1
        else:
            pass_test_case = False
        print("[{3}] Result: {0}, Expected: {1}, Comment: {2}".format(actual_result, expected_result, comment, pass_test_case))
    
    print("Score: " + str(score) + "/" + str(total))
    
if __name__ == "__main__":
    main()
