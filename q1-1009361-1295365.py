import re
import spacy
import pandas as pd
from collections import defaultdict
from spacy.tokenizer import _get_regex_pattern

import numpy as np
class Vectorizer(object):
    
    def __init__(self):
      self.nlp = spacy.load('en_core_web_sm')

    def load_data(self, file_path, data_col, label_col):
      df = pd.read_csv(file_path)
      documents = df[data_col].astype(str).tolist()
      labels = df[label_col].astype(int).tolist()
  
      return documents, labels

    def normalize(self, document):
        
        normalized_document = re.sub("(?<=#hashtag)([A-Z][^A-Z]*)",  r' \1 ', document.replace("#", "#hashtag"))
        normalized_document = re.split(r'(\d+)', normalized_document)
        return ' '.join(normalized_document)


    def tokenize(self, data):
        re_token_match = _get_regex_pattern(self.nlp.Defaults.token_match)
        re_token_match = f"({re_token_match}|#\w+|\w+-\w+)"
        self.nlp.tokenizer.token_match = re.compile(re_token_match).match
        doc_tokens = []
        for doc in data:
            doc = self.nlp(doc)
            doc_tokens.append([token.text for token in doc])
        return doc_tokens

      
    def cropped_vocab(self, documents, cutoff, frequency):
        word_counts = {}
        for doc in documents:
            for word in doc:
                if word not in word_counts:
                    word_counts[word] = 0
                word_counts[word] += 1
        if frequency:
            cropped_vocab = {word for word, count in word_counts.items() if count >= cutoff}
        else:
            sorted_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            cropped_vocab = {word for word, count in sorted_counts[:cutoff]}

        return cropped_vocab


    def tfidf_vectorize(self, documents, vocab, grams):
      sorted_vocab = sorted(vocab)

      matching_words_per_doc = []
      ngrams_per_doc = []
      tf_per_doc = defaultdict(int)
      idf_per_doc = defaultdict(int)
      tfidf_per_doc = defaultdict(int)
      tfidf_values_per_doc = []

      for document in documents:
          matching_words = [word for word in document if word in sorted_vocab]
          matching_words_per_doc.append(matching_words)
          newlist = [tuple(matching_words[y-grams:y]) for y in range(grams, len(matching_words)+1)]
          ngrams_per_doc.append(newlist)

      all_ngrams = set([el for lst in ngrams_per_doc for el in set(lst)])

      ngram_count_per_doc = []
      for ngram_list in ngrams_per_doc:
          ngram_count = defaultdict(int)
          for ngram in ngram_list:
              ngram_count[ngram] += 1
          ngram_count_per_doc.append(ngram_count)

      ngram_count_all_docs = defaultdict(int)
      for ngram_count in ngram_count_per_doc:
          for ngram in ngram_count:
              ngram_count_all_docs[ngram] += 1

      sorted_ngram_count_all_docs = dict(sorted(ngram_count_all_docs.items()))
      ngram_count_per_doc_with_all_ngrams = [{ngram: ngram_count.get(ngram, 0) for ngram in all_ngrams} for ngram_count in ngram_count_per_doc]
      sorted_ngram_count_per_doc = [dict(sorted(ngram_count.items())) for ngram_count in ngram_count_per_doc_with_all_ngrams]

      N = len(documents)
      for sorted_ngram_count in sorted_ngram_count_per_doc:
          for ngram, count in sorted_ngram_count.items():
              if count > 0:
                  tf_per_doc[ngram] = 1 + np.log(count)
              else:
                  tf_per_doc[ngram] = 0
          for (key, value), (key2, value2) in zip(sorted_ngram_count.items(), sorted_ngram_count_all_docs.items()):
              idf_per_doc[key]= np.log10((1+N) / (value2 + 1)) + 1
          for (key, value), (key2, value2) in zip(idf_per_doc.items(), tf_per_doc.items()):
              tfidf_per_doc[key] = round(value*value2, 3)

          tfidf_values = [i for i in tfidf_per_doc.values()]
          tfidf_values_per_doc.append(tfidf_values)

      return tfidf_values_per_doc
