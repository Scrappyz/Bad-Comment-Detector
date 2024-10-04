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
def loadAndPrepareDataSetFromCSV(nlp, startRange, endRange):
  t = helper.readCSVFromFile("../assets/labeled_data.csv")
  l = []
  if endRange == None:
    endRange = len(t)
  print(endRange)
  # print(t[1][5])
  # print(t[1][6])
  for i in range(startRange, endRange):
    # print(t[6])
    doc1 = nlp(t[i][6])
    if t[i][5] == "0" or t[i][5] == "1":
      # print("Hello")
      doc1.cats["toxic"] = 1
      doc1.cats["non-toxic"] = 0
    else:
      # print("Not")
      doc1.cats["toxic"] = 0
      doc1.cats["non-toxic"] = 1
    l.append(doc1)
  return l

def loadYoutubeComments(nlp, startRange, endRange):
  t = helper.readCSVFromFile("../assets/youtoxic_english_1000.csv")
  l = []
  if endRange == None:
    endRange = len(t)
  print(endRange)
  # print(t[1][5])
  # print(t[1][6])
  for i in range(startRange, endRange):
    # print(t[6])
    doc1 = nlp(t[i][2])
    isToxic = False
    for j in range(3, 15):
      if t[i][j] == "TRUE":
        isToxic = True
        break
    if isToxic:
      # print("Hello")
      doc1.cats["toxic"] = 1
      doc1.cats["non-toxic"] = 0
    else:
      # print("Not")
      doc1.cats["toxic"] = 0
      doc1.cats["non-toxic"] = 1
    l.append(doc1)
  return l

def loadAllDPossibleTrainDataSets(nlp):
  l = []
  # l += loadAndPrepareDataSetFromCSV(nlp, 1, 13477)
  l += loadYoutubeComments(nlp, 1, 500)
  return l

def loadAllPossibleValidationDataSets(nlp):
  l = []
  # l += loadAndPrepareDataSetFromCSV(nlp, 13477, None)
  l += loadYoutubeComments(nlp, 500, None)
  return l

if __name__ == "__main__":
  nlp = spacy.load("en_core_web_md")
  trainData = loadAllDPossibleTrainDataSets(nlp)
  validationData = loadAllPossibleValidationDataSets(nlp)
  print(len(trainData))
  print(len(validationData))
  binaryTrainData = DocBin(docs=trainData)
  binaryTrainData.to_disk("../data/train.spacy")
  binaryValidData = DocBin(docs=validationData)
  binaryValidData.to_disk("../data/valid.spacy")