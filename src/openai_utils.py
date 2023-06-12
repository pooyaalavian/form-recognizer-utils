import openai
from openai.error import RateLimitError
import logging
import os 
from typing import Literal
import time
import json

def setup_openai():
    logging.info("Setting up OpenAI API")
    openai.api_type: Literal["openai", "azure", "azure_ad", None] = None
    if os.getenv("OPENAI_API_KEY"):
        openai.api_type = "openai"
        openai.api_key = os.getenv("OPENAI_API_KEY")
        logging.info("Using OpenAI API")
    if os.getenv("AZURE_OPENAI_API_KEY"):
        openai.api_type = "azure"
        openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        openai.api_base = os.getenv("AZURE_OPENAI_API_ENDPOINT")
        openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        logging.info("Using Azure OpenAI API")

def call_openai(prompt, settings={},*, recursion=0) -> str:
    try:
        res = openai.Completion.create(
            engine=settings.get("engine", "text-davinci-003"),
            prompt=prompt,
            temperature=settings.get("temperature", 0.25),
            max_tokens=settings.get("max_tokens", 1500),
            top_p=settings.get("top_p", 1),
        )
        logging.debug(prompt)
        logging.debug(res.choices[0].text)
        return res.choices[0].text
    except RateLimitError:
        if recursion > 5:
            raise BaseException(f"OpenAI API call failed after {recursion+1} tries")
        # wait for 5 seconds 
        logging.info("Rate limit reached. Waiting for 5 seconds")
        time.sleep(5)
        call_openai(prompt, settings, recursion=recursion+1)
    except Exception as e:
        logging.error(e)
        raise BaseException("OpenAI API call failed")


def translate_keys_to_preset_terms(keys:list[str]):
    predefined_terms = [
        "invoice total", 
        "taxes", 
        "delivery fee", 
        "storage cost",
        "towing fee",
    ]
    prompt = '''You are an agent responsible for extracting information from a form.
    Each form uses different terminology to express the same information. 
    You are given a set of keys from the form and a set of predefined terms. 
    Find the best key that explains the term. 
    Respond with valid json, key being a predefined term and value being the matching key from the form. 
    Use null if no key matches the term. Ignore unused keys. 
    
    Predefined terms: {terms}
    
    Given terms from the form: {keys}
    
    JSON response: '''
    
    prompt = prompt.format(
        keys=', '.join([f'"{k}"' for k in keys]),
        terms=', '.join([f'"{t}"' for t in predefined_terms]),
    )
    res =  call_openai(prompt)
    try:
        d = json.loads(res)
        d_clean = {}
        d_bad = {}
        for k,v in d.items():
            k_clean = k.replace('"','').lower()
            if k_clean in predefined_terms:
                d_clean[k_clean]=v
            else:
                d_bad[k_clean]=v
        if len(d_bad) > 0:
            d_clean['_bad_keys'] = d_bad
        return d_clean
    except:
        logging.error(res)
        raise BaseException("OpenAI: failed to parse output as JSON")


setup_openai()