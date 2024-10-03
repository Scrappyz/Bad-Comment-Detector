import spacy
from spacy.tokens import DocBin

import helper

def loadAndPrepareDataSet(nlp):
  test_cases = list(helper.readJsonFromFile("../assets/test_cases.json"))
  l = []
  for t in test_cases:
    doc1 = nlp(t["comment"])
    doc2 = nlp(t["cleaned"])
    if t["expected"] == "Toxic":
      doc1.cats["toxic"] = 1
      doc1.cats["non-toxic"] = 0
      doc2.cats["toxic"] = 1
      doc2.cats["non-toxic"] = 0
    else:
      doc1.cats["toxic"] = 0
      doc1.cats["non-toxic"] = 1
      doc2.cats["toxic"] = 0
      doc2.cats["non-toxic"] = 1
    l.append(doc1)
    l.append(doc2)
  return l

if __name__ == "__main__":
  nlp = spacy.load("en_core_web_md")
  trainData = loadAndPrepareDataSet(nlp)
  binaryData = DocBin(docs=trainData)
  binaryData.to_disk("../data/train.spacy")
  binaryData.to_disk("../data/valid.spacy")