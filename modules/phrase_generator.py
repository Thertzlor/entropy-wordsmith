from secrets import randbelow
from math import inf
from typing import Iterable, Tuple
import re

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

listEntry = lambda l: '' if len(l) == 0 else l[randbelow(len(l))]
firstUp = lambda w: f'{w[0].upper()}{w[1:]}'

def wordAndIndex(l) -> Tuple[str,int]:
   if len(l) == 0:return ('',0)
   num = randbelow(len(l))
   return (l[num],num)

class Word:
   def __init__(self, kind:str,initiate:str|int|None=None,start:str|None=None) -> None:
      self._type = kind
      raw = ''
      index = -1
      if initiate is not None and type(initiate) is str: raw = initiate
      elif initiate is not None: 
         index = initiate 
         raw = words[kind][index]
      else: (raw,index) = wordAndIndex(not start and words[kind] or (w for w in words[kind] if w.startswith(start.lower())))
      self._raw = raw
      self._varied = False
      self._index = index
      self._empty = raw == ''
      self._variants = self._raw in variations[kind] and variations[kind][self._raw] or tuple()
      self._multi = " " in self._raw
      self._hyphen = "-" in self._raw
      self._compound = next((True for x in ("in","at","after","from","of","and","a","it") if (re.match(f'\b{x}\b',self._raw))),None)
      self._possessive = "'s" in self._raw
      self._withArticle = " the " in self._raw or "the " in self._raw
      self._split = tuple(self._raw.split(" "))

   def export(self): return (self._varied and self._variants) and listEntry(self._variants) or self._raw

   def output(self): return { 
      "index": self._index, 
      "raw":self._raw,
      "variants" : self._variants,
      "multi": self._multi,
      "hyphen":self._hyphen,
      "compound":self._compound,
      "possessive":self._possessive,
      "varied":self._varied,
   }

class Noun(Word):
   def __init__(self,initiate=None,start=None) -> None:
      super().__init__('noun',initiate,start)
      self.pluralized = False
      self.articled = False
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

   def getArticle(self,before:str=''):
      if self._withArticle:return ''
      if self.pluralized: return listEntry(('the','some','many'))
      else: return listEntry(((before or self._raw[0]).upper() in ('A','U','O','I') and 'an' or 'a', 'the'))

   def export(self,adj:str=''):
      core = self.pluralized and self._plural or self._singular
      if (not self.articled) or not self.getArticle(): return adj and f"{adj} {core}" or core
      return f'{self.getArticle(adj)}{adj and f" {adj} " or " "}{core}'

   def output(self):
      oldput = super().output()
      merged = dict()
      merged.update(oldput)
      newObj = {
         "pluralized" : self.pluralized,
         "singular":self._singular,
         "plurtarget":self._split[self._pluralTarget],
         "plural":self._plural
      }
      merged.update(newObj)
      return merged

class Adjective(Word):
   def __init__(self, initiate: str | int | None = None,start=None) -> None:
      super().__init__('adj', initiate,start)
      self.comparable = bool(self._variants)
      self._comparative = self.comparable and self._variants[0] or None
      self._superlative = self.comparable and self._variants[1] or None
   
   def output(self):
      oldput = super().output()
      merged = dict()
      merged.update(oldput)
      newObj = {
         "comparable" : self.comparable,
         "comparative": self._comparative,
         "superlative":self._superlative
      }
      merged.update(newObj)
      return merged

class Verb(Word):
   def __init__(self,init=None,start=None) -> None:
      super().__init__('verb',init,start)
      if(not self._variants):
         if self._multi: self._variants = tuple(" ".join((x," ".join(self._split[1:]))) for x in Verb(self._split[0])._variants)
         else:
            pastTense = self._raw.endswith('e') and f'{self._raw[:-1]}ed' or f'{self._raw}ed'
            partic = self._raw.endswith('e') and f'{self._raw[:-1]}ing' or f'{self._raw}ing'
            self._variants = (pastTense,partic)
      elif len(self._variants) == 1:
         partic = self._raw.endswith('e') and f'{self._raw[:-1]}ing' or f'{self._raw}ing'
         self._variants = (self._variants[0],partic)
      self._variants = self._variants + tuple([f'{self._raw}s'])
      self.pastTense = False
      self.continuous = False
      self.present = False


   def output(self):
      oldput = super().output()
      merged = dict()
      merged.update(oldput)
      newObj = {"varied":self._varied}
      merged.update(newObj)
      return merged
   
   def export(self):
      return not self._variants and self._raw or self.pastTense and self._variants[0] or self.continuous and self._variants[1] or self.present and self._variants[2] or self._raw

class Adverb(Word):
   def __init__(self, initiate: str | int | None = None,start=None) -> None:
      super().__init__('adv', initiate,start)


def entryForWord(type,limit=inf,starting=''):return listEntry([w for w in words[type]if w.startswith(starting) and len(w)<limit and (type not in ['noun','adv'] or len(w) > 2)]) 

def vary(word:str,wordType):
   if word == '':return ''
   wordSplit = word.split(' ')
   firstWord = wordSplit[0] if (wordType != "noun" or " of " in word) else word
   default={
      'noun':lambda w: f'{w[:-1]}ies' if w.endswith('y') else  f'{w[-2]}a' if w.endswith('ium') else f'{w[:-1]}ces' if w.endswith('x') else w if w.endswith('s') else f"{w}es" if (w.endswith('z') or w.endswith('ch')) else  f'{w}s',
      'verb':lambda w: [re.sub(r"e$","ed",w),re.sub(r"i?e?$","ing",w)] 
   }
   defVal = default[wordType](firstWord)
   variation = (defVal if type(defVal) is str else listEntry(defVal)) if word not in variations[wordType] else listEntry(variations[wordType][word])
   return variation

def unvaryVerb(v:str):
   if v == '':return v
   wordSplit = v.split(' ')
   firstWord = wordSplit[0]
   changed= f'{firstWord[:-1]}ies' if firstWord.endswith('y') else f'{firstWord}es' if firstWord[-1] in ['h'] else re.sub("s?$","s",firstWord)
   return f'{changed} {" ".join(wordSplit[1:])}'

def compose(starting='',maxLength=inf,noSpace=False,num=False,ending='.',mode=0):
   p1= randbelow(2) == 1
   p2= randbelow(2) == 0
   if num and (not p1) and (not p2):
      rePlural = randbelow(2)
      if rePlural == 1: p1 = True
      else: p2 = True
   numerized = False

   def article(noun,plural):
      if randbelow(2) == 1: return noun
      if not plural: return f'{randbelow(2) == 1 and "the" or ((noun)[0].capitalize() in ["O","A","U","I"] and "an" or "a")} {noun}'
      return f'{(randbelow(4) == 1) and "some" or "the"} {noun}'

   def numerize(noun,plural):
      nonlocal numerized
      if (not num) or (numerized or not plural):return article(noun,plural)
      numerized= True
      useNum = num if type(num) is int else max(2,randbelow(10))
      return f'{useNum} {noun}'
   limit = (maxLength-4-(minLength['noun']*2)-minLength['verb']-minLength['adv']-len(ending))+1
   if num: limit = limit-(len(str(num))+1)

   def var1():
      nonlocal limit
      adj = entryForWord('adj',limit,starting)
      adj = numerize(adj,p1)
      limit = limit + minLength['adj'] - len(adj) +1
      noun1 = entryForWord('noun',limit) if not p1 else vary(entryForWord('noun',limit),'noun')
      limit = limit + minLength['noun'] - len(noun1) +1
      verb = unvaryVerb(entryForWord('verb',limit)) if not p1 else vary(entryForWord('verb',limit),'verb')
      limit = limit + minLength['verb'] - len(verb)
      noun2 = entryForWord('noun',limit) if p2 else vary(entryForWord('noun',limit),'noun')
      noun2 = numerize(noun2,p2)
      limit = limit + minLength['noun'] - len(noun2)
      adv = entryForWord('adv',limit)
      finito = f"{' '.join([adj,noun1,verb,noun2,adv]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   def var2():
      nonlocal limit
      limit=limit-1
      adv = entryForWord('adv',limit,starting)
      limit = limit + minLength['adv'] - len(adv) +1
      adj = entryForWord('adj',limit)
      adj = numerize(adj,p1)
      limit = limit + minLength['adj'] - len(adj) +1
      noun1 = entryForWord('noun',limit) if not p1 else vary(entryForWord('noun',limit),'noun')
      limit = limit + minLength['noun'] - len(noun1) +1
      verb = unvaryVerb(entryForWord('verb',limit)) if not p1 else vary(entryForWord('verb',limit),'verb')
      limit = limit + minLength['verb'] - len(verb)
      noun2 = entryForWord('noun',limit) if p2 else vary(entryForWord('noun',limit),'noun')
      noun2 = numerize(noun2,p2)
      limit = limit + minLength['noun'] - len(noun2)
      finito = f"{adv}, {' '.join([adj,noun1,verb,noun2]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   def var3():
      nonlocal limit
      noun1 = entryForWord('noun',limit,starting) if not p1 else vary(entryForWord('noun',limit,starting),'noun')
      noun1 = numerize(noun1,p1)
      limit = limit + minLength['noun'] - len(noun1) +1
      verb = unvaryVerb(entryForWord('verb',limit)) if not p1 else vary(entryForWord('verb',limit),'verb')
      limit = limit + minLength['verb'] - len(verb)
      adj = entryForWord('adj',limit)
      adj = numerize(adj,p2)
      limit = limit + minLength['adj'] - len(adj) +1
      noun2 = entryForWord('noun',limit) if p2 else vary(entryForWord('noun',limit),'noun')
      limit = limit + minLength['noun'] - len(noun2)
      adv = entryForWord('adv',limit)
      finito = f"{' '.join([noun1,verb,adj,noun2,adv]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   def var4():
      nonlocal limit
      noun1 = entryForWord('noun',limit,starting) if not p1 else vary(entryForWord('noun',limit,starting),'noun')
      noun1 = numerize(noun1,p1)
      limit = limit + minLength['noun'] - len(noun1) +1
      adv = entryForWord('adv',limit)
      limit = limit + minLength['adv'] - len(adv) +1
      verb = unvaryVerb(entryForWord('verb',limit)) if not p1 else vary(entryForWord('verb',limit),'verb')
      limit = limit + minLength['verb'] - len(verb)
      adj = entryForWord('adj',limit)
      adj = numerize(adj,p2)
      limit = limit + minLength['adj'] - len(adj) +1
      noun2 = entryForWord('noun',limit) if p2 else vary(entryForWord('noun',limit),'noun')
      finito = f"{' '.join([noun1,adv,verb,adj,noun2]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)
   
   def var5():
      nonlocal limit
      limit = limit-1
      adj = entryForWord('adj',limit,starting)
      limit = limit + minLength['adj'] - len(adj) +1
      noun1 = entryForWord('noun',limit) if not p1 else vary(entryForWord('noun',limit),'noun')
      noun1 = numerize(noun1,p1)
      limit = limit + minLength['noun'] - len(noun1) +1
      adv = entryForWord('adv',limit)
      limit = limit + minLength['adv'] - len(adv) +1
      verb = unvaryVerb(entryForWord('verb',limit)) if not p1 else vary(entryForWord('verb',limit),'verb')
      limit = limit + minLength['verb'] - len(verb)
      noun2 = entryForWord('noun',limit) if p2 else vary(entryForWord('noun',limit),'noun')
      noun2 = numerize(noun2,p2)
      finito = f"{adj}: {' '.join([noun1,adv,verb,noun2]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   variations = [var1,var2,var3,var4,var5]
   select = listEntry(variations) if mode == 0 else variations[mode-1]
   return '' if select == '' else select().replace(' ','_') if noSpace else select()

def saveList(wordList:Iterable[str],filePath:str):
   with open(filePath,'w') as r:
      r.write('\n'.join(wordList))
   return True

def mainProcess(filePath='', start='',entries=20,limit=inf,noSpace=False,num=False,ending='.',mode=0):
   print("")
   print("")
   def newVar1():
      adv=Adverb()
      adj=Adjective()
      noun1=Noun()
      if randbelow(2) ==1:noun1.articled = True
      if randbelow(2) ==1:noun1.pluralized = True
      verb=Verb()
      if not noun1.pluralized: 
         if randbelow(2) == 1: verb.pastTense = True 
         else: verb.present =True
      noun2=Noun()
      if randbelow(2)==1:noun2.articled = True
      if randbelow(2)==1:noun2.pluralized = True
      finito = f"{adv.export()}, {' '.join([noun1.export(adj.export()),verb.export(),noun2.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)
   for _ in range(10):
      if False:
         dolly = Verb()
         while not dolly._variants: dolly=Verb()
         dolly.present=True
         print(dolly.export())
         print(dolly.output())
      else: print(newVar1())
      print("")
   pass
   # passList = [compose(start,limit,noSpace,num,ending,mode) for _ in range(entries)]
   # (saveList(passList,filePath) and print(f"Saved phrases to {filePath}")) if filePath != '' else print('\n'.join(passList))