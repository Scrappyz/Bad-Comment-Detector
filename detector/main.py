import argparse
from pathlib import Path
import preprocess
import helper
import spacy
from os import getcwd

def ruleBasedDetection(tokens, keywords: dict, debug=False):
    # Detect toxicity using rule-based methods.
    keywords_list = list(keywords.keys())
    for i in tokens:
        text = str(i)
        substrings = list(preprocess.findAllSubstrings(text, keywords_list))
        if substrings:
            substr = substrings[0]
            if "center" in keywords[substr] and keywords[substr]["center"] and preprocess.isSubstring(text, keywords[substr]["center"]):
                continue
            
            if "left" in keywords[substr] and keywords[substr]["left"] and preprocess.isSubstring(text, keywords[substr]["left"]):
                continue
            
            if "right" in keywords[substr] and keywords[substr]["right"] and preprocess.isSubstring(text, keywords[substr]["right"]):
                continue
            return True
    return False

def aiBasedDetection(tokens, nlp, threshold):
    # Detect toxicity using spaCy's AI-based model.
    threshold /= 100
    
    # Assuming the model's 'cats' attribute gives the category probabilities
    if 'toxic' in tokens.cats and tokens.cats['toxic'] >= threshold:
        return True  # Toxic based on AI model
    
    return False

def detectToxicity(text, keywords: dict, stopwords: set, nlp, custom_nlp, threshold, ai=True, debug=False):
    # Hybrid approach combining rule-based and AI-based toxicity detection.
    # Step 1: Clean the text
    cleaned_text = preprocess.cleanText(text, set(keywords.keys()), stopwords, nlp)
    
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
        is_toxic = aiBasedDetection(tokens, custom_nlp, threshold)
        if debug:
            print("Detection: AI")
            print("Categories:", tokens.cats)
        return is_toxic

    if debug:
        print("Detection: None")
    return False

def main():
    source_dir = Path(__file__).parent.resolve()
    asset_dir = source_dir.parent.joinpath("assets")
    config_file = Path(__file__).parent.joinpath("config.json").resolve()
    # print(config_file)
    config = helper.readJsonFromFile(config_file)
    test_cases = list(helper.readJsonFromFile(asset_dir.joinpath("test_cases.json")))
    feedback_data_file = config["feedbackDataFile"]
    
    if not Path(feedback_data_file).is_absolute():
        feedback_data_file = Path(source_dir).joinpath(feedback_data_file).resolve()
    
    parser = argparse.ArgumentParser("Bad Comment Detector")
    parser.add_argument("-t", dest="text", metavar="Text", nargs='+', type=str, help="Comment to detect", required=False)
    parser.add_argument("--no-ai", dest="ai", action="store_false", required=False, help="Disable AI filter")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", required=False, help="Debug mode")
    parser.add_argument("-r", "--result", dest="result", nargs=1, type=str, required=False, help="Expected result with the given comment (e.g. 'toxic' or 'non-toxic')")
    parser.add_argument("--set-threshold", dest="threshold", nargs=1, type=int, required=False, help="Set toxicity threshold from 0-100")
    parser.add_argument("--set-feedback-file", dest="feedback_file", nargs=1, type=str, required=False, help="Set CSV file to put feedback")
    
    args = parser.parse_args()
    
    if args.threshold:
        config["threshold"] = args.threshold[0]
        helper.writeJsonToFile(config_file, config)
        return
    
    if args.feedback_file:
        config["feedbackDataFile"] = str(Path(getcwd()).joinpath(args.feedback_file[0]).resolve()) if not Path(args.feedback_file[0]).is_absolute() else args.feedback_file[0]
        helper.writeJsonToFile(config_file, config)
        return
    
    if args.ai:
        nlp = spacy.load("en_core_web_md")
        custom_nlp = spacy.load(source_dir.parent.joinpath("output/model-last").resolve())
        # print("With AI")
    else:
        nlp = spacy.load("en_core_web_md", disable=["parser", "ner", "tagger", "lemmatizer", "textcat"])
        custom_nlp = None
        
    toxic_keywords = dict(helper.readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    stopwords = set(nlp.Defaults.stop_words)
    stopwords -= set(helper.readJsonFromFile(Path(__file__).parent.parent.joinpath("assets/exclude_stopwords.json").resolve()))
    
    args.text = ["youre ugly"]
    if args.text:
        print("==========================")
        for i in args.text:
            print("Comment:", i)
            is_toxic = detectToxicity(i, toxic_keywords, stopwords, nlp, custom_nlp, config["threshold"], args.ai, args.debug)
            print("Result: ", end="")
            print("Toxic" if is_toxic else "Non-toxic")
            print("==========================")
        
        if args.result:
            arr = []
            result = str(args.result[0]).lower()
            result = "1" if result == "toxic" or result == "1" else "0"
            for i in args.text:
                arr.append([i, result])
            helper.appendToCSVFile(feedback_data_file, arr)
    else:
        main_test(test_cases, toxic_keywords, stopwords, nlp, custom_nlp, config["threshold"])
    

def main_test(test_cases, toxic_keywords, stopwords, nlp, custom_nlp, threshold):
    # Main function to run toxicity detection on test cases.
    source_dir = Path(__file__).parent.resolve()
    
    score = 0
    total = 0
    pass_test_case = False

    for i in test_cases:
        total += 1
        comment = i["comment"]
        expected_result = i["expected"]
        is_toxic = detectToxicity(comment, toxic_keywords, stopwords, nlp, custom_nlp, threshold, True, False)
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
