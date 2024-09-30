def create_dict(base):
  d = {}
  for i in range(len(base)):
    if base[i] in d:
      d[base[i]]["required"] += 1
    else:
      d[base[i]] = { "required": 1, "current": 0 }
  return d

def check_dict(d):
  for k in d:
    if d[k]["current"] < d[k]["required"]:
      return False
  return True

def parse_word_fuck(target_word):
  print("---------------")
  print(target_word)
  words = ["fucking","fuck", "fck", "fuc", "fuk"]
  for i in range(len(words)):
    ci = 0
    cj = 0
    base = words[i]
    d = create_dict(base)
    while ci < len(base) and cj < len(target_word):
      if base[ci] == target_word[cj]:
        cj += 1
        d[base[ci]]["current"] += 1
      else:
        ci += 1
    if check_dict(d):
      print(base)
      return True
  print("Not fuck")
  return False

def parse_bad_word(target_word, words):
  # print("---------------")
  # print(target_word)
  for i in range(len(words)):
    ci = 0
    cj = 0
    base = words[i]
    d = create_dict(base)
    while ci < len(base) and cj < len(target_word):
      if base[ci] == target_word[cj]:
        cj += 1
        d[base[ci]]["current"] += 1
      else:
        ci += 1
    if check_dict(d):
      # print(base)
      return base
  # print("Not bad word")
  return target_word
    
def main_test():
  parse_word_fuck("fart")
  parse_word_fuck("fuuu")
  parse_word_fuck("fuck")
  parse_word_fuck("fucccckkkk")
  parse_word_fuck("fck")
  parse_word_fuck("feature")
  parse_bad_word("motherfuckerrr", ["motherfucker", "mthrfcker"])
  parse_bad_word("asssssholeeeeee", ["asshole", "ashole"])

if __name__ == "__main__":
  main_test()
