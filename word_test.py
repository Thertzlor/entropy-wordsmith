import sys
from modules.word_parser import prepareWords

getWords = prepareWords()
getWords(debug_object=["verb",sys.argv[1]])