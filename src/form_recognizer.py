import os 
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient, AnalyzeResult 
from enum import Enum
import json
from pathlib import Path
import logging

endpoint = os.getenv('AZURE_FORM_RECOGNIZER_ENDPOINT')
credential = AzureKeyCredential(os.getenv('AZURE_FORM_RECOGNIZER_KEY'))
api_version = os.getenv('AZURE_FORM_RECOGNIZER_API_VERSION')
client = DocumentAnalysisClient(endpoint, credential, api_version=api_version)

class FormRecognizerModelEnum(Enum):
    OCR='prebuilt-read'
    Layout='prebuilt-layout'
    General='prebuilt-document'
    

def process_document(path: Path, model_name:FormRecognizerModelEnum=FormRecognizerModelEnum.General)->AnalyzeResult:
    logging.info(f'Processing {path}')

    try:
        out_path = str(path).replace('input','output').replace('.pdf','.json')
        logging.info(f'Loading prerecorded file {out_path}')
        f = open(out_path, 'r')
        obj = json.load(f)
        return AnalyzeResult.from_dict(obj)
    except:
        logging.info('No prerecorded file found')
        logging.info('Processing document with form recognizer')
        with open(path, 'rb'):
            poller = client.begin_analyze_document(model_name.value,path)
            return poller.result()


class KeyValuePair:
    def __init__(self, k:str, v:str, confidence:float):
        self.key=k
        self.value=v.strip()
        self.value_numeric = None
        self.is_numeric = False
        try:
            val = self.value.replace(',','').replace('$','')
            hasParanthesis = val.startswith('(') and val.endswith(')')
            val = val.replace('(','').replace(')','')
            self.value_numeric = float(val)
            self.is_numeric = True
            if hasParanthesis and self.value_numeric>0:
                self.value_numeric = -self.value_numeric
        except:
            pass
        self.confidence=confidence
        if self.key.endswith(':'):
            self.key = self.key[:-1]
    
    def __str__(self):
        val = self.value if not self.is_numeric else f'{self.value_numeric}'
        return f'[{self.key}]: [{val}] ({self.confidence})'
        
def clean_key_vals(res:AnalyzeResult):
    kv = res.key_value_pairs
    ans = []
    for k in kv:
        ans.append(KeyValuePair(k.key.content, '' if k.value is None else k.value.content, k.confidence))
    return ans