"""
Summarization tools
"""
from typing import Dict
from pathlib import Path

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

# imports for bert-extractive-summarizer
from summarizer import Summarizer

# chatgpt summary
import openai

openai.api_key = open("key.txt", "r").read().strip("\n")


# TODO: refactor everything into one class that updates the Dict
def spacy_summary(file: Dict, per=0.5) -> Dict:
    """
    Simple text summary with spacy.
    `file` is a dictionary containing the file location of the transcript text.
    Ideally produced by `podcasty.transcribe.transcribe`
    `per` is the percentage of highest ranking sentences to extract.
    This is very crude and a proof of concept. For semantically meaningful summaries use BERT or ChatGPT functions.
    """
    pth = file["txt"]
    assert pth.exists()
    # TODO: make sure we can process multi line .txt files (tests)
    with open(pth, "r") as text_file:
        text = text_file.read().replace("\n", "")
    # TODO: make sure en_core_web_sm is cached before initialization
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    tokens = [token.text for token in doc]
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in list(STOP_WORDS):
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency
    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]
    select_length = int(len(sentence_tokens) * per)
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_summary = [word.text for word in summary]
    summary = "".join(final_summary)
    # output summary as text file to same temporary directory
    out_path = Path(pth.parent / Path(str(pth.stem) + "_SPACY_SUMMARY.txt"))
    with open(out_path, "w") as text_file:
        text_file.write(summary)
    file["spacy_summary"] = out_path
    return file


def bert_summary(file: Dict, per=0.5) -> Dict:
    pth = file["txt"]
    assert pth.exists()
    # TODO: make sure we can process multi line .txt files (tests)
    with open(pth, "r") as text_file:
        text = text_file.read().replace("\n", "")
    # instantiate bert summarizer
    # TODO: add options for summarizer, SBERT etc.
    model = Summarizer("distilbert-base-uncased", hidden=[-1, -2], hidden_concat=True)
    summary = model(text, ratio=0.5)
    # output summary as text file to same temporary directory
    out_path = Path(pth.parent / Path(str(pth.stem) + "_BERT_SUMMARY.txt"))
    with open(out_path, "w") as text_file:
        text_file.write(summary)
    file["bert_summary"] = out_path
    return file


def chatgpt_summary(file: Dict, per=0.5) -> Dict:
    pth = file["txt"]
    assert pth.exists()
    # TODO: make sure we can process multi line .txt files (tests)
    with open(pth, "r") as text_file:
        text = text_file.read().replace("\n", "")
    # using the openai api
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Summarize the following text: {text}"}],
    )
    # TOOD: set up paid account xd
    summary = completion["choices"][0]["message"]["content"]
    out_path = Path(pth.parent / Path(str(pth.stem) + "_CHATGPT_SUMMARY.txt"))
    with open(out_path, "w") as text_file:
        text_file.write(summary)
    file["chatgpt_summary"] = out_path
    return file
