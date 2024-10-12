import spacy
from pathlib import Path

if __name__ == "__main__":
  source_dir = Path(__file__).parent.resolve()
  nlp = spacy.load(source_dir.parent.joinpath("output/model-last").resolve())
  doc = nlp("great job, it works so well")
  print(doc.text)
  print(doc.cats)
  doc = nlp("fuck you")
  print(doc.text)
  print(doc.cats)
