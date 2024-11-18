import sys
from wordsmith_modules.word_parser import prepareWords

_, _, dbg = prepareWords()
dbg(["verb", sys.argv[1]])
