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

## Prepare Local SpaCy AI Model
On GNU/Linux:
```
cd scripts
./script.sh
```
On Windows:
```
cd scripts
.\script.bat
```

## Usage
```
usage: Bad Comment Detector [-h] [-t Text [Text ...]] [--no-ai]

options:
  -h, --help          show this help message and exit
  -t Text [Text ...]  Comment to detect
  --no-ai             Disable AI filter
```
Navigate to the `detector` directory and run `main.py` with the `-t` flag to test a comment.
```
python main.py -t "your comment to test"
```