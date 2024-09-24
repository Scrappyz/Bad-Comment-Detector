import sys, unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1].joinpath("project").resolve()))

import main

current_dir = Path(__file__).parent.resolve()
test_cases_path = current_dir.parent.joinpath("assets/test_cases.json").resolve()
test_cases = main.getTestCases(test_cases_path)

class TestMain(unittest.TestCase):
    def test_main(self):
        for i in test_cases:
            comment = i["comment"]
            expected_result = i["expected"]
            actual_result = main.detectToxicity(comment, main.nlp)
            
            if expected_result.lower() == "toxic":
                expected_result = True
            else:
                expected_result = False
            
            self.assertEqual(actual_result, expected_result, msg=comment)
        
if __name__ == "__main__":
    unittest.main()