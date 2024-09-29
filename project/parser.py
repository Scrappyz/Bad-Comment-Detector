def parse_word_fuck(target_word):
  words = ["fucking","fuck", "fck", "fuc", "fuk"]
  for i in range(len(words)):
    ci = 0
    cj = 0
    score = 0
    base = words[i]
    while ci < len(base) and cj < len(target_word):
      if base[ci] == target_word[cj]:
        cj += 1
        score += 1
      else:
        ci += 1
    if score >= len(base):
      print("Score: " + str(score))
      return True
  print("Not fuck")
  return False


    


if __name__ == "__main__":
  parse_word_fuck("fart")
  parse_word_fuck("fuck")
  parse_word_fuck("fucccckkkk")
  parse_word_fuck("fck")
  parse_word_fuck("feature")