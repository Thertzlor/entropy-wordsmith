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
      if item[0] in modStore:modStore[item[0]].append(item[1])
      else:modStore[item[0]] = [item[1]]
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
   def __init__(self, type:str,index=None) -> None:
      self.type = type
      (raw,index) = wordAndIndex(words[type])
      self.raw = raw
      self.index = index
      self.empty = raw == ''
      self.variants = self.raw in variations[type] and variations[type][self.raw] or tuple()
      self.multi = " " in self.raw
      self.hyphen = "-" in self.raw
      self.compound = " in " in self.raw or " at " in self.raw or " of " in self.raw or " after " in self.raw or " from " in self.raw or " and " in self.raw
      self.possessive = "'s" in self.raw
      self.withArticle = " the " in self.raw or "the " in self.raw
      self.split = self.raw.split(" ")


   def export(self):
      return self.raw
   def output(self):
      return { 
         "index": self.index, 
         "raw":self.raw,
         "variants" : self.variants,
         "multi": self.multi,
         "hyphen":self.hyphen,
         "compound":self.compound,
         "possessive":self.possessive,
         }

class Noun(Word):
   def __init__(self) -> None:
      super().__init__('noun')
      self.pluralized = False
      self.articled = False
      self.singular = self.raw
      singularticles = tuple()
      pluralticles = tuple()
      if not self.withArticle:
         singularticles = (self.raw[0].upper() in ('A','U','O','I') and 'an' or 'a', 'the')
         pluralticles = tuple(['the'])
      self.singularticles = singularticles
      self.pluralticles = pluralticles
      pluraltarget = len(self.split)-1
      if self.compound: pluraltarget = 0
      self.pluralTarget =  pluraltarget
      plural = len(self.variants)!=0 and self.variants[len(self.variants)-1] or ''
      if plural == '':
         target = not self.multi and self.raw or self.split[self.pluralTarget]
         target =  (target.endswith('y') and target[-2:] not in ('ay','ey')) and f'{target[:-1]}ies' or target.endswith('us') and f'{target[:-2]}a' or (target.endswith('z') or target[-2:] in ('ss','is','sh','ch')) and f'{target}es' or target.endswith('s') and target or f'{target}s'
         if not self.multi:
            plural = target
         else:
            plural = " ".join(i != self.pluralTarget and x or target for [i,x] in enumerate(self.split))
      self.plural = plural

   def output(self):
      oldput = super().output()
      merged = dict()
      merged.update(oldput)
      newObj = {
         "pluralized" : self.pluralized,
         "singular":self.singular,
         "artSing": self.singularticles,
         "artPLur":self.pluralticles,
         "plurtarget":self.split[self.pluralTarget],
         "plural":self.plural
      }
      merged.update(newObj)
      return merged

class Adjective(Word):
   pass

class Verb(Word):
   def __init__(self) -> None:
      super().__init__('verb')
      self.varied = False
      if(not self.variants):
         tenseTarget = self.multi and self.split[0] or self.raw
         pastTense =  (tenseTarget.endswith('m') and tenseTarget[-2:-1] in ('a','e','i','o','u'))  and f'{tenseTarget[:-2]}med' or  tenseTarget.endswith('eed') and f'{tenseTarget[:-2]}d' or tenseTarget.endswith('e') and f'{tenseTarget}d' or f'{tenseTarget}ed'
         tensed = pastTense
         if self.multi: tensed = " ".join(i != 0 and x or pastTense for [i,x] in enumerate(self.split))
         partic = tenseTarget.endswith('e') and f'{tenseTarget[:-1]}ing' or f'{tenseTarget}ing'
         particied = partic
         if self.multi: particied = " ".join(i != 0 and x or partic for [i,x] in enumerate(self.split))
         self.variants = [tensed,particied]


   def output(self):
      oldput = super().output()
      merged = dict()
      merged.update(oldput)
      newObj = {
         "varied":self.varied,
      }
      merged.update(newObj)
      return merged

class Adverb(Word):
   pass


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
   for _ in range(10):
      dolly = Verb()
      # while len(dolly.variants) == 0:
      #    dolly=Noun()
      print(dolly.output())
      print("")
   pass
   # passList = [compose(start,limit,noSpace,num,ending,mode) for _ in range(entries)]
   # (saveList(passList,filePath) and print(f"Saved phrases to {filePath}")) if filePath != '' else print('\n'.join(passList))