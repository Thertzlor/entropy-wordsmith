from math import inf
from typing import Iterable, Callable, Literal
from modules.word_parser import prepareWords
from modules.utilities import listEntry

def saveList(wordList:Iterable[str],filePath:str):
   with open(filePath,'w') as r: r.write('\n'.join(wordList))

def mainProcess(filePath='', start='',entries=10,limit=inf,noSpace=False,num=0,ending='.',mode=0,articles:Literal["random","always","never"]="random",compare:Literal["random","always","never"]="random"):
   getWords = prepareWords()
   firstUp = lambda w: f'{w[0].upper()}{w[1:]}'
   toFile = filePath != ''

   def var1():
      w=getWords(limit,'adverb',start,num,articles,compare)
      finito = f"{w.adverb.export()}, {' '.join([w.noun1.export(w.adjective.export()),w.verb.export(),w.noun2.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   def var2():
      w=getWords(limit,'adjective',start,num,articles,compare)
      finito = f"{' '.join([w.noun1.export(w.adjective.export()),w.verb.export(),w.noun2.export(),w.adverb.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)
   
   def var3():
      w=getWords(limit,'noun1',start,num,articles,compare)
      finito = f"{' '.join([w.noun1.export(),w.verb.export(),w.noun2.export(w.adjective.export()),w.adverb.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   def var4():
      w=getWords(limit,'noun1',start,num,articles,compare)
      finito = f"{' '.join([w.noun1.export(),w.adverb.export(),w.verb.export(),w.noun2.export(w.adjective.export())]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)

   def var5():
      w=getWords(limit,'adjective',start,num,articles,compare)
      finito = f"{w.adjective.export()}: {' '.join([w.noun1.export(),w.adverb.export(),w.verb.export(),w.noun2.export()]).strip().replace('  ',' ')}{ending}"
      return firstUp(finito)
   
   variations:list[Callable[[],str]] = []
   variations.append(var1)
   variations.append(var2)
   variations.append(var3)
   variations.append(var4)
   variations.append(var5)
   
   passes: list[str] = []
   failures = 0
   max_failures = 250
   while len(passes) < entries:
      try:
         word = (listEntry(variations) if mode == 0 else variations[mode-1])()
         if(len(word)<=limit):
            if noSpace: word = word.replace(" ","_")
            if not toFile:print(word)
            passes.append(word)
            failures = 0
      except:
         failures += 1
         if(failures > max_failures):
            print('ERROR: Could not consistently generate pass phrases of the desired length. Try raising the value of your "-l/--max_length" argument.')
            break

   if toFile: saveList(passes,filePath)
