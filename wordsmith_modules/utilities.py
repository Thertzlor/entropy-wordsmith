from os import path
from secrets import randbelow
import sys
from typing import Any, Callable, Tuple

listEntry: Callable[[list | tuple], Any] = lambda l: '' if len(l) == 0 else l[randbelow(len(l))]

maybe = lambda x=0: randbelow(x or 2) == 1


def wordAndIndex(l) -> Tuple[str, int]:
   if len(l) == 0: return ('', 0)
   num = randbelow(len(l))
   return (l[num], num)


def resource_path(relative_path):
   """ Get absolute path to resource, works for dev and for PyInstaller """
   try:
      base_path = sys._MEIPASS  # type: ignore
   except Exception:
      base_path = path.abspath(".")

   return path.join(base_path, relative_path)
