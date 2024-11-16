from secrets import randbelow
from typing import Tuple

listEntry = lambda l: '' if len(l) == 0 else l[randbelow(len(l))]

maybe = lambda x=0 : randbelow(x or 2) == 1



def wordAndIndex(l) -> Tuple[str,int]:
  if len(l) == 0:return ('',0)
  num = randbelow(len(l))
  return (l[num],num)