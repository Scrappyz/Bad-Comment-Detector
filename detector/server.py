from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from main import  getOutputWithSpacyObject
import spacy
# import tracemalloc

class InputText(BaseModel):
  text: str

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

nlp = None
custom_nlp = None

@app.on_event("startup")
def on_startup():
  global nlp, custom_nlp
  # tracemalloc.start()
  source_dir = Path(__file__).parent.resolve()
  # nlp = spacy.load("en_core_web_md")
  custom_nlp = spacy.load(source_dir.parent.joinpath("output/model-last").resolve())
  # current, peak = tracemalloc.get_traced_memory()
  # print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
  # tracemalloc.stop()

@app.post("/api")
def getCategory(textObject: InputText):
  return getOutputWithSpacyObject(textObject.text, custom_nlp, 60)