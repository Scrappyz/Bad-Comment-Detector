import sys, unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1].joinpath("project").resolve()))

import main

current_dir = Path(__file__).parent.resolve()
asset_dir = current_dir.parent.joinpath("assets").resolve()

test_cases_path = asset_dir.joinpath("test_cases.json").resolve()
toxic_keywords_path = asset_dir.joinpath("toxic_keywords.json").resolve()

test_cases = main.readJsonFromFile(test_cases_path)
toxic_keywords = set(main.readJsonFromFile(toxic_keywords_path))

class TestMain(unittest.TestCase):
    def test_cleaning(self):
        for i in test_cases:
            if "cleaned" not in i:
                continue
            self.assertEqual(i["cleaned"], " ".join(main.cleanTextAndTokenize(i["comment"], toxic_keywords)))
            
    def test_toxicity(self):
        for i in test_cases:
            comment = i["comment"]
            expected_result = i["expected"]
            actual_result = main.detectToxicity(comment, toxic_keywords, main.nlp, 50)
            
            if expected_result.lower() == "toxic":
                expected_result = True
            else:
                expected_result = False
            
            self.assertEqual(actual_result, expected_result, msg=comment)
        
if __name__ == "__main__":
    unittest.main()