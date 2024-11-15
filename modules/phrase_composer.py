from math import inf
from typing import Iterable
from modules.word_parser import getWords

def saveList(wordList:Iterable[str],filePath:str):
   with open(filePath,'w') as r:
      r.write('\n'.join(wordList))
   return True

def mainProcess(filePath='', start='',entries=20,limit=inf,noSpace=False,num=False,ending='.',mode=0):
   firstUp = lambda w: f'{w[0].upper()}{w[1:]}'
   
   variations:list[function] = []
   
   def var1():
      w=getWords(limit,'adverb',start)
      finito = f"{w.adverb.export()}, {' '.join([w.noun1.export(w.adjective.export()),w.verb.export(),w.noun2.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   def var2():
      w=getWords(limit,'noun1',start)
      finito = f"{' '.join([w.noun1.export(w.adjective.export()),w.verb.export(),w.noun2.export(),w.adverb.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)
   
   def var3():
      w=getWords(limit,'noun1',start)
      finito = f"{' '.join([w.noun1.export(),w.verb.export(),w.adjective.export(),w.noun2.export(),w.adverb.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   def var4():
      w=getWords(limit,'noun1',start)
      finito = f"{' '.join([w.noun1.export(),w.adverb.export(),w.verb.export(),w.noun2.export(w.adjective.export())]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)
   
   variations.append(var1)
   variations.append(var2)
   variations.append(var3)
   variations.append(var4)
   

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
         passes.append(var1())
         print(passes[-1])
      except:
         pass

   print("\n")
    # passList = [compose(start,limit,noSpace,num,ending,mode) for _ in range(entries)]
    # (saveList(passList,filePath) and print(f"Saved phrases to {filePath}")) if filePath != '' else print('\n'.join(passList))
