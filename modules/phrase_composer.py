from math import inf
from typing import Iterable
from modules.word_parser import getWords
from modules.utilities import listEntry

def saveList(wordList:Iterable[str],filePath:str):
   with open(filePath,'w') as r:
      r.write('\n'.join(wordList))
   return True

def mainProcess(filePath='', start='',entries=10,limit=inf,noSpace=False,num=0,ending='.',mode=0):
   firstUp = lambda w: f'{w[0].upper()}{w[1:]}'
   variations:list[function] = []
   
   def var1():
      w=getWords(limit,'adverb',start,num)
      finito = f"{w.adverb.export()}, {' '.join([w.noun1.export(w.adjective.export()),w.verb.export(),w.noun2.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   def var2():
      w=getWords(limit,'noun1',start,num)
      finito = f"{' '.join([w.noun1.export(w.adjective.export()),w.verb.export(),w.noun2.export(),w.adverb.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)
   
   def var3():
      w=getWords(limit,'noun1',start,num)
      finito = f"{' '.join([w.noun1.export(),w.verb.export(),w.adjective.export(),w.noun2.export(),w.adverb.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   def var4():
      w=getWords(limit,'noun1',start,num)
      finito = f"{' '.join([w.noun1.export(),w.adverb.export(),w.verb.export(),w.noun2.export(w.adjective.export())]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)
   def var5():
      w=getWords(limit,'adjective',start,num)
      finito = f"{w.adjective.export()}: {' '.join([w.noun1.export(),w.adverb.export(),w.verb.export(),w.noun2.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)
   
   variations.append(var1)
   variations.append(var2)
   variations.append(var3)
   variations.append(var4)
   variations.append(var5)
   

    # if True:
    #    dolly = Noun(None,"child")
    #    while not dolly._variants: dolly=Noun(None,"child")
    #    dolly.present=True
    #    dolly.pluralized = True
    #    print(dolly.export())
    #    print(dolly.output())

   passes: list[str] = []

   while len(passes) < entries:
      try:
         word = (listEntry(variations) if mode == 0 else variations[mode-1])()
         if(len(word)<=limit):
            passes.append(word)
            print(passes[-1])
      except:
         pass

   print("\n")
    # passList = [compose(start,limit,noSpace,num,ending,mode) for _ in range(entries)]
    # (saveList(passList,filePath) and print(f"Saved phrases to {filePath}")) if filePath != '' else print('\n'.join(passList))
