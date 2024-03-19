import sys, pathlib, unittest

sys.path.append(str(pathlib.Path(__file__).parents[1].joinpath("project").resolve()))

import main

current_dir = pathlib.Path(__file__).parent.resolve()
rephrasals = main.getRephrasals(pathlib.Path.joinpath(current_dir, "../project/rephrase.json"))

class TestMain(unittest.TestCase):
    def test_main(self):
        self.assertEqual(main.rephraseComment("I won't do that", rephrasals), "i will not do that")
        self.assertEqual(main.rephraseComment("I shouldn't do that", rephrasals), "i should not do that")
        
if __name__ == "__main__":
    unittest.main()