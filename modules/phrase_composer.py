from math import inf
from typing import Iterable, Literal
from modules.word_parser import prepareWords
from modules.utilities import listEntry


def saveList(wordList: Iterable[str], filePath: str):
   with open(filePath, 'w') as r:
      r.write('\n'.join(wordList))


def mainProcess(filePath='', start='', entries=10, limit=inf, noSpace=False, num=0, ending='.', mode=0, articles: Literal["random", "always", "never"] = "random", compare: Literal["random", "always", "never"] = "random"):
   getWords, _ = prepareWords()
   firstUp = lambda w: f'{w[0].upper()}{w[1:]}'
   toFile = filePath != ''

   clean_text = lambda t: firstUp(t).replace(' ,', ',').replace('  ', ' ')

   def var1():
      (noun1, noun2, adverb, adjective, verb) = getWords(limit, 'adverb', start, num, articles, compare)
      finito = f"{adverb.export()}, {' '.join([noun1.export(adjective.export()),verb.export(noun2.export())]).strip()}{ending}"
      return clean_text(finito)

   def var2():
      (noun1, noun2, adverb, adjective, verb) = getWords(limit, 'adjective', start, num, articles, compare)
      finito = f"{' '.join([noun1.export(adjective.export()),verb.export(noun2.export()),adverb.export()]).strip()}{ending}"
      return clean_text(finito)

   def var3():
      (noun1, noun2, adverb, adjective, verb) = getWords(limit, 'noun1', start, num, articles, compare)
      finito = f"{' '.join([noun1.export(),verb.export(noun2.export(adjective.export())),adverb.export()]).strip()}{ending}"
      return clean_text(finito)

   def var4():
      (noun1, noun2, adverb, adjective, verb) = getWords(limit, 'noun1', start, num, articles, compare, True)
      finito = f"{' '.join([noun1.export(),adverb.export(),verb.export(noun2.export(adjective.export()))]).strip()}{ending}"
      return clean_text(finito)

   def var5():
      (noun1, noun2, adverb, adjective, verb) = getWords(limit, 'adjective', start, num, articles, compare, True)
      finito = f"{adjective.export()}: {' '.join([noun1.export(),adverb.export(),verb.export(noun2.export())]).strip()}{ending}"
      return clean_text(finito)

   variations = (var1, var2, var3, var4, var5)

   passes: list[str] = []
   failures = 0
   max_failures = 250
   while len(passes) < entries:
      try:
         word = (listEntry(variations) if mode == 0 else variations[mode - 1])()
         if (len(word) <= limit):
            if noSpace: word = word.replace(" ", "_")
            if not toFile: print(word)
            passes.append(word)
            failures = 0
      except:
         failures += 1
         if (failures > max_failures):
            print('ERROR: Could not consistently generate pass phrases of the desired length. Try raising the value of your "-l/--max_length" argument.')
            break

   if toFile: saveList(passes, filePath)
