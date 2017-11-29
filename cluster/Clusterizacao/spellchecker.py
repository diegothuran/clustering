# Nick Sweeting 2014
# python spellchecker
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import collections
from itertools import product, imap
class Spellchecker():
    def __init__(self):
        self.VERBOSE = True
        self.vowels = set('aeiouy')
        self.alphabet = set('abcdefghijklmnopqrstuvwxyz')

    ### IO

    def log(self,*args):
        if self.VERBOSE: print ''.join([ str(x) for x in args])

    def words(self,text):
        """filter body of text for words"""
        return re.findall('[a-z]+', text.lower())

    def train(self,text, model=None):
        """generate or update a word model (dictionary of word:frequency)"""
        model = collections.defaultdict(lambda: 0) if model is None else model
        for word in self.words(text):
            model[word] += 1
        return model

    def train_from_files(self,file_list, model=None):
        for f in file_list:
            model = self.train(file(f).read(), model)
        return model

    ### UTILITY FUNCTIONS

    def numberofdupes(self,string, idx):
        """return the number of times in a row the letter at index idx is duplicated"""
        # "abccdefgh", 2  returns 1
        initial_idx = idx
        last = string[idx]
        while idx+1 < len(string) and string[idx+1] == last:
            idx += 1
        return idx-initial_idx

    def hamming_distance(self,word1, word2):
        if word1 == word2:
            return 0
        dist = sum(imap(str.__ne__, word1[:len(word2)], word2[:len(word1)]))
        dist = max([word2, word1]) if not dist else dist+abs(len(word2)-len(word1))
        return dist

    def frequency(self,word, word_model):
        return word_model.get(word, 0)

    ### POSSIBILITIES ANALYSIS

    def variants(self,word):
        """get all possible variants for a word"""
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        replaces = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
        inserts = [a + c + b for a, b in splits for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)

    def double_variants(self,word):
        """get variants for the variants for a word"""
        return set(s for w in self.variants(word) for s in self.variants(w))

    def reductions(self,word):
        """return flat option list of all possible variations of the word by removing duplicate letters"""
        word = list(word)
        # ['h','i', 'i', 'i'] becomes ['h', ['i', 'ii', 'iii']]
        for idx, l in enumerate(word):
            n = self.numberofdupes(word, idx)
            # if letter appears more than once in a row
            if n:
                # generate a flat list of options ('hhh' becomes ['h','hh','hhh'])
                flat_dupes = [l*(r+1) for r in xrange(n+1)][:3]
                for _ in range(n):
                    word.pop(idx+1)
                # replace original letter with flat list
                word[idx] = flat_dupes

        # ['h',['i','ii','iii']] becomes 'hi','hii','hiii'
        for p in product(*word):
            yield ''.join(p)

    def vowelswaps(self,word):
        """return flat option list of all possible variations of the word by swapping vowels"""
        word = list(word)
        # ['h','i'] becomes ['h', ['a', 'e', 'i', 'o', 'u', 'y']]
        for idx, l in enumerate(word):
            if type(l) == list:
                pass                        # dont mess with the reductions
            elif l in self.vowels:
                word[idx] = list(self.vowels)    # if l is a vowel, replace with all possible vowels

        # ['h',['i','ii','iii']] becomes 'hi','hii','hiii'
        for p in product(*word):
            yield ''.join(p)

    def both(self,word):
        """permute all combinations of reductions and vowelswaps"""
        for reduction in self.reductions(word):
            for variant in self.vowelswaps(reduction):
                yield variant

    ### POSSIBILITY CHOOSING

    def suggestions(self,word, real_words, short_circuit=True):
        """get best spelling suggestion for word
        return on first match if short_circuit is true, otherwise collect all possible suggestions"""
        word = word.lower()
        if short_circuit:   # setting short_circuit makes the spellchecker much faster, but less accurate in some cases
            return ({word} & real_words or   #  caps     "inSIDE" => "inside"
                    set(self.reductions(word)) & real_words or   #  repeats  "jjoobbb" => "job"
                    set(self.vowelswaps(word)) & real_words or   #  vowels   "weke" => "wake"
                    set(self.variants(word)) & real_words or   #  other    "nonster" => "monster"
                    set(self.both(word)) & real_words or   #  both     "CUNsperrICY" => "conspiracy"
                    set(self.double_variants(word)) & real_words or   #  other    "nmnster" => "manster"
                    {"NO SUGGESTION"})
        else:
            return ({word} & real_words or
                    (set(self.reductions(word)) | set(self.vowelswaps(word)) | set(self.variants(word)) | set(self.both(word)) | set(self.double_variants(word))) & real_words or
                    {"NO SUGGESTION"})

    def best(self,inputted_word, suggestions, word_model=None):
        """choose the best suggestion in a list based on lowest hamming distance from original word, or based on frequency if word_model is provided"""

        suggestions = list(suggestions)

        def comparehamm(one, two):
            score1 = self.hamming_distance(inputted_word, one)
            score2 = self.hamming_distance(inputted_word, two)
            return cmp(score1, score2)  # lower is better

        def comparefreq(one, two):
            score1 = self.frequency(one, word_model)
            score2 = self.frequency(two, word_model)
            return cmp(score2, score1)  # higher is better

        freq_sorted = sorted(suggestions, cmp=comparefreq)[10:]     # take the top 10
        hamming_sorted = sorted(suggestions, cmp=comparehamm)[10:]  # take the top 10
        print 'FREQ', freq_sorted
        print 'HAM', hamming_sorted
        return ''
    def correct(self,word):
        # init the word frequency model with a simple list of all possible words
        word_model = self.train(file('cluster/Clusterizacao/brazilian').read())
        real_words = set(word_model)
        # add other texts here, they are used to train the word frequency model
        texts = [
            'cluster/Clusterizacao/tese.txt',
            'cluster/Clusterizacao/sherlockholmes.txt',
            'cluster/Clusterizacao/lemmas.txt',
        ]
        # enhance the model with real bodies of english so we know which words are more common than others
        word_model = self.train_from_files(texts, word_model)

        try:
            while True:
                #possibilities = self.suggestions(word, real_words, short_circuit=False)
                short_circuit_result = self.suggestions(word, real_words, short_circuit=True)

                teste = [(x, word_model[x]) for x in short_circuit_result]

                return teste[0][0]

        except (EOFError, KeyboardInterrupt):
            exit(0)