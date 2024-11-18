from math import inf
from secrets import randbelow
from typing import Literal
from wordsmith_modules.utilities import wordAndIndex, listEntry, maybe, resource_path

min_length = 2


def isVowel(t):
   return t in ('a', 'e', 'i', 'o', 'u')


def getList(path):
   with open(resource_path(path), 'r') as resRaw:
      res = (m.replace('_', ' ').strip() for m in resRaw.readlines() if not (len(m) <= min_length or m.startswith('  ')))
   return tuple(res)


def getMods(path):
   with open(resource_path(path), 'r') as resRaw:
      res = (tuple([w.replace('_', ' ').strip() for w in reversed(m.split(' '))]) for m in resRaw.readlines() if not m.startswith('  '))
   modStore = {}

   def setter(item):
      if item[0] in modStore: modStore[item[0]] = modStore[item[0]] + tuple([item[1]])
      else: modStore[item[0]] = tuple([item[1]])

   [setter(r) for r in res]
   return modStore


verb_type_index: list[int] = []


def separate_verb(v: str):
   split = v.split(" ")
   verb_type_index.append(int(split.pop()))
   return ' '.join(split)


words = {'adj': getList('./dict/index_adj.txt'), 'adv': getList('./dict/index_adv.txt'), 'noun': getList('./dict/index_noun.txt'), 'verb': tuple(separate_verb(x) for x in getList('./dict/index_verb.txt'))}

variations = {'adj': getMods('./dict/exc_adj.txt'), 'adv': getMods('./dict/exc_adv.txt'), 'noun': getMods('./dict/exc_noun.txt'), 'verb': getMods('./dict/exc_verb.txt')}


def prepareWords():
   characters_used = 0
   words_generated = 0
   char_limit = 0

   class Word:

      def __init__(self, kind: str, initiate: str | int | None = None, start: str | None = None, add_chars=1, max_expand=0) -> None:
         nonlocal char_limit, characters_used, words_generated
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
            word_list = tuple(x for x in not start and words[kind] or tuple(w for w in words[kind] if w.startswith(start.lower())) if len(x) < maxLength)
            if (len(word_list)) == 0: raise Exception("Could not find enough words.")
            (raw, index) = wordAndIndex(word_list)
         self._raw = raw
         self._index = index
         self._empty = raw == ''
         lowraw = self._raw.lower()
         self._variants = lowraw in variations[kind] and variations[kind][lowraw] or tuple()
         self._fixed_variant = None
         self._multi = " " in self._raw
         self._hyphen = "-" in self._raw
         self._possessive = "'s" in self._raw
         self._withArticle = " the " in self._raw or "the " in self._raw
         self._split = tuple(self._raw.split(" "))
         self._compound = None if len(self._split) < 2 else (self._split[1] in ("in", "at", "after", "from", "of", "and", "a", "it"))

      def export(self):
         if not self._fixed_variant and self._variants:
            self._fixed_variant = randbelow(len(self._variants))
         return self._raw if self._fixed_variant is None else self._variants[self._fixed_variant]

      def add(self):
         nonlocal characters_used, words_generated
         words_generated += 1
         characters_used += (len(self.export()) + self._space)

      def output(self):
         return {"index": self._index, "raw": self._raw, "variants": self._variants, "multi": self._multi, "hyphen": self._hyphen, "compound": self._compound, "possessive": self._possessive}

   class Noun(Word):

      def __init__(self, initiate=None, start=None, articled=False, pluralized=False, add_chars=1, prepend_number: int | None = None) -> None:
         super().__init__('noun', initiate, start, add_chars, max_expand=2)
         self._pluralized = pluralized
         self._articled = articled
         self._singular = self._raw
         pluraltarget = len(self._split) - 1
         if self._compound: pluraltarget = 0
         self._pluralTarget = pluraltarget
         plural = len(self._variants) != 0 and self._variants[len(self._variants) - 1] or ''
         self._generated_plural = plural == ''
         if plural == '':
            target = not self._multi and self._raw or self._split[self._pluralTarget]
            target = (target.endswith('y') and target[-2:] not in ('ay', 'ey')) and f'{target[:-1]}ies' or target.endswith('us') and f'{target[:-2]}a' or (target.endswith('z') or target[-2:] in ('ss', 'is', 'sh', 'ch')) and f'{target}es' or target.endswith('s') and target or f'{target}s'
            if not self._multi: plural = target
            else: plural = " ".join(i != self._pluralTarget and x or target for [i, x] in enumerate(self._split))

         self._plural = plural
         self._adjust_plural_caps()
         self._num_string = "" if prepend_number is None else f"{prepend_number} "
         self.add()

      @property
      def pluralized(self):
         return self._pluralized

      @property
      def articled(self):
         return self._articled

      def _getArticle(self, before: str = ''):
         if self._withArticle: return ''
         if self._pluralized: return listEntry(('the', 'some'))
         else: return listEntry(((before or self._raw[0]).upper() in ('A', 'U', 'O', 'I') and 'an' or 'a', 'the'))

      def export(self, adj: str = ''):
         core = self._pluralized and self._plural or self._singular
         if (not self._articled) or not self._getArticle(): return adj and f"{self._num_string}{adj} {core}" or f"{self._num_string}{core}"
         return f'{self._getArticle(adj)} {self._num_string}{adj and f" {adj} " or " "}{core}'

      def _adjust_plural_caps(self):
         if (self._generated_plural): return
         plural_split = self._plural.split(' ')
         if (len(plural_split) != len(self._split)): return
         if (self._raw[0].isupper()): print(self._raw)
         self._plural = ' '.join((x if (self._split[i][0].islower() or self._split[i][0].lower() != x[0]) else f"{self._split[i][0]}{x[1:]}") for i, x in enumerate(plural_split))

      def output(self):
         oldput = super().output()
         merged = dict()
         merged.update(oldput)
         newObj = {"pluralized": self._pluralized, "singular": self._singular, "plurtarget": self._split[self._pluralTarget], "plural": self._plural}
         merged.update(newObj)
         return merged

   class Adjective(Word):

      def __init__(self, initiate: str | int | None = None, start=None, mode: None | Literal["comparative", "superlative"] = None, add_chars=1, force_mode: Literal["random", "always", "never"] = "random") -> None:
         super().__init__("adj", initiate, start, add_chars)
         self.comparable = bool(self._variants)
         treat_comparable = force_mode == "always" or maybe(3)
         self._comparative = self.comparable and self._variants[0] or (f"more {self._raw}" if treat_comparable else None)
         self._superlative = self.comparable and self._variants[1] or (f"most {self._raw}" if treat_comparable else None)
         self._mode = mode
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

      def export(self):
         return self._raw if self._mode is None else self._comparative if self._mode == "comparative" else self._superlative

   class Verb(Word):

      def __init__(self, init=None, start=None, tense: Literal["present", "past"] | None = None, continuous=False, add_chars=1, dummy=False) -> None:
         super().__init__('verb', init, start, add_chars, max_expand=3)
         self._pastTense = tense == "past"
         self._continuous = continuous
         self._present = tense == "present"
         self._stem_past()
         self._frame = verb_type_index[self._index]

         if (not self._variants):
            if self._multi:
               self._variants = tuple(" ".join((x, " ".join(self._split[1:]))) for x in Verb(self._split[0], dummy=True)._variants)
            else:
               [suffix, cut] = self._stem_past()
               pastTense = f'{self._raw[:cut]}{suffix}'
               [suffix_p, cut_p] = self._stem_ing()
               partic = f'{self._raw[:cut_p]}{suffix_p}'
               self._variants = (pastTense, partic)
         elif len(self._variants) == 1:
            [suffix, cut] = self._stem_ing()
            partic = f'{self._raw[:cut]}{suffix}'
            self._variants = (self._variants[0], partic)
         if not self._multi:
            [suffix, cut] = self._stem_present()
            self._variants = self._variants + tuple([f'{self._raw[:cut]}{suffix}'])
         if not dummy: self.add()

      def _stem_present(self):
         last_letter = self._raw[-1:]
         second_to_last = self._raw[-2:-1]
         l = len(self._raw)
         match last_letter:
            case "o":
               return ("es" if second_to_last != "o" else "os", l if second_to_last != "o" else -1)
            case "z":
               return ("es", -1)
            case "h":
               return ("es", l)
            case "s":
               return ("es", l)
            case "y":
               return ("s" if isVowel(second_to_last) else "ies", l if isVowel(second_to_last) else -1)
            case _:
               return ("s", l)

      def _stem_past(self):
         last_letter = self._raw[-1:]
         second_to_last = self._raw[-2:-1]
         l = len(self._raw)
         match last_letter:
            case "l":
               return ("led", l if not isVowel(second_to_last) else -1)
            case "e":
               return ("d", l)
            case "p":
               return ("ped", l)
            case _:
               return ("ed", l)

      def _stem_ing(self):
         last_letter = self._raw[-1:]
         second_to_last = self._raw[-2:-1]
         l = len(self._raw)
         match last_letter:
            case "e":
               return ("ing", -1 if second_to_last not in ["e", "u"] else l)
            case "l":
               return ("ing", l)
            case "p":
               return ("ping", l if self._raw[-2:-1] != self._raw[-3:-2] else -1)
            case _:
               return ("ing", l)

      @property
      def pastTense(self):
         return self._pastTense

      @property
      def presentTense(self):
         return self._present

      @property
      def continuous(self):
         return self._continuous

      def output(self):
         oldput = super().output()
         merged = dict()
         merged.update(oldput)
         newObj = {}
         merged.update(newObj)
         return merged

      def export(self, context: str = ''):
         verbum = not self._variants and self._raw or self._pastTense and self._variants[0] or self._continuous and self._variants[1] or self._present and self._variants[2] or self._raw
         if self._multi:
            splitor = verbum.split(" ")
            match self._frame:
               case 0:
                  return f'{verbum} for {context}'
               case 1:
                  return f'{verbum} with {context}'
               case 2:
                  return f'{verbum} on {context}'
               case 3:
                  return f'{splitor.pop(0)} {context} {' '.join(splitor)}'
               case 5:
                  return f'{verbum} with {context}'
               case 12:
                  return f'{verbum} against {context}'
               case 13:
                  return f'{splitor.pop(0)} {context} {' '.join(splitor)}'
               case 15:
                  return f'{splitor.pop(0)} {context} {' '.join(splitor)}'
               case 19:
                  return f'{splitor.pop(0)} {context} {' '.join(splitor)}'
               case 21:
                  return f'{verbum} to {context}'
               case 23:
                  return f'{verbum} to {context}'
               case 25:
                  return f'{verbum} with {context}'
               case 26:
                  return f'{verbum} to {context}'
               case 27:
                  return f'{verbum} to {context}'
               case 31:
                  return f'{verbum} by {context}'
         return f"{verbum}{context and f' {context}' or ''}"

   class Adverb(Word):

      def __init__(self, initiate: str | int | None = None, start=None, add_chars=1, middle=False) -> None:
         super().__init__('adv', initiate, start, add_chars)
         self._middle = middle
         self.add()

      def export(self):
         return f', {self._raw},' if self._multi and self._middle else self._raw

   def single_word_debug_info(debug_object: list[str]):
      w_type = debug_object.pop(0)
      my_word = (Noun if w_type == "noun" else Verb if w_type == "verb" else Adjective if w_type == "adj" else Adverb)(*debug_object)
      print(my_word.export(), my_word.output(), sep='\n')

   def dict_info():
      print(f"Nouns: {len(words['noun'])}\nAdjectives: {len(words['adj'])}\nAdverbs: {len(words['adv'])}\nVerbs: {len(words['verb'])}")

   def getWords(c_limit=inf, first_word: None | Literal['noun1', 'noun2', 'verb', 'adjective', 'adverb'] = None, start: str | None = None, num=None, articles: Literal["random", "always", "never"] = "random", compare: Literal["random", "always", "never"] = "random", enclosed_adverb=False):
      nonlocal char_limit, characters_used, words_generated
      char_limit = c_limit
      characters_used = 0
      words_generated = 0

      plural1 = maybe()
      plural2 = maybe()
      article1 = (not maybe(3)) if articles == "random" else articles == "always"
      article2 = (not maybe(3)) if articles == "random" else articles == "always"
      adjMode = None
      if compare != "never": adjMode = None if maybe(3) else "comparative" if maybe() else "superlative"
      if compare == "always" and adjMode != None: adjMode = "comparative" if maybe() else "superlative"

      num_target = 0

      if num:
         if type(num) is bool:
            num = randbelow(8) + 2
         if plural1:
            num_target = 1
         else:
            plural2 = True
            num_target = 2

      noun1 = Noun(articled=article1, pluralized=plural1, start=start if first_word == "noun1" else None, prepend_number=num if num_target == 1 else None)
      noun2 = Noun(articled=article2, pluralized=plural2, start=start if first_word == "noun2" else None, prepend_number=num if num_target == 2 else None)
      verb = Verb(tense=(None if noun1.pluralized else "past" if maybe() else "present"), start=start if first_word == "verb" else None)
      adv = Adverb(start=start if first_word == "adverb" else None, middle=enclosed_adverb)
      adj = Adjective(start=start if first_word == "adjective" else None, mode=adjMode, force_mode=compare)
      return (noun1, noun2, adv, adj, verb)

   return getWords, dict_info, single_word_debug_info
