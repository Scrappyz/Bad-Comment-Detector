import spacy

if __name__ == "__main__":
  nlp = spacy.load("../output/model-last")
  doc = nlp("great job, it works so well")
  print(doc.text)
  print(doc.cats)
  doc = nlp("fuck you")
  print(doc.text)
  print(doc.cats)
