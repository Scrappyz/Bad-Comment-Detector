import spacy
from spacy.tokens import DocBin
from pathlib import Path

import helper
import detector.parser_1 as parser_1

# Project root directory
root_dir = Path(__file__).parent.parent.resolve()

# import main

# def loadAndPrepareDataSet(nlp):
#   test_cases = list(helper.readJsonFromFile("../assets/test_cases.json"))
#   l = []
#   for t in test_cases:
#     doc1 = nlp(t["comment"])
#     doc2 = nlp(t["cleaned"])
#     if t["expected"] == "Toxic":
#       doc1.cats["toxic"] = 1
#       doc1.cats["non-toxic"] = 0
#       doc2.cats["toxic"] = 1
#       doc2.cats["non-toxic"] = 0
#     else:
#       doc1.cats["toxic"] = 0
#       doc1.cats["non-toxic"] = 1
#       doc2.cats["toxic"] = 0
#       doc2.cats["non-toxic"] = 1
#     l.append(doc1)
#     l.append(doc2)
#   return l

def loadAndPrepareDataSetFromCSV(nlp, startRange, endRange, keywords, stopwords):
  t = helper.readCSVFromFile(root_dir.joinpath("assets/training/labeled_data.csv").resolve())
  # print("Length: " + str(len(t)))
  l = []
  if endRange == None:
    endRange = len(t)
  # print(endRange)
  # print(t[1][5])
  # print(t[1][6])
  for i in range(startRange, endRange):
    # print(t[6])
    comment = parser_1.cleanText(t[i][6], keywords, stopwords, nlp)
    doc1 = nlp(comment)
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

def loadYoutubeComments(nlp, startRange, endRange, keywords, stopwords):
  t = helper.readCSVFromFile(root_dir.joinpath("assets/training/youtoxic_english_1000.csv").resolve())
  # print(len(t))
  l = []
  if endRange == None:
    endRange = len(t)
  # print(endRange)
  # print(t[1][5])
  # print(t[1][6])
  for i in range(startRange, endRange):
    # print(t[6])
    comment = parser_1.cleanText(t[i][2], keywords, stopwords, nlp)
    doc1 = nlp(comment)
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

def loadTCCC(nlp, startRange, endRange, keywords, stopwords):
  t = helper.readCSVFromFile(root_dir.joinpath("assets/training/youtoxic_english_1000.csv").resolve())
  # print("Length is " + str(len(t)))
  # print("Comment: " + t[1][1])
  l = []
  if endRange == None:
    endRange = len(t)
  print(endRange)
  for i in range(startRange, endRange):
    # print(t[6])
    comment = parser_1.cleanText(t[i][1], keywords, stopwords, nlp)
    doc1 = nlp(comment)
    isToxic = False
    for j in range(2, 8):
      if t[i][j] == "1":
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

def loadAllPossibleTrainDataSets(nlp, keywords, stopwords):
  l = []
  l += loadAndPrepareDataSetFromCSV(nlp, 1, None, keywords, stopwords)
  l += loadYoutubeComments(nlp, 1, None, keywords, stopwords)
  l += loadTCCC(nlp, 1, None, keywords, stopwords)
  return l

if __name__ == "__main__":
  print("----- model.py -----")
  print("Preparing data sets...")
  nlp = spacy.load("en_core_web_md")
  keywords = set(helper.readJsonFromFile(root_dir.joinpath("assets/toxic_keywords.json").resolve()))
  stopwords = set(nlp.Defaults.stop_words)
  stopwords -= set(helper.readJsonFromFile(root_dir.joinpath("assets/exclude_stopwords.json").resolve()))
  
  trainData = loadAllPossibleTrainDataSets(nlp, keywords, stopwords)
  # print(len(trainData))
  # print(len(validationData))
  print("------ Saving data ------")
  binaryTrainData = DocBin(docs=trainData)
  binaryTrainData.to_disk(root_dir.joinpath("data/train.spacy").resolve())
  binaryTrainData.to_disk(root_dir.joinpath("data/valid.spacy").resolve())
  print("------ DONE ------")