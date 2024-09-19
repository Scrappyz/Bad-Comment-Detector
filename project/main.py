import argparse
from deep_translator import GoogleTranslator

def main():
    parser = argparse.ArgumentParser(description='Detect bad comment.')
    parser.add_argument('sentence', type=str, nargs=1,
                         help='bad comment.')
    
    args = parser.parse_args()
    
    text = args.sentence[0]
    translator = GoogleTranslator()
    translator.source = 'filipino'
    translator.target = 'english'
    
    print(translator.translate(text))

if __name__ == "__main__":
    main()