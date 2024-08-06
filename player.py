import json
import random
import re

import numpy as np

board = [
  [" ", " ", " "], 
  [" ", " ", " "],
  [" ", " ", " "]
]


machineMoveList = [[],[]]
machineBoardList = [[],[]]

guaranteedLosses = 0
didntLearn = 0
learningExperiences = 0

def filetext(file):
  f = open(file, "rt")
  text = f.read()
  f.close()
  return text

def filelines(file):
  f = open(file, "rt")
  lines = f.readlines()
  f.close()
  return lines

originalfile = filelines("moves.txt")

def drawBoard(D):
  print("   0   1   2")
  print("0  %s | %s | %s " % (D[0][0], D[0][1], D[0][2]))
  print("  ---+---+---")
  print("1  %s | %s | %s " % (D[1][0], D[1][1], D[1][2]))
  print("  ---+---+---")
  print("2  %s | %s | %s " % (D[2][0], D[2][1], D[2][2]))

def checkvalid(In, D):
  if In[0] >= "0" and In[0] <= "2" and In[1] >= "0" and In[1] <= "2":
    return D[int(In[0])][int(In[1])] == " "
  return False

def checkRows(board):
    for row in board:
        if len(set(row)) == 1 and row[0] != " ":
            return row[0]
    return 0

def checkDiagonals(board):
  if len(set([board[i][i] for i in range(len(board))])) == 1 and board[0][0] != " ":
    return board[0][0]
  if len(set([board[i][len(board)-i-1] for i in range(len(board))])) == 1 and board[0][len(board)-1] != " ":
      return board[0][len(board)-1]
  return 0

def checkWin(board):
  #transposition to check rows, then columns
  for newBoard in [board, np.transpose(board)]:
    result = checkRows(newBoard)
    if result:
      return result
  return checkDiagonals(board)

def checkTie(board):
  return " " not in "".join(board[0]+board[1]+board[2])

def emptyTiles(area):
  return [str(i//3) + str(i%3) for i in range(9) if area[i//3][i%3] == " "]

def invertBoard(area, on):
  if on:
    return [["o" if i == "x" else "x" if i == "o" else i for i in row] for row in area]
  else:
    return area

def humaninput():
  machineBoardList[1].append(json.dumps(invertBoard(board, 1))) #why waste free learning?
  while True:
    move = input("enter row, col with no separator\n")
    if checkvalid(move, board):
      board[int(move[0])][int(move[1])] = "x"
      drawBoard(board)
      break
    else:
      print("invalid move")
  machineMoveList[1].append(move)

def weightedEmptyTiles(area):
  return [[str(i//3) + str(i%3), 10] for i in range(9) if area[i//3][i%3] == " "] #looks like I can put this on one line

def machineinput(player):
  machineBoardList[player].append(json.dumps(invertBoard(board, player))) #boardlist must be updated before move made, it is also inverted if machine is playing x
  text = filetext("moves.txt")
  if json.dumps(invertBoard(board, player)) + "\n" not in filelines("moves.txt"):
    print("computer has never seen this move") #debug
    file = open("moves.txt", "at")
    file.write(json.dumps(invertBoard(board, player)) + "\n" \
    + json.dumps(weightedEmptyTiles(invertBoard(board, player))) + "\n/\n\n")
    file.close()
  text = filetext("moves.txt")
  startmatch = re.search(re.escape(json.dumps(invertBoard(board, player))), text) #find current board in json
  if startmatch is not None:
    starts = startmatch.span()[1]
    endmatch = re.search("/", text[starts:]) #find end
    if endmatch is not None:
      ends = endmatch.span()[0] + starts
      #print("moves raw",text[starts:ends]) #debug
      moves = json.loads(text[starts:ends]) #get moves
      #print("moves",moves) #debug
      weightedMovesHalf = [[moves[i][0]] * int(moves[i][1]) for i in range(len(moves))]
      #print("weighted moves step 1",weightedMovesHalf) #debug
      weightedMoves = [item for sublist in weightedMovesHalf for item in sublist]
      #print("weighted moves step 2",weightedMoves) #debug
      if len(weightedMoves) > 0:
        move = random.choice(weightedMoves)
      else:
        move = random.choice(emptyTiles(invertBoard(board, player)))
        global guaranteedLosses
        guaranteedLosses += 1 #random move if no items in moves (no moves appear if situation is guaranteed loss)
      #print("chosen move",move) #debug
      board[int(move[0])][int(move[1])] = "o" if player == 0 else "x"
      machineMoveList[player].append(move)
      #print("movelist",machineMoveList[player]) #debug
      #print("boardlist",machineBoardList[player],"end of boardlist") #debug

      drawBoard(board)

def machineLoss(player):
  text = filetext("moves.txt")
  prevBoard = machineBoardList[player][-1]
  startmatch = re.search(re.escape(prevBoard), text) #find start by finding board
  #print("last board",machineBoardList[player][-1]) #debug
  #print("bad move",machineMoveList[player][-1]) #debug
  if startmatch is not None:
    starts = startmatch.span()[1]
    endmatch = re.search("/", text[starts:]) #find end
    if endmatch is not None:
      ends = endmatch.span()[0] + starts
      moveset = json.loads(text[starts:ends]) #get set of moves
      #print("moves",moveset) #debug
      #if len(moveset) == 0: #debug
        #print("no moves: guaranteed loss") #debug
      badMoveSpan = re.search(machineMoveList[player][-1], json.dumps(moveset))
      #print("badmove span",badMoveSpan) #debug
      if badMoveSpan is not None:
        #badMovePos = badMoveSpan.span()[0] + starts + 1 #This badmove position stuff is not necessary but I will not remove it (for machineLoss at least)
        #print("badmove pos",badMovePos) #debug
        #print("badmove but complicated",text[badMovePos:badMovePos+2],) #debug
        moveset = [x for x in moveset if x[0] != machineMoveList[player][-1]] \
        + [[machineMoveList[player][-1], 0]] #sets weight to 0 for bad move
        #print("new moves",moveset) #debug
        newText = text[:starts] + json.dumps(moveset) + text[ends:]
        #print("move is in:", newText[(starts-10):(ends+10)]) #debug
        for i in range(len(machineBoardList[player])):
          startmatch = re.search(re.escape(machineBoardList[player][i]), newText)
          #print("startmatch",startmatch) #debug
          if startmatch is not None:
            starts = startmatch.span()[1]
            endmatch = re.search("/", newText[starts:]) #find end
            if endmatch is not None:
              ends = endmatch.span()[0] + starts
              moveset = json.loads(newText[starts:ends])
              #dangerousMovePos = [x for x in moveset if x[0] == machineMoveList[player][i] else]
              newMoveset = [x for x in moveset if x[0] != machineMoveList[player][i]] \
              + [[x[0], x[1] - (1 if x[1] != 0 else 0)] for x in moveset if x[0] == machineMoveList[player][i]] #reduces weight for moves that led to bad move
              #print("new moveset",newMoveset) #debug
              newText = newText[:starts] + "\n" + json.dumps(newMoveset) + newText[ends:]
        file = open("moves.txt", "wt")
        file.write(newText)
        if newText == text:
          global didntLearn
          didntLearn += 1
        file.close()

def machineWin(player):
  text = filetext("moves.txt")
  prevBoard = machineBoardList[player][-1]
  startmatch = re.search(re.escape(prevBoard), text) #find start by finding board
  #print("last board",machineBoardList[player][-1]) #debug
  #print("winning move",machineMoveList[player][-1]) #debug
  if startmatch is not None:
    starts = startmatch.span()[1]
    endmatch = re.search("/", text[starts:]) #find end
    if endmatch is not None:
      ends = endmatch.span()[0] + starts
      moveset = json.loads(text[starts:ends]) #get set of moves
      #print("moves",moveset) #debug
      #if len(moveset) == 0: #debug
        #print("no moves: full board?") #debug
      moveset = [[x[0], 0] for x in moveset if x[0] != machineMoveList[player][-1]] \
      + [[machineMoveList[player][-1], 10]] #sets all weights to 0, apart from the winning move
      #print("new moves",moveset) #debug
      newText = text[:starts] + json.dumps(moveset) + text[ends:]
      #print("move is in:", newText[(starts-10):(ends+10)]) #debug
      for i in range(len(machineBoardList[player])):
        startmatch = re.search(re.escape(machineBoardList[player][i]), newText)
        #print("startmatch",startmatch) #debug
        if startmatch is not None:
          starts = startmatch.span()[1]
          endmatch = re.search("/", newText[starts:]) #find end
          if endmatch is not None:
            ends = endmatch.span()[0] + starts
            moveset = json.loads(newText[starts:ends])
            newMoveset = [x for x in moveset if x[0] != machineMoveList[player][i]] \
            + [[x[0], (x[1] + 2 if x[1] <= 20 else 20)] for x in moveset if x[0] == machineMoveList[player][i]] #increases weight by 2 for moves that led to winning move
            #print("new moveset",newMoveset) #debug
            newText = newText[:starts] + "\n" + json.dumps(newMoveset) + newText[ends:]
      file = open("moves.txt", "wt")
      file.write(newText)
      if newText == text:
        global didntLearn
        didntLearn += 1
      file.close()

drawBoard(board)    

ties = 0
maxGames = 5000 #change this to change games
gamesChunks = 0
subGames = 0


#print(weightedEmptyTiles(board)) #debug
#input("Press enter to start")

try:
  for gamesChunks in range(int(maxGames/10)):
    for subGames in range(10):
      while True:
        humaninput()
        if checkWin(board):
          print("You win")
          machineLoss(0)
          machineWin(1)
          break
        if checkTie(board):
          print("tie")
          ties += 1
          break
        machineinput(0)
        if checkWin(board):
          print("You lost")
          machineLoss(1)
          machineWin(0)
          break
        if checkTie(board):
          print("tie")
          ties += 1
          break
      board = [
        [" ", " ", " "], 
        [" ", " ", " "],
        [" ", " ", " "]
      ]
      machineMoveList = [[],[]]
      machineBoardList = [[],[]]

    text = filetext(r"moves.txt")
    f = open(r"usermoves.txt", "wt")
    f.write(text)
    f.close()

  print("\n\nFinished at",maxGames,"games")
except KeyboardInterrupt:
  print("\n\nInterrupted. Games played:",gamesChunks * 10 + subGames)

print("ties:",ties)
print("guaranteed losses:",guaranteedLosses)
print("times didn\'t learn:",didntLearn)
#print("learning experiences:",games-ties-guaranteedLosses-didntLearn)
print("added lines:",len(filelines("moves.txt")) - len(originalfile))
