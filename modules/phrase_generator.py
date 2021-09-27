from secrets import randbelow
from math import inf
from typing import Iterable
import re

def getList(path):
   with open(path,'r') as resRaw:
     res = [m.replace('_',' ').strip() for m in resRaw.readlines() if not m.startswith('  ')]
     res.sort(key=len);
   return res

def getMods(path):
   with open(path,'r') as resRaw:
     res = [[w.replace('_',' ').strip() for w in reversed(m.split(' '))] for m in resRaw.readlines() if not m.startswith('  ')]
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

def entryForWord(type,limit=inf,starting=''):return listEntry([w for w in words[type]if w.startswith(starting) and len(w)<limit and (type not in ['noun','adv'] or len(w) > 2)]) 

def vary(word,wordType):
   if word == '':return ''
   default={
      'noun':lambda w: f'{w[:-1]}ies' if w.endswith('y') else  f'{w[-2]}a' if w.endswith('ium') else f'{w[:-1]}ces' if w.endswith('x') else w if w.endswith('s') else  f'{w}s',
      'verb':lambda w: [re.sub(r"e?d?$","ed",w),re.sub(r"i?e?$","ing",w)] 
   }
   defVal = default[wordType](word)
   variation = (defVal if type(defVal) is str else listEntry(defVal)) if word not in variations[wordType] else listEntry(variations[wordType][word])
   return variation

def unvaryVerb(v:str):
   if v == '':return v
   splat = v.split(' ')
   splot = splat[0]
   changed= f'{splot[:-1]}ies' if splot.endswith('y') else f'{splot}es' if splot[-1] in ['h'] else re.sub("s?$","s",splot)
   return f'{changed} {" ".join(splat[1:])}'

def compose(starting='',maxLength=inf,noSpace=False,num=False,ending='.',mode=0):
   p1= randbelow(2) == 1
   p2= randbelow(2) == 0
   if num and (not p1) and (not p2):
      rePlural = randbelow(2)
      if rePlural == 1: p1 = True
      else: p2 = True
   numerized = False

   def numerize(noun,plural):
      nonlocal numerized
      if (not num) or (numerized or not plural):return noun
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
   passList = [compose(start,limit,noSpace,num,ending,mode) for _ in range(entries)]
   (saveList(passList,filePath) and print(f"Saved phrases to {filePath}")) if filePath != '' else print('\n'.join(passList))