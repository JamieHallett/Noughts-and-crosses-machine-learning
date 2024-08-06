if input("save backup? ") == "y": #save backup
  f = open("moves.txt", "r")
  text = f.read()
  f.close()

  f = open("backup.txt", "w")
  f.write(text)
  f.close()
  print("overwritten backup")

load = input("load backup? or press x to delete moves.txt ")
if load == "y" or load == "x": #load backup
  f = open("backup.txt", "r")
  text = f.read()
  f.close()

  if load == "x":
    if input("delete moves.txt? TYPE \"CoNfIrM\" TO CONFIRM AND PRESS ENTER TO CANCEL ") == "CoNfIrM":
      text = "" #DELETES MOVES.TXT
      print("deleted")
  
  f = open("moves.txt", "w")
  f.write(text)
  f.close()
  print("written to moves.txt")
