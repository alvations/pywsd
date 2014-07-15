import os, re, string
from collections import defaultdict
from itertools import chain, izip

from nltk import word_tokenize

#############################################################################

def per_section(it):
    """ Read a file and yield sections using empty line as delimiter """
    section = []
    for line in it:
        if line.strip('\n'):
            section.append(line)
        else:
            yield ''.join(section)
            section = []
    # yield any remaining lines as a section too
    if section:
        yield ''.join(section)
        
def extract_between_quotations(string, double=True):
    return re.findall(r'\"(.+?)\"',string)


def grouped(iterable, n):
    return izip(*[iter(iterable)]*n)

def tokens_fromto(sentence):
    spaces = [0] + list(chain(*[(spaceloc,spaceloc+1) for spaceloc,tok \
                in enumerate(sentence) if tok == " "])) + [len(sentence)]
    for i in grouped(spaces, 2):
        yield i, sentence[i[0]:i[1]]

def remove_punct(token):
    return "".join([ch for ch in token if ch not in string.punctuation])

##############################################################################
ace_download_url = "http://sweaglesw.org/linguistics/ace/download/"
ace_bleeding_edge =  "ace-0.9.17-x86-64.tar.gz"
ace_version =  ace_bleeding_edge.partition('-x86-64')[0]

erg_bleeding_edge = "erg-1212-x86-64-0.9.17.dat.bz2"
erg_version = erg_bleeding_edge.rpartition('.')[0]

home_path = os.path.expanduser("~") + "/"
ace_cmd = "~/aceparser/" + ace_version + "/ace -g ~/aceparser/" + erg_version + " " 
ace_path = home_path + "aceparser/"

erg_lextdl = home_path + '/delphin/erg/lexicon.tdl'

def install_ace():
    if not os.path.exists(ace_path):
        os.makedirs(ace_path)

    # Downloads ACE and ERG.
    if not os.path.exists(home_path + ace_bleeding_edge):
        download_ace = " ".join(["wget", "-P", home_path, 
                         ace_download_url+ace_bleeding_edge])
        os.system(download_ace)
    if not os.path.exists(home_path + erg_bleeding_edge):
        download_erg = " ".join(["wget", "-P", home_path, 
                        ace_download_url+erg_bleeding_edge ])
        os.system(download_erg)

    # Exact ACE and ERG.
    if not os.path.exists(ace_path+ace_version+"/ace"):
        extract_ace = " ".join(["tar", "-zxvf", home_path+ace_bleeding_edge, 
                        "-C", ace_path])
        os.system(extract_ace)
    if not os.path.exists(ace_path+erg_version):
        extract_erg = " ".join(["bzip2", "-dc", home_path+erg_bleeding_edge, 
                                ">", ace_path+erg_version])
        os.system(extract_erg)
        
def ace_parse(sent, onlyMRS=False, parameters="", bestparse=False):
    if onlyMRS == True:
            parameters+=" -T"
    pipe_sent_in = "echo " +sent+" | "
    cmd = pipe_sent_in + ace_cmd +" 2> silence"
    ace_output = [p.strip() for p in os.popen(cmd) 
                  if p.strip() != ""]
    if bestparse:
        return ace_output[1]
    else:
        return ace_output

def erg_lexicon(lextdl=erg_lextdl):
    lexkey_name = defaultdict(list)
    with open(lextdl, 'r') as fin:
        for entry in per_section(fin):
            if not entry.strip(): # skip empty lines.
                continue
            entry = entry.strip()
            lexkey = entry.split(":=")[0]
            
            # Getting the ORTH values.
            orth = re.findall(r'ORTH \<(.*?)\>,', entry)
            if not orth:
                orth = re.findall(r'ORTH \<(.*?)\>', entry)
            orth = orth[0]
            lexnames = extract_between_quotations(orth)
            lexkey_name[lexkey].append(lexnames)
            
            # Getting the KEYREL.PRED values.
            keyrelpred = re.findall(r'KEYREL\.PRED (.*?) ]', entry)
            if keyrelpred:
                lexkey2 = keyrelpred[0]
                if lexkey2.strip().startswith('"'):
                    lexkey2 = extract_between_quotations(lexkey2)[0]
                lexkey_name[lexkey2].append(lexnames)
                    
            # Getting the LKEYS.KEYREL.PRED values.
            lkeyskeyrelpred = re.findall(r'LKEYS\.KEYREL\.PRED (.*?),', entry)
            if lkeyskeyrelpred:
                lkeyskeyrelpred = lkeyskeyrelpred[0]
                if lkeyskeyrelpred.startswith('"'):
                    lexkey3 = extract_between_quotations(lkeyskeyrelpred)[0]
                else:
                    lexkey3 = lkeyskeyrelpred
                lexkey_name[lexkey3].append(lexnames)
           
    return lexkey_name

unwanted_rels = ['_a_q_rel', 'appos_rel', '_the_q_rel', '_udef_q_rel',
                 '_and_c_rel', 'unknown_rel', '_or_c_rel', '_in_p_rel',
                 '_object_n_1_rel', 'udef_q_rel', ]

def ace_rels(parse_output, flatten=False):
    """ Returns RELS from ACE parse output. """
    ##print parse_output
    rels = re.findall(r'RELS: \<(.*?)\> HCONS', parse_output)[0]
    lemmas = [l.rpartition('[')[2].strip() for 
              l in re.findall(r' \[ (.*?) LBL', rels)]
    idx_lemma = defaultdict(list) 
    for l in lemmas:
        idx = '<'+l.split('<')[1]
        idx = idx[1:-1].split(":")
        lemma = l.split('<')[0]
        lemma = lemma[1:] if lemma.startswith('"') else lemma
        lemma = lemma[:-1] if lemma.endswith('"') else lemma
        idx = map(int, idx)
        idx_lemma[idx[0], idx[1]].append(lemma)
    for i in sorted(idx_lemma):
        if not isinstance(idx_lemma[i], list):
            i = map(int, i)
            idx_lemma[i] = list(idx_lemma[i])
    if flatten:
        flat_rels = []
        for rel in idx_lemma.values():
            if not isinstance(rel, str):
                flat_rels.append("|".join([rl for rl in rel if rl 
                                           not in unwanted_rels]))
            elif rel not in unwanted_rel:
                flat_rels.apennd("|".join(rel))
        flat_rels = [frl for frl in flat_rels if frl]
        #print flat_rels
        return flat_rels
    else:
        return idx_lemma

def ace_chunk(sentence, lexicon = erg_lexicon(), 
              onlylemma=False, debugging=False):
    best_parse_output = ace_parse(sentence)[1:][0]
    idx_lemma = ace_rels(best_parse_output)
    
    idx_chunk = defaultdict(set)
    for i in sorted(idx_lemma):
        lemma_chunks = ["_".join(l).lower() for l in list(chain(*[lexicon[j] \
                                                for j in idx_lemma[i]]))]
        if lemma_chunks:
            for lc in lemma_chunks:
                idx_chunk[i].add(lc)

    lemmas = []                
    for fromto, token in tokens_fromto(sentence):
        ergtoken = ""
        surfacetoken = remove_punct(token.lower())
        if fromto in idx_chunk:
            ergtoken = idx_chunk[fromto]
            if len(ergtoken) == 1:
                ergtoken = list(ergtoken)[0]
        else:
            ergtoken = surfacetoken
        
        if onlylemma and isinstance(ergtoken, set):
            ergtoken = surfacetoken if surfacetoken in ergtoken else ergtoken
        lemmas.append(ergtoken)
        if debugging:
            print fromto, surfacetoken, ergtoken
    
    if debugging:
        ##print ace_parse(sentence)
        print idx_chunk
    elif onlylemma:
        print lemmas
    else:
        return idx_chunk
    
def ace_lemmatize(sentence, debugging=False, onlylemma=True):
    return ace_chunk(sentence, debugging=debugging, onlylemma=onlylemma)
    

##############################################################################

install_ace()

#ace_chunk('the geese ate a ratatta with two bottles of wine.', debugging=True)
#ace_chunk('the geese ate a ratatta with two bottles of wine.', onlylemma=True)
#ace_chunk('the geese ate a ratatta with two bigger bottles of wine that are larger than life and the sentence went on and on.', debugging=True)
#ace_lemmatize('the geese ate a ratatta with two bigger bottles of wine that are larger than life and the sentence went on and on.')

##ace_lemmatize('John is facebooking Mary on the net.', onlylemma=True, debugging=True)

##############################################################################

def mrs_lesk(context_sentence, ambiguous_word, usepostag=True, nbest=False):
    """
    This is a novel function that uses deep parsing (Head-driven Phrase 
    Structure Grammar) to generate lexical vectors from Minimal Recursion 
    Semantics (MRS) structures.
    
    NOTE: 1. Currently only using the definition of the senses as signature !!!
          2. Also, if ACE don't parse the sentence, the sense will not be 
             represented in the inventory.
          3. Be patient, ACE might take some time to install and 
             parse the sentences.
          4. Falls back on simple_lesk() if no overlaps found in RELS.
    """
    
    # Ensure that ambiguous word is a lemma.
    ambiguous_word = lemmatize(ambiguous_word)
    
    # Get POS of ambiguous in the context sentence.
    if usepostag:
        pos = get_pos_of_ambiguous_word(context_sentence, ambiguous_word)
    
    # Getting the MRS signatures from synset definition.
    ss_sign = {}
    for ss in wn.synsets(ambiguous_word):
        # Skips if the synset POS is not the pos_tag() POS.
        if usepostag:
            try: sspos = ss.pos()
            except: sspos = ss.pos
            if sspos != pos:
                continue
        # Get the definition for this synset.
        try: definition = ss.definition() + '.'
        except: definition = ss.definition + '.'
        definition = "".join([ch for ch in definition if ch \
                              not in ["(", ")", ";"]])
        
        try:
            parse_output = ace_parse(definition, bestparse=True)
            signature = ace_rels(parse_output, flatten=True)
            #print parse_output
            print definition
            print signature
            ss_sign[ss] = signature
        except: # ace parser don't like the sentence.
            pass
    
    # Disambiguating the sense from the context sentence.
    context_sentence = context_sentences if context_sentence.endswith('.') else\
                        context_sentence+"."
    context_sent_signature = ace_rels(ace_parse(context_sentence, 
                                                bestparse=True), flatten=True)
    best_sense = compare_overlaps(context_sent_signature, ss_sign, 
                                  nbest=True, keepscore=True)[0]
    
    if best_sense[0] == 0:
        print "falling back on simple_lesk()"
        return simple_lesk(context_sentence, ambiguous_word)
    else:
        return best_sense[1]

##############################################################################


from nltk.corpus import wordnet as wn
from lesk import lemmatize, get_pos_of_ambiguous_word, \
compare_overlaps, simple_lesk


bank_sents = ['I went to the bank to deposit my money',
'The river bank was full of dead fishes']

plant_sents = ['The workers at the industrial plant were overworked',
'The plant was no longer bearing flowers']

print "======== TESTING mrs_lesk() ===========\n"
print "#TESTING mrs_lesk() ..."
print "Context:", bank_sents[0]
print
answer = mrs_lesk(bank_sents[0],'bank')
print
print "Sense:", answer
try: definition = answer.definition() 
except: definition = answer.definition # Using older version of NLTK.
print "Definition:", definition
print
print "Simple Lesk", simple_lesk(bank_sents[0],'bank')
print
print "======== TESTING mrs_lesk() ===========\n"
print "#TESTING mrs_lesk() ..."
print "Context:", bank_sents[1]
print
answer = mrs_lesk(bank_sents[1],'bank')
print
print "Sense:", answer
try: definition = answer.definition() 
except: definition = answer.definition # Using older version of NLTK.
print "Definition:", definition
print
print "Simple Lesk", simple_lesk(bank_sents[1],'bank')
print
print "======== TESTING mrs_lesk() ===========\n"
print "Context:", plant_sents[0]
print
answer = mrs_lesk(plant_sents[0],'plant')
print
print "Sense:", answer
try: definition = answer.definition() 
except: definition = answer.definition # Using older version of NLTK.
print "Definition:", definition
print
print "Simple Lesk", simple_lesk(plant_sents[0],'plant')
print
print "======== TESTING mrs_lesk() ===========\n"
print "Context:", plant_sents[1]
print
answer = mrs_lesk(plant_sents[1],'plant')
print
print "Sense:", answer
try: definition = answer.definition() 
except: definition = answer.definition # Using older version of NLTK.
print "Definition:", definition
print
print "Simple Lesk", simple_lesk(plant_sents[1],'plant')
