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

def aiBasedDetection(tokens, nlp):
    # Detect toxicity using spaCy's AI-based model.

    # Assuming the model's 'cats' attribute gives the category probabilities
    if 'toxic' in tokens.cats and tokens.cats['toxic'] > 0.7:
        return True  # Toxic based on AI model
    
    return False

def detectToxicity(text, keywords: set, nlp, custom_nlp, ai=True, threshold=65, debug=False):
    # Hybrid approach combining rule-based and AI-based toxicity detection.
    # Step 1: Clean the text
    cleaned_text = cleanText(text, keywords)
    tokens = nlp(cleaned_text)
    
    # Step 2: Rule-based detection
    if ruleBasedDetection(tokens, keywords):
        if debug:
            print("Detection: Rule-based")
        return True  # Mark as toxic if rule-based approach detects it
    
    # Step 3: AI-based detection
    if ai:
        tokens = custom_nlp(cleaned_text)
        if debug:
            print("Detection: AI")
            print("Categories:", tokens.cats)
        return aiBasedDetection(tokens, custom_nlp)
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
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", required=False, help="Debug mode")
    
    args = parser.parse_args()
    
    if args.ai:
        nlp = spacy.load("en_core_web_md")
        custom_nlp = spacy.load(source_dir.parent.joinpath("output/model-last").resolve())
        # print("With AI")
    else:
        nlp = spacy.load("en_core_web_md", disable=["parser", "ner", "tagger", "lemmatizer", "textcat"])
        custom_nlp = None
    
    if args.text:
        print("==========================")
        for i in args.text:
            print("Comment:", i)
            is_toxic = detectToxicity(i, toxic_keywords, nlp, custom_nlp, args.ai, debug=args.debug)
            print("Result: ", end="")
            print("Toxic" if is_toxic else "Non-toxic")
            print("==========================")
    else:
        main_test(test_cases, toxic_keywords, nlp, custom_nlp)
    

def main_test(test_cases, toxic_keywords, nlp, custom_nlp):
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
        is_toxic = detectToxicity(comment, toxic_keywords, nlp, custom_nlp)
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
