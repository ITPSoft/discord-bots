import sys

from ufal.morphodita import *

# In Python2, wrap sys.stdin and sys.stdout to work with unicode.
if sys.version_info[0] < 3:
  import codecs
  import locale
  encoding = locale.getpreferredencoding()
  sys.stdin = codecs.getreader(encoding)(sys.stdin)
  sys.stdout = codecs.getwriter(encoding)(sys.stdout)

if len(sys.argv) < 2:
  sys.stderr.write('Usage: %s dict_file\n' % sys.argv[0])
  sys.exit(1)

sys.stderr.write('Loading dictionary: ')
morpho = Morpho.load(sys.argv[1])
if not morpho:
  sys.stderr.write("Cannot load dictionary from file '%s'\n" % sys.argv[1])
  sys.exit(1)
sys.stderr.write('done\n')

lemmas = TaggedLemmas()
lemmas_forms = TaggedLemmasForms()
line = sys.stdin.readline()
while line:
  tokens = line.rstrip('\r\n').split('\t')
  if len(tokens) == 1: # analyze
    result = morpho.analyze(tokens[0], morpho.GUESSER, lemmas)

    guesser = "Guesser " if result == morpho.GUESSER else ""
    for lemma in lemmas:
      sys.stdout.write('%sLemma: %s %s\n' % (guesser, lemma.lemma, lemma.tag))
  elif len(tokens) == 2: # generate
    result = morpho.generate(tokens[0], tokens[1], morpho.GUESSER, lemmas_forms)

    guesser = "Guesser " if result == morpho.GUESSER else ""
    for lemma_forms in lemmas_forms:
      sys.stdout.write('%sLemma: %s\n' % (guesser, lemma_forms.lemma))
      for form in lemma_forms.forms:
        sys.stdout.write('  %s %s\n' % (form.form, form.tag))

  line = sys.stdin.readline()