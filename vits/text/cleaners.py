""" from https://github.com/keithito/tacotron """

'''
Cleaners are transformations that run over the input text at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English text
  2. "transliteration_cleaners" for non-English text that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
'''

import re
import gruut
from unidecode import unidecode


# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')


def lowercase(text):
  return text.lower()


def collapse_whitespace(text):
  return re.sub(_whitespace_re, ' ', text)


def convert_to_ascii(text):
  return unidecode(text)


def gruut_cleaner(text):
    # Table for str.translate to fix gruut/TTS phoneme mismatch
    GRUUT_TRANS_TABLE = str.maketrans("g", "ɡ")

    text = lowercase(text)

    sentences = gruut.sentences(text, lang="de_de", major_breaks=False, minor_breaks=False)

    ph_list = []

    for sent in sentences:
      for word in sent:
        if word.phonemes:
          ph_list.append("".join(word.phonemes))

    clean_text = " ".join(ph_list)

    # Fix a few phonemes
    clean_text = (
        clean_text.translate(GRUUT_TRANS_TABLE)
        .replace(" .", ".")
        .replace(" ?", "?")
        .replace(" !", "!")
        .replace(" ,", ",")
        .replace(" :", ":")
        .replace(" ;", ";")
    )
    clean_text = collapse_whitespace(clean_text)
    print(clean_text)

    return clean_text