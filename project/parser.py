import ahocorasick

def createDict(base):
  d = {}
  for i in range(len(base)):
    if base[i] in d:
      d[base[i]]["required"] += 1
    else:
      d[base[i]] = { "required": 1, "current": 0 }
  return d

def checkDict(d):
  for k in d:
    if d[k]["current"] < d[k]["required"]:
      return False
  return True

def parseBadWord(target_word, words):
  # print("---------------")
  # print(target_word)
  for i in range(len(words)):
    ci = 0
    cj = 0
    base = words[i]
    wildCardFound = False
    d = createDict(base)
    while ci < len(base) and cj < len(target_word):
      if base[ci] == target_word[cj]:
        cj += 1
        d[base[ci]]["current"] += 1
      elif target_word[cj] == '*':
        cj += 1
        wildCardFound = True
      else:
        if wildCardFound:
          while ci < len(base) and base[ci] != target_word[cj]:
            d[base[ci]]["current"] += 1
            ci += 1
          wildCardFound = False
        else:
          ci += 1
    if wildCardFound:
      while ci < len(base):
        d[base[ci]]["current"] += 1
        ci += 1
    if checkDict(d):
      print(base)
      return base
  print("Not bad word")
  return target_word

# def parseBadWordWithAhoCorasick(targetWord, words):
#   automaton = ahocorasick.Automaton(ahocorasick.STORE_INTS)
#   for word in words:
#     automaton.add_word(word)
#   new_word = ""
#   current_letter = ''
#   for i in range(len(targetWord)):
#     if current_letter != targetWord[i]:
#       current_letter = targetWord[i]
#       new_word += current_letter
#   # print(new_word)
#   listOfWords = list(automaton.keys(new_word, '*', ahocorasick.MATCH_AT_LEAST_PREFIX))
#   if len(listOfWords) > 0:
#     print(listOfWords)
#     return listOfWords[0]
#   print(targetWord)
#   return targetWord

def fuzzyMatchWildCard(word, base):
  wordI = 0
  baseI = 0
  last = 0
  while wordI < len(word):
    if word[wordI] == base[baseI]:
      wordI += 1
      baseI += 1
      last += 1
      if baseI == len(base):
        # print("Success")
        # return base
        return True
    elif word[wordI] == '*':
      wordI += 1
      baseI += 1
      last += 1
      if baseI == len(base):
        # print("Success")
        # return base
        return True
    else:
      wordI += 1
      wordI -= last
      baseI = 0
      last = 0
  # print("Failed")
  # return word
  return False

def fuzzyMatchWord(word, words):
  for i in range(len(words)):
    if fuzzyMatchWildCard(word, words[i]):
      print(words[i])
      return words[i]
  print(word)
  return word

def findAllSubstrings(s, word_list, wildcard='*'):
  automaton = ahocorasick.Automaton(ahocorasick.STORE_INTS)
  for word in word_list:
    automaton.add_word(word)
  automaton.make_automaton()
  return set(automaton.keys(s, wildcard))

def isSubstring(s, word_list, wildcard='*'):
  listOfWords = findAllSubstrings(s, word_list, wildcard)
  if len(listOfWords) > 0:
    return True
  return False

def main_test():
  # parse_word_fuck("fart")
  # parse_word_fuck("fuuu")
  # parse_word_fuck("fuck")
  # parse_word_fuck("fucccckkkk")
  # parse_word_fuck("fck")
  # parse_word_fuck("feature")
  # parseBadWord("motherfuckerrr", ["motherfucker", "mthrfcker"])
  # parseBadWord("asssssholeeeeee", ["asshole", "ashole"])
  # parseBadWord("ffffff*****ccccckkkk", ["fuck"])
  # parseBadWord("ffffff*****ccccc**", ["fuck"])
  # parseBadWord("bigbird", ["bigbird"])
  # parseBadWord("helloworld", ["helloworld"])
  # parseBadWordWithAhoCorasick("f*ck*ng", ["fucking"])
  # parseBadWordWithAhoCorasick("a**hole", ["asshole"])
  # fuzzyMatchWildCard("bird", "bi")
  # fuzzyMatchWildCard("bi", "bird")
  # fuzzyMatchWord("bigb*rd", ["bird"])
  # fuzzyMatchWord("aass", ["ass"])
  # fuzzyMatchWord("aabaabaabaabaabaabaab", ["aaab"])
  print(isSubstring("bigbird", ["bird", "big"]))
  fuzzyMatchWord("bigbird", ["bird", "big"])

if __name__ == "__main__":
  main_test()
