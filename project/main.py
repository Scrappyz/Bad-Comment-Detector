import argparse
from deep_translator import GoogleTranslator

def main():
    text = "Magandang hapon!"
    translator = GoogleTranslator(source="auto")
    translator.target = "english"
    
    print(translator.translate(text))

if __name__ == "__main__":
    main()