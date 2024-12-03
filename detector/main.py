import argparse
from pathlib import Path
import preprocess
import helper
import spacy
from os import getcwd

def ruleBasedDetection(tokens, keywords: dict, debug=False):
    # Detect toxicity using rule-based methods.
    keywords_list = list(keywords.keys())
    for i in range(len(tokens)):
        text = str(tokens[i])
        substrings = list(preprocess.findAllSubstrings(text, keywords_list))
        if substrings:
            substr = substrings[0]
            
            # Check current token if it has an excluded substring
            if "center" in keywords[substr] and keywords[substr]["center"] and preprocess.isSubstring(text, keywords[substr]["center"]):
                continue
            
            # Check next token if it has an excluded substring
            text = "" if i >= len(tokens)-1 else str(tokens[i+1])
            if text and "right" in keywords[substr] and keywords[substr]["right"] and preprocess.isSubstring(text, keywords[substr]["right"]):
                continue
            
            # Check previous token if it has an excluded substring
            text = "" if i <= 0 else str(tokens[i-1])
            if text and "left" in keywords[substr] and keywords[substr]["left"] and preprocess.isSubstring(text, keywords[substr]["left"]):
                continue
            
            return True
    return False

def aiBasedDetection(tokens, nlp, threshold):
    # Detect toxicity using spaCy's AI-based model.
    threshold /= 100
    
    # Assuming the model's 'cats' attribute gives the category probabilities
    if 'toxic' in tokens.cats and tokens.cats['toxic'] >= threshold or tokens.cats['toxic'] > tokens.cats['non-toxic']:
        return True  # Toxic based on AI model
    
    return False

def detectToxicity(text, keywords: dict, stopwords: set, custom_nlp, threshold, rulebased=True, ai=True, debug=False) -> dict:
    # Hybrid approach combining rule-based and AI-based toxicity detection.
    # Step 1: Clean the text
    output = {}
    cleaned_text = preprocess.cleanText(text, set(keywords.keys()), stopwords, custom_nlp)
    output["comment"] = text
    
    if debug:
        output["cleaned"] = cleaned_text
        
    tokens = custom_nlp(cleaned_text)
    
    # Step 2: Rule-based detection
    if rulebased and ruleBasedDetection(tokens, keywords):
        if debug:
            output["detection"] = "rule-based"
        output["result"] = "toxic"
        return output
    
    if not ai:
        output["result"] = "non-toxic"
        return output
    
    # Step 3: AI-based detection
    if ai:
        tokens = custom_nlp(cleaned_text)
        is_toxic = aiBasedDetection(tokens, custom_nlp, threshold)
        if debug:
            output["detection"] = "ai"
            output["categories"] = dict(tokens.cats)
        output["result"] = "toxic" if is_toxic else "non-toxic"
        return output

    if debug:
        output["detection"] = ""
    return output

def main():
    current_dir = Path(getcwd())
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
    parser.add_argument("-t", dest="text", metavar="Text", nargs='+', required=False, type=str, help="Comment to detect")
    parser.add_argument("--no-rule", dest="rule", action="store_false", required=False, help="Disable Rule-based filter")
    parser.add_argument("--no-ai", dest="ai", action="store_false", required=False, help="Disable AI filter")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", required=False, help="Debug mode")
    parser.add_argument("-r", "--result", dest="result", nargs=1, type=str, required=False, help="Expected result with the given comment (e.g. 'toxic' or 'non-toxic')")
    parser.add_argument("-f", "--file", dest="file", nargs='+', type=str, required=False, help="File input. (e.g. `comments.txt`)")
    parser.add_argument("-o", "--output", dest="output", nargs=1, type=str, required=False, help="Output to file. (e.g. 'output.json`)")
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
    
    inputs = []
    
    if args.file:
        for i in args.file:
            inputs += helper.readCommentsFromFile(current_dir.joinpath(i).resolve())
    elif args.text:
        inputs = args.text
        
    outputs = []
    if inputs:
        for i in inputs:
            outputs.append(detectToxicity(i, toxic_keywords, stopwords, nlp, custom_nlp, config["threshold"], args.rule, args.ai, args.debug))
        
        if args.result:
            arr = []
            result = str(args.result[0]).lower()
            result = "1" if result == "toxic" or result == "1" else "0"
            for i in inputs:
                arr.append([i, result])
            helper.appendToCSVFile(feedback_data_file, arr)
        
        print("=============================")
        for i in range(len(outputs)):
            for k, v in outputs[i].items():
                print(k.title() + ":", v if k == "comment" or k == "cleaned" or k == "categories" else v.title())
            print("=============================")
            
        if args.output:
            output_path = current_dir.joinpath(args.output[0]).resolve()
            file_extension = output_path.suffix
            
            helper.writeJsonToFile(output_path, outputs)
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
        output = detectToxicity(comment, toxic_keywords, stopwords, nlp, custom_nlp, threshold, True, True, False)
        if output["result"] == expected_result.lower():
            pass_test_case = True
            score += 1
        else:
            pass_test_case = False
        print("[{3}] Result: {0}, Expected: {1}, Comment: {2}".format(output["result"].title(), expected_result, comment, pass_test_case))
    
    print("Score: " + str(score) + "/" + str(total))

def getOutput(str):
    current_dir = Path(getcwd())
    source_dir = Path(__file__).parent.resolve()
    asset_dir = source_dir.parent.joinpath("assets")
    toxic_keywords = dict(helper.readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    nlp = spacy.load("en_core_web_md")
    custom_nlp = spacy.load(source_dir.parent.joinpath("output/model-last").resolve())
    stopwords = set(nlp.Defaults.stop_words)
    stopwords -= set(helper.readJsonFromFile(Path(__file__).parent.parent.joinpath("assets/exclude_stopwords.json").resolve()))
    return detectToxicity(str, toxic_keywords, stopwords, nlp, custom_nlp, 75, True, True, True)['result']

def getOutputWithSpacyObject(str, custom_nlp, threshold):
    source_dir = Path(__file__).parent.resolve()
    asset_dir = source_dir.parent.joinpath("assets")
    toxic_keywords = dict(helper.readJsonFromFile(asset_dir.joinpath("toxic_keywords.json")))
    stopwords = set(custom_nlp.Defaults.stop_words)
    stopwords -= set(helper.readJsonFromFile(Path(__file__).parent.parent.joinpath("assets/exclude_stopwords.json").resolve()))
    return detectToxicity(str, toxic_keywords, stopwords, custom_nlp, threshold, True, True, True)

if __name__ == "__main__":
    main()
