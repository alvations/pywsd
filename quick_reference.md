### Calculate similarity between two documents or words:
```
## Document similarity
>>> import pywsd

>>> pywsd.cosine.cosine_similarity(text1, text2)

## Word similarity
## Use max_similarity for unified interface, options: path, wup, lch, res, jcn, lin 
>>> law = wn.synsets("law")[0]
>>> doc = wn.synsets("document")[0]
>>> pywsd.similarity.similarity_by_path(law, doc, option="path") # same as wn.path_similarity(law, doc)
0.125
>>> pywsd.similarity.similarity_by_path(law, doc, option="wup") # same as win.wup_similarity(law, doc)
0.36363636363636365

## Note to investigate, default option="path" does not work (TypeError - invalid comparison of NoneType)
>>> pywsd.similarity.max_similarity("The law is certain the law is absolute", "law", option="res")
Synset('police.n.01')
>>> pywsd.similarity.max_similarity("The law is certain the law is absolute", "law", option="jcn")
Synset('police.n.01')
```

### Custom word sense
(Works by counting how often each of its synsets' lemmas appears in Brown)
```
>>> from pywsd.baseline import max_lemma_count
>>> max_lemma_count("dog")
Synset('dog.n.01')
>>> max_lemma_count("cat")
Synset('guy.n.01')
>>> pywsd.baseline.max_lemma_count("law").definition()
'the collection of rules imposed by authority'
```

```
>>> law = pywsd.baseline.max_lemma_count("law")
>>> law
Synset('law.n.01')
>>> pywsd.lesk.synset_signatures(law) # SYNSET --> SET # truncated output
{'international_law', 'case_law', 'jurisprudence', 'law_of_nations', 'sharia', 
'commercial_law', 'tax_law', 'mercantile_law', 'shariah', 'order', 
'shariah_law', 'rule', 'allow', 'civil_law', 'securities_law', 'respect', 'law'}
```

### Signatures and API type reference:<br>

```
>>> law_sigs = pywsd.lesk.signatures("law") # returns a dict of form {wn.Synset : set}
>>> law_sigs
{
Synset('law.n.01'): {'international_law', 'case_law', ...},
...,
Synset('jurisprudence.n.01'): {'legal_philosophy', 'concerned',...}
}

>>> sent = "The law is certain the law is absolute"

>>> token_sent = sent.split() # ["The", "law", ...]
>>> pywsd.lesk.compare_overlaps(token_sent, law_sigs) # List(strings), dict{Synset:set} --> Synset
Synset('police.n.01')
>>> pywsd.lesk.compare_overlaps_greedy(sent, law_sigs) # List(strings), dict{Synset:set} --> Synset
Synset('law.n.01')

>>> pywsd.lesk.cosine_lesk(sent, "law")
Synset('law.n.01')
>>> pywsd.lesk.cosine_lesk(sent, "police")
Synset('police.n.01')
```

### Comparison of lesk disambiguation algorithms:<br>

```
>>> pywsd.lesk.cosine_lesk(sent, "enforce")
Synset('enforce.v.01')
>>> pywsd.lesk.adapted_lesk(sent, "enforce")
Synset('enforce.v.02')
>>> pywsd.lesk.simple_lesk(sent, "enforce")
Synset('enforce.v.02')
```
