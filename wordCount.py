import sys
import re
from collections import Counter

if len(sys.argv) is not 3:
    print("2 arguments required. Found" + str(len(sys.argv) - 1))
    exit()
try:
    lower_input_string = open(sys.argv[1]).read().lower()
    word_list = re.compile("\w+").findall(lower_input_string)
    counted_words_dictionary = Counter(word_list)
    output_file = open(sys.argv[2], "w")
    for word in sorted(counted_words_dictionary):
        output_file.write(word + " " + str(counted_words_dictionary[word]) + "\n")

except IOError as e:
    print("Could not read " + e.filename)
    exit()
