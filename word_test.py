import sys
from modules.word_parser import prepareWords

_, _, dbg = prepareWords()
dbg(["verb", sys.argv[1]])
