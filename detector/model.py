import spacy
from spacy.tokens import DocBin
from pathlib import Path

import helper
import preprocess

# Project root directory
root_dir = Path(__file__).parent.parent.resolve()

def loadLabeledData(nlp, startRange, endRange, keywords, stopwords):
  t = helper.readCSVFromFile(root_dir.joinpath("assets/training/labeled_data.csv").resolve())
  l = []
  
  if endRange == None:
    endRange = len(t)

  for i in range(startRange, endRange):
    comment = preprocess.cleanText(t[i][6], keywords, stopwords, nlp)
    doc1 = nlp(comment)
    
    if t[i][5] == "0" or t[i][5] == "1":
      doc1.cats["toxic"] = 1
      doc1.cats["non-toxic"] = 0
    else:
      doc1.cats["toxic"] = 0
      doc1.cats["non-toxic"] = 1
      
    l.append(doc1)
    
  return l

def loadYoutubeComments(nlp, startRange, endRange, keywords, stopwords):
  t = helper.readCSVFromFile(root_dir.joinpath("assets/training/youtoxic_english_1000.csv").resolve())
  l = []
  
  if endRange == None:
    endRange = len(t)
    
  for i in range(startRange, endRange):
    comment = preprocess.cleanText(t[i][2], keywords, stopwords, nlp)
    doc1 = nlp(comment)
    isToxic = False
    
    for j in range(3, 15):
      if t[i][j] == "TRUE":
        isToxic = True
        break
      
    if isToxic:
      doc1.cats["toxic"] = 1
      doc1.cats["non-toxic"] = 0
    else:
      doc1.cats["toxic"] = 0
      doc1.cats["non-toxic"] = 1
      
    l.append(doc1)
    
  return l

def loadCustomDataset(file_path, nlp, start_range, end_range, keywords, stopwords):
  t = helper.readCSVFromFile(file_path)
  l = []
  
  if end_range == None:
    end_range = len(t)
    
  for i in range(start_range, end_range):
    comment = preprocess.cleanText(t[i][0], keywords, stopwords, nlp)
    doc1 = nlp(comment)
    is_toxic = False
    
    if t[i][1] == "1":
        is_toxic = True
      
    if is_toxic:
      doc1.cats["toxic"] = 1
      doc1.cats["non-toxic"] = 0
    else:
      doc1.cats["toxic"] = 0
      doc1.cats["non-toxic"] = 1
      
    l.append(doc1)
    
  return l

def loadKaggleDataset(nlp, startRange, endRange, keywords, stopwords):
  t = helper.readCSVFromFile(root_dir.joinpath("assets/training/kaggle_train_data.csv").resolve())
  l = []
  
  if endRange == None:
    endRange = len(t)
    
  for i in range(startRange, endRange):
    # print("=================")
    # print("Index:", i)
    # print(t[i][1])
    comment = preprocess.cleanText(t[i][1], keywords, stopwords, nlp)
    doc1 = nlp(comment)
    isToxic = False
    # print(comment)
    # print("=================")
    
    for j in range(2, 8):
      if t[i][j] == "1":
        isToxic = True
        break
      
    if isToxic:
      doc1.cats["toxic"] = 1
      doc1.cats["non-toxic"] = 0
    else:
      doc1.cats["toxic"] = 0
      doc1.cats["non-toxic"] = 1
      
    l.append(doc1)
    
  return l

def loadAllPossibleTrainDataSets(nlp, keywords, stopwords):
  l = []
  l += loadLabeledData(nlp, 1, None, keywords, stopwords)
  l += loadYoutubeComments(nlp, 1, None, keywords, stopwords)
  l += loadCustomDataset(root_dir.joinpath("assets/training/custom_data.csv").resolve(), nlp, 1, None, keywords, stopwords)
  l += loadCustomDataset(root_dir.joinpath("assets/training/feedback_data.csv").resolve(), nlp, 1, None, keywords, stopwords)
  l += loadKaggleDataset(nlp, 1, 1000, keywords, stopwords)
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