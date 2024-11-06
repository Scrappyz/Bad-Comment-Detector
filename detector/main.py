import argparse
from pathlib import Path
import preprocess
import helper
import spacy

def ruleBasedDetection(tokens, keywords: set, debug=False):
    # Detect toxicity using rule-based regex patterns.
    for i in tokens:
        if preprocess.isSubstring(str(i), keywords):
            return True
    return False

def aiBasedDetection(tokens, nlp):
    # Detect toxicity using spaCy's AI-based model.

    # Assuming the model's 'cats' attribute gives the category probabilities
    if 'toxic' in tokens.cats and tokens.cats['toxic'] > 0.6:
        return True  # Toxic based on AI model
    
    return False

def detectToxicity(text, keywords: set, stopwords: set, nlp, custom_nlp, ai=True, threshold=65, debug=False):
    # Hybrid approach combining rule-based and AI-based toxicity detection.
    # Step 1: Clean the text
    cleaned_text = preprocess.cleanText(text, keywords, stopwords, nlp)
    
    if debug:
        print("Cleaned:", cleaned_text)
        
    tokens = nlp(cleaned_text)
    
    # Step 2: Rule-based detection
    if ruleBasedDetection(tokens, keywords):
        if debug:
            print("Detection: Rule-based")
        return True  # Mark as toxic if rule-based approach detects it
    
    # Step 3: AI-based detection
    if ai:
        tokens = custom_nlp(cleaned_text)
        toxic = aiBasedDetection(tokens, custom_nlp)
        if debug:
            print("Detection: AI")
            print("Categories:", tokens.cats)
        return toxic

    print("Detection: None")
    return False

def main():
    source_dir = Path(__file__).parent.resolve()
    asset_dir = source_dir.parent.joinpath("assets")
    test_cases = list(helper.readJsonFromFile(asset_dir.joinpath("test_cases.json")))
    
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
        
    toxic_keywords = set(helper.readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    stopwords = set(nlp.Defaults.stop_words)
    stopwords -= set(helper.readJsonFromFile(Path(__file__).parent.parent.joinpath("assets/exclude_stopwords.json").resolve()))
        
    if args.text:
        print("==========================")
        for i in args.text:
            print("Comment:", i)
            is_toxic = detectToxicity(i, toxic_keywords, stopwords, nlp, custom_nlp, args.ai, debug=args.debug)
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
