import spacy

if __name__ == "__main__":
  nlp = spacy.load("../output/model-best")
  doc = nlp("Good job")
  print(doc.cats)
