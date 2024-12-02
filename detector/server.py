from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from main import  getOutputWithSpacyObject
import spacy

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
  source_dir = Path(__file__).parent.resolve()
  nlp = spacy.load("en_core_web_md")
  custom_nlp = spacy.load(source_dir.parent.joinpath("output/model-last").resolve())

@app.post("/api")
def getCategory(textObject: InputText):
  return getOutputWithSpacyObject(textObject.text, nlp, custom_nlp)