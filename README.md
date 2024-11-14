## Bad-Comment-Detector
A python script to detect toxic comments.

## Installation
```
git clone https://github.com/Scrappyz/Bad-Comment-Detector.git
cd Bad-Comment-Detector
pip install .
python -m spacy download en_core_web_md
```
Run these commands in your preferred terminal.

## Train SpaCy AI Model
```
cd scripts
python train.py
```
**Note:** No need to train to run the program.

## Usage
```
usage: Bad Comment Detector [-h] [-t Text [Text ...]] [--no-ai] [-d] [-r RESULT] [--set-threshold THRESHOLD]
                            [--set-feedback-file FEEDBACK_FILE]

options:
  -h, --help            show this help message and exit
  -t Text [Text ...]    Comment to detect
  --no-ai               Disable AI filter
  -d, --debug           Debug mode
  -r RESULT, --result RESULT
                        Expected result with the given comment (e.g. 'toxic' or 'non-toxic')
  --set-threshold THRESHOLD
                        Set toxicity threshold from 0-100
  --set-feedback-file FEEDBACK_FILE
                        Set CSV file to put feedback
```
Navigate to the `detector` directory and run `main.py` with the `-t` flag to test a comment.

### Testing
To test a comment, do:
```
python main.py -t "your comment to test"
```

Also allows multiple comments.
```
python main.py -t "first comment" "second comment" "third comment"
```

Add the `-d` flag for a more verbose response such as what detection type was used.
```
python main.py -t "first comment" "second comment" "third comment" -d
```

### Adding Training Data
To add training data, do:
```
python main.py -t "you suck" "this README is terrible" "go to hell" -r "toxic"
```

The value of `-r` is the expected result of the given comments.

Each comment will be put on a CSV file with the designated result in `-r`. In this case, `you suck`, `this README is terrible`, and `go to hell` will have a label of `toxic` or `1` in the CSV file. You can also put in `1` or `0` in the `-r` argument where `1` means `toxic` and `0` means `non-toxic`.