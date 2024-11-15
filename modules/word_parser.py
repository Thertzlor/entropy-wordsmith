from math import inf
from secrets import randbelow
from typing import Literal, NamedTuple
import re

from modules.utilities import wordAndIndex, listEntry,maybe

def getList(path):
   with open(path,'r') as resRaw:
     res = [m.replace('_',' ').strip() for m in resRaw.readlines() if not m.startswith('  ')]
     res.sort(key=len);
   return tuple(res)

def getMods(path):
   with open(path,'r') as resRaw:
     res = (tuple([w.replace('_',' ').strip() for w in reversed(m.split(' '))]) for m in resRaw.readlines() if not m.startswith('  '))
   modStore = {}
   def setter(item):
      if item[0] in modStore:modStore[item[0]] = modStore[item[0]] + tuple([item[1]])
      else:modStore[item[0]] = tuple([item[1]])
   [setter(r) for r in res]
   return modStore

words={
   'adj' : getList('./dict/index_adj.txt'),
   'adv' : getList('./dict/index_adv.txt'),
   'noun' : getList('./dict/index_noun.txt'),
   'verb' : getList('./dict/index_verb.txt')
}

variations={
   'adj' :  getMods('./dict/exc_adj.txt'),
   'adv' : getMods('./dict/exc_adv.txt'),
   'noun' : getMods('./dict/exc_noun.txt'),
   'verb' : getMods('./dict/exc_verb.txt')
}

minLength={
   'noun':3,
   'adv':3,
   'adj':len(words['adj'][0]),
   'verb':len(words['verb'][0]),
}
def prepareWords():
  characters_used = 0
  words_generated = 0
  char_limit = 0

  class Word:
      def __init__(self, kind:str,initiate:str|int|None=None,start:str|None=None,add_chars=1, max_expand=0) -> None:
        nonlocal char_limit,characters_used,words_generated
        maxLength = char_limit - characters_used - max_expand
        self._type = kind
        raw = ''
        index = -1
        self._space = add_chars
        if initiate is not None and type(initiate) is str: raw = initiate
        elif initiate is not None: 
            index = initiate 
            raw = words[kind][index]
        else:
            wuple = tuple(x for x in not start and words[kind] or tuple(w for w in words[kind] if w.startswith(start.lower())) if len(x) < maxLength and len(x) > minLength[kind])
            if(len(wuple)) == 0: raise Exception("Not enough fucking words.")
            (raw,index) = wordAndIndex(wuple)
        self._raw = raw
        self._index = index
        self._empty = raw == ''
        self._variants = self._raw in variations[kind] and variations[kind][self._raw] or tuple()
        self._fixed_variant = None
        self._multi = " " in self._raw
        self._hyphen = "-" in self._raw
        self._compound = next((True for x in ("in","at","after","from","of","and","a","it") if (re.match(f'\b{x}\b',self._raw))),None)
        self._possessive = "'s" in self._raw
        self._withArticle = " the " in self._raw or "the " in self._raw
        self._split = tuple(self._raw.split(" "))

      def export(self): 
        if not self._fixed_variant and self._variants:
            self._fixed_variant = randbelow(len(self._variants))      
        return self._raw if self._fixed_variant is None else self._variants[self._fixed_variant]
      
      def add(self): 
        nonlocal characters_used,words_generated
        words_generated +=1
        characters_used += (len(self.export()) + self._space)

      def output(self): return { 
        "index": self._index, 
        "raw":self._raw,
        "variants" : self._variants,
        "multi": self._multi,
        "hyphen":self._hyphen,
        "compound":self._compound,
        "possessive":self._possessive
      }


  class Noun(Word):
      def __init__(self,initiate=None,start=None,articled=False,pluralized=False,add_chars=1,prepend_number:int|None=None) -> None:
          super().__init__('noun',initiate,start,add_chars,max_expand=2)
          self._pluralized = pluralized
          self._articled = articled
          self._singular = self._raw
          pluraltarget = len(self._split)-1
          if self._compound: pluraltarget = 0
          self._pluralTarget =  pluraltarget
          plural = len(self._variants)!=0 and self._variants[len(self._variants)-1] or ''
          if plural == '':
            target = not self._multi and self._raw or self._split[self._pluralTarget]
            target =  (target.endswith('y') and target[-2:] not in ('ay','ey')) and f'{target[:-1]}ies' or target.endswith('us') and f'{target[:-2]}a' or (target.endswith('z') or target[-2:] in ('ss','is','sh','ch')) and f'{target}es' or target.endswith('s') and target or f'{target}s'
            if not self._multi:
                plural = target
            else:
                plural = " ".join(i != self._pluralTarget and x or target for [i,x] in enumerate(self._split))
          self._plural = plural
          self._num_string = "" if prepend_number is None else f"{prepend_number} "
          self.add()
        
      @property
      def pluralized(self):return self._pluralized
      @property
      def articled(self):return self._articled

      def _getArticle(self,before:str=''):
        if self._withArticle:return ''
        if self._pluralized: return listEntry(('the','some'))
        else: return listEntry(((before or self._raw[0]).upper() in ('A','U','O','I') and 'an' or 'a', 'the'))

      def export(self,adj:str=''):
        core = self._pluralized and self._plural or self._singular
        if (not self._articled) or not self._getArticle(): return adj and f"{self._num_string}{adj} {core}" or f"{self._num_string}{core}"
        return f'{self._getArticle(adj)} {self._num_string}{adj and f" {adj} " or " "}{core}'

      def output(self):
        oldput = super().output()
        merged = dict()
        merged.update(oldput)
        newObj = {
            "pluralized" : self._pluralized,
            "singular":self._singular,
            "plurtarget":self._split[self._pluralTarget],
            "plural":self._plural
        }
        merged.update(newObj)
        return merged


  class Adjective(Word):
      def __init__(self, initiate: str | int | None = None, start=None,mode:None|Literal["comparative","superlative"]=None,add_chars=1) -> None:
        super().__init__("adj", initiate, start,add_chars)
        self.comparable = bool(self._variants)
        self._comparative = self.comparable and self._variants[0] or None
        self._superlative = self.comparable and self._variants[1] or None
        self.add()

      def output(self):
        oldput = super().output()
        merged = dict()
        merged.update(oldput)
        newObj = {
            "comparable": self.comparable,
            "comparative": self._comparative,
            "superlative": self._superlative,
        }
        merged.update(newObj)
        return merged


  class Verb(Word):
      def __init__(self,init=None,start=None, tense:Literal["present","past"]|None=None,continuous = False,add_chars=1,) -> None:
        super().__init__('verb',init,start,add_chars,max_expand=3)
        if(not self._variants):
            if self._multi: self._variants = tuple(" ".join((x," ".join(self._split[1:]))) for x in Verb(self._split[0])._variants)
            else:
              pastTense = self._raw.endswith('e') and f'{self._raw[:-1]}ed' or f'{self._raw}ed'
              partic = self._raw.endswith('e') and f'{self._raw[:-1]}ing' or f'{self._raw}ing'
              self._variants = (pastTense,partic)
        elif len(self._variants) == 1:
            partic = self._raw.endswith('e') and f'{self._raw[:-1]}ing' or f'{self._raw}ing'
            self._variants = (self._variants[0],partic)
        self._variants = self._variants + tuple([f'{self._raw}es' if (self._raw.endswith('o') and not self._raw.endswith('oo')) else f'{self._raw}s'])
        self._pastTense = tense == "past"
        self._continuous = continuous
        self._present = tense == "present"
        self.add()
        
      @property
      def pastTense(self):return self._pastTense
      @property
      def presentTense(self):return self._present
      @property
      def continuous(self):return self._continuous

      def output(self):
        oldput = super().output()
        merged = dict()
        merged.update(oldput)
        newObj = {"varied":self._varied}
        merged.update(newObj)
        return merged
      
      def export(self):
        return not self._variants and self._raw or self._pastTense and self._variants[0] or self._continuous and self._variants[1] or self._present and self._variants[2] or self._raw


  class Adverb(Word):
      def __init__(self, initiate: str | int | None = None,start=None,add_chars=1,) -> None:
        super().__init__('adv', initiate,start,add_chars)
        self.add()
  
  def getWords(c_limit = inf,first_word:None|Literal['noun1','noun2','verb','adjective','adverb']=None,start:str|None=None, num = None):
    nonlocal char_limit,characters_used,words_generated
    char_limit = c_limit
    characters_used = 0
    words_generated = 0
  
    WordTuple = NamedTuple('WordTuple', [('noun1', Noun), ('noun2', Noun),('adverb',Adverb),('adjective',Adjective),('verb',Verb)])      
  
    plural1 = maybe()
    plural2 = maybe()
    
    numTarget = 0
    
    if num:
      if type(num) is bool:
        num = randbelow(8)+1
      if plural1: 
        numTarget = 1
      else:
        plural2 = True
        numTarget = 2

    noun1 = Noun(articled=maybe(), pluralized=plural1,start=start if first_word == "noun1" else None,prepend_number=num if numTarget == 1 else None)
    noun2 = Noun(articled=maybe(), pluralized=plural2, start=start if first_word == "noun2" else None,prepend_number=num if numTarget == 2 else None)
    verb = Verb(tense=(None if noun1.pluralized else "past" if maybe() else "present"),start=start if first_word == "verb" else None)
    adv = Adverb(start=start if first_word == "adverb" else None)
    adj = Adjective(start=start if first_word == "adjective" else None)
    return WordTuple(noun1,noun2,adv,adj,verb)
  
  return getWords