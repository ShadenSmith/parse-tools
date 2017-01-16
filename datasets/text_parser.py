
from nltk.stem.porter import PorterStemmer
import string

stops = 'a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your'

# read stopwords
stop_words = frozenset(stops.split(','))

# Precompute translation to very quickly convert to lowercase and remove
# punctuation except for spaces. Adapted from:
# <http://stackoverflow.com/questions/638893/what-is-the-most-efficient-way-in-
# python-to-convert-a-string-to-all-lowercase-st>
# now we can filter a str via s.translate(s, filter_table)
letter_set = frozenset(string.ascii_lowercase + string.ascii_uppercase + ' ')
deletions = ''.join(ch for ch in map(chr,range(256)) if ch not in letter_set)
filter_table = str.maketrans(\
    string.ascii_lowercase + string.ascii_uppercase + ' ',\
    string.ascii_lowercase + string.ascii_lowercase + ' ',\
    deletions)

# load porter stemmer
stemmer = PorterStemmer()

def parse_text(text_string):
  nbailed = 0
  for word in text_string.translate(filter_table).split():
    if word not in stop_words:
      # sometimes the stemmer crashes due to maximum recursion depth?
      try:
        yield stemmer.stem(word)
      except GeneratorExit:
        break

