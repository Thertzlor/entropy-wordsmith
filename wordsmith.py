from modules.phrase_composer import mainProcess
from math import inf
from argparse import ArgumentParser

parser = ArgumentParser(description='Welcome to Entropy Wordsmith!',prog='Entropy Wordsmith')
parser.add_argument('-c','--count', type=int, default=20,help="The number of passphrases to generate. Defaults to 20.",metavar='')
parser.add_argument('-i','--include_number', action="store_true",help="If the password is required to contain a number, this setting will force one of the nouns to be pluralized and prepend a random number in the range of 2-9.")
parser.add_argument('-n','--set_number',help="Same as the -i/--include-number argument, but directly specifies the number to use.", type=int,metavar='')
parser.add_argument('-s','--start', type=str, help="Specify a letter that the first word of the passphrase needs to start with (not counting articles).",metavar='',default='')
parser.add_argument('-l','--max_length',help="The maximum number of characters the passphrase should contain. Shorter settings give less varied results.", type=int,default=inf,metavar='')
parser.add_argument('-m','--mode', type=int, help="There are 5 word combination modes used to generate passphrases. They are normally chosen at random, but with this option you can specify a single one for the whole batch. Accepts a number in the range 1-5.",metavar='',default=0)
parser.add_argument('-e','--ending',default='.', help='Select which characters should be appended at the end of the passphrase. Defaults to a period.',metavar='')
parser.add_argument('-a','--no_articles', help='Do not prepend nouns with articles',action="store_true")
parser.add_argument('-u','--underscore', action="store_true", help="Replace the spaces in the passphrase with underscores.")
parser.add_argument('-p','--path',type=str,help="A path of an output file. Leave blank to write the results to stdout.",metavar='',default='')
parser.add_argument('-v','--version',action='version', version='%(prog)s 1.0')

args = parser.parse_args()

if args.start and len(args.start) != 1:
    raise SystemExit('the s/--start argument only accepts a single letter.')
if args.mode and args.mode not in (1,2,3,4,5):
    raise SystemExit('the m/--mode argument has to be between between 1 and 5.')
    
mainProcess(args.path,args.start,args.count,args.max_length,args.underscore,args.set_number or args.include_number,args.ending,args.mode,args.no_articles)
