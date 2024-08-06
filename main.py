import copy
import json
import random
import time

import numpy as np

board = [
  [" ", " ", " "], 
  [" ", " ", " "],
  [" ", " ", " "]
]

machineMoveList: list[list[str]] = [[],[]]
machineBoardList: list[list[str]] = [[],[]]

startTime = time.time()
guaranteedLosses = 0
didntLearn = 0
learningExperiences = 0

def filetext(file: str):
  with open(file, "rt") as f:
    return f.read()

def filelines(file: str):
  with open(file, "rt") as f:
    return f.readlines()

originalfile = filelines("moves.json")
moveDictBuffer: dict[str, list[list[str | int]]] = json.loads(filetext("moves.json"))

def printAndLog(*strings: str, sep = " ", end = "\n"):
  print(*strings, sep= sep, end= end)
  with open("log.txt", "a") as f:
    f.write(sep.join(strings) + end)

def drawBoard(D: list[list[str]] , Print = True ):
  if Print:
    print("   0   1   2")
    print("0  %s | %s | %s " % (D[0][0], D[0][1], D[0][2]))
    print("  ---+---+---")
    print("1  %s | %s | %s " % (D[1][0], D[1][1], D[1][2]))
    print("  ---+---+---")
    print("2  %s | %s | %s " % (D[2][0], D[2][1], D[2][2]))
  return """
   0   1   2
0  %s | %s | %s 
  ---+---+---
1  %s | %s | %s 
  ---+---+---
2  %s | %s | %s""" % tuple([D[i // 3][i % 3] for i in range(9)])

def checkvalid(In: str, D: list[list[str]] ):
  if In[0] >= "0" and In[0] <= "2" and In[1] >= "0" and In[1] <= "2":
    return D[int(In[0])][int(In[1])] == " "
  return False

def checkRows(board: list[list[str]]):
  for row in board:
    if len(set(row)) == 1 and row[0] != " ":
      return row[0]
  return 0

def checkDiagonals(board: list[list[str]] ):
  if len(set([board[i][i] for i in range(len(board))])) == 1 and board[0][0] != " ":
    return board[0][0]
  if len(set([board[i][len(board)-i-1] for i in range(len(board))])) == 1 and board[0][len(board)-1] != " ":
    return board[0][len(board)-1]
  return 0

def checkWin(board: list[list[str]] ):
  #transposition to check rows, then columns
  for newBoard in [board, np.transpose(board)]:
    result = checkRows(newBoard)
    if result:
      return result
  return checkDiagonals(board)

def checkTie(board: list[list[str]] ):
  return " " not in "".join(board[0]+board[1]+board[2])

def emptyTiles(area: list[list[str]] ):
  return [str(i//3) + str(i%3) for i in range(9) if area[i//3][i%3] == " "]
  
def invertBoard(area: list[list[str]] , on: int):
  if on:
    return [["o" if i == "x" else "x" if i == "o" else i for i in row] for row in area]
  else:
    return area

def humaninput() -> None:
  while True:
    move = input("enter row, column with no separator\n")
    if checkvalid(move, board):
      board[int(move[0])][int(move[1])] = "x"
      drawBoard(board)
      break
    else:
      print("invalid move")

def weightedEmptyTiles(area: list[list[str]] ) -> list[list[str | int]]:
  return [[str(i//3) + str(i%3), 10] for i in range(9) if area[i//3][i%3] == " "] #looks like I can put this on one line

def machineinput(player: int) -> None:
  machineBoardList[player].append(json.dumps(invertBoard(board, player))) #boardlist must be updated before move made, it is also inverted if machine is playing x
  global moveDictBuffer
  moveDict = copy.deepcopy(moveDictBuffer) #store dict of moves as a variable
  if json.dumps(invertBoard(board, player)) not in moveDict:
    # if move dict does not contain board, update moves with the board and possible moves
    moveDict.update({json.dumps(invertBoard(board, player)): weightedEmptyTiles(invertBoard(board, player))}) 
    #moveDictBuffer will be updated at the end of the function
  
  moves = moveDict[(json.dumps(invertBoard(board, player)))] #moves are in the dict entry for the board, board inverted if player x
  #print("moves",moves) #debug
  weightedMovesHalf = [str(i) * int(moves[i][1]) for i in range(len(moves))]
  #print("weighted moves step 1",weightedMovesHalf) #debug
  weightedMoves: list[str] = [str(item) for sublist in weightedMovesHalf for item in sublist]
  #print("weighted moves step 2",weightedMoves) #debug

  #the moves in weightedMoves are not actual moves, they look like this: ["1","1","1","2","2","3"]
  #whereas real weighted moves would look like ["00", "00", "00", "01", "01", "02", "10", "10", "10", "11", "21"]
  #the numbers in weightedMoves variable are the indices of the moves in the moves variable, which can be looked up
  
  if len(weightedMoves) > 0 and board != [[" ", " ", " "], [" ", " ", " "],[" ", " ", " "]]:
    moveNum = random.choice(weightedMoves)
    move = str(moves[int(moveNum)][0])
  else:
    #random move if no items in moves (no moves appear if situation is guaranteed loss, or if the ai gets confused)
    #also random if board is empty, for training purposes
    move = random.choice(emptyTiles(invertBoard(board, player)))
  #print("chosen move",move) #debug
  board[int(move[0])][int(move[1])] = "o" if player == 0 else "x" #p1 is x, p0 is o
  machineMoveList[player].append(move)

def machineLoss(player: int) -> None:
  prevBoard = machineBoardList[player][-1]
  #print("last board",machineBoardList[player][-1]) #debug
  #print("bad move",machineMoveList[player][-1]) #debug
  global moveDictBuffer
  moveDict = copy.deepcopy(moveDictBuffer) #store dict of moves as a variable
  if json.dumps(invertBoard(board, player)) not in moveDict:
    # prevent crashing by adding previous board to moveDict if it does not exist
    moveDict.update({prevBoard: weightedEmptyTiles(json.loads(prevBoard))})
  moveset = moveDict[json.dumps(json.loads(prevBoard))] #moves are in the dict entry for the previous board
  #print("moves",moveset) #debug
  #if len(moveset) == 0: #this is not reachable anymore
    #global guaranteedLosses
    #guaranteedLosses += 1
    #print("no moves: guaranteed loss") #debug
  moveset = [[x[0], int(x[1]) + 1] for x in moveset if x[0] != machineMoveList[player][-1] \
  and int(x[1]) > 0] + [[machineMoveList[player][-1], 0]] #sets weight to 0 for bad move, increases weight by 1 for other moves with a non-0 weight
  #print("new moves",moveset) #debug
  moveDict[json.dumps(invertBoard(json.loads(prevBoard), player))] = moveset #update move dict
  
  for i in range(len(machineBoardList[player])): #iterates through all played moves
    if json.dumps(invertBoard(board, player)) not in moveDict:
      # prevent crashing by adding the board to moveDict if it does not exist
      moveDict.update({machineBoardList[player][i]: weightedEmptyTiles(json.loads(machineBoardList[player][i]))})
    moveset = moveDict[json.dumps(json.loads(machineBoardList[player][i]))] #board seems not to need inverting here
    #print("moveset",moveset) #debug
    #print("bad move",machineMoveList[player][i]) #debug
    newMoveset = [[x[0], (int(x[1]) + 1 if int(x[1]) < 20 else 20)] for x in moveset if x[0] != machineMoveList[player][i]] \
    + [[x[0], (int(x[1]) - 3 if int(x[1]) > 0 else 0)] for x in moveset if x[0] == machineMoveList[player][i]] #reduces weight by 3 for moves that led to bad move, increases weight by 1 for other moves
    #print("new moveset",newMoveset) #debug
    moveDict[json.dumps(invertBoard(json.loads(machineBoardList[player][i]), player))] = newMoveset #update move dict with new moveset
  #if moveDict == moveDictBuffer: #check if no change made, if so didn't learn
  #  global didntLearn
  #  didntLearn += 1
  moveDictBuffer = copy.deepcopy(moveDict) #save changes to moveDictBuffer


def machineWin(player: int) -> None:
      text = filetext("moves.json")
      prevBoard = machineBoardList[player][-1]
      #print("last board",machineBoardList[player][-1]) #debug
      #print("winning move",machineMoveList[player][-1]) #debug
      moveDict = dict(json.loads(text)) #store dict of moves as a variable
      moveset = moveDict[json.dumps((json.loads(machineBoardList[player][-1])))] #moves are in the dict entry for the previous board
      print("moves",moveset) #debug
      #if len(moveset) == 0: #this is not reachable anymore
        #global guaranteedLosses
        #guaranteedLosses += 1
        #print("no moves: guaranteed loss") #debug
      moveset = [[x[0], 0] for x in moveset if x[0] != machineMoveList[player][-1]] \
      + [[machineMoveList[player][-1], 10]] #sets weight to 10 for winning move, sets weight to 0 for other moves
      #print("new moves",moveset) #debug
      moveDict[json.dumps(invertBoard(board, player))] = moveset #update move dict
      for i in range(len(machineBoardList[player])): #iterates through all played moves
        moveset = moveDict[json.dumps(invertBoard(json.loads(machineBoardList[player][i]), 0))] 
        #print("moveset",moveset) #debug
        #print("bad move",machineMoveList[player][i]) #debug
        newMoveset = [[x[0], (x[1] - 1 if x[1] > 0 else 0)] for x in moveset if x[0] != machineMoveList[player][i]] \
        + [[x[0], (x[1] + 3 if x[1] <= 20 else 20)] for x in moveset if x[0] == machineMoveList[player][i]] #increases weight by 3 for moves that led to win, decreases weight by 1 for other moves
        #print("new moveset",newMoveset) #debug
        moveDict[json.dumps(invertBoard(board, player))] = moveset #update move dict
      with open("moves.json", "wt") as file:
        file.write(json.dumps(moveDict, indent = 2)) #saves changes to moves.json
      if json.dumps(moveDict, indent = 2) == text:
        global didntLearn
        didntLearn += 1

def machineTie(player: int) -> None: #machineTie(0) will call machineTie(1)
    text = filetext("moves.json")
    moveDict = dict(json.loads(text)) #store dict of moves as a variable
  
    # last move is not punished for ties
    for i in range(len(machineBoardList[player])): #iterates through all played moves
      moveset = moveDict[json.dumps(invertBoard(json.loads(machineBoardList[player][i]), 0))]
      #print("moveset",moveset) #debug
      #print("bad move",machineMoveList[player][i]) #debug
      newMoveset = [x for x in moveset if x[0] != machineMoveList[player][i]] \
      + [[x[0], (x[1] - 1 if x[1] > 0 else 0)] for x in moveset if x[0] == machineMoveList[player][i]] #reduces weight by 1 for moves that led to tie
      #print("new moveset",newMoveset) #debug
      moveDict[json.dumps(invertBoard(board, player))] = moveset #update move dict
    with open("moves.json", "wt") as file:
      file.write(json.dumps(moveDict)) #saves changes to moves.json
    if json.dumps(moveDict) == text:
      global didntLearn
      didntLearn += 1
    machineTie(1)   

drawBoard(board)    

ties = 0
MAX_GAMES = 5000 #change this to change games
gamesChunks = 0
subGames = 0


#print(weightedEmptyTiles(board)) #debug
#input("Press enter to start")

try:
  for gamesChunks in range(int(MAX_GAMES/10)):
    for subGames in range(10):
      while True: #loop is broken when game ends
        machineinput(1)
        #input(drawBoard(board, Print = False) + "\nPress enter to continue")#debug
        #drawBoard(board)
        if checkWin(board):
          print("x win")
          machineLoss(0)
          #machineWin(1)
          break
        if checkTie(board):
          print("tie")
          ties += 1
          #machineTie(0) #this will call machineTie(1) as well
          break
        
        machineinput(0)
        #input(drawBoard(board, Print = False) + "\nPress enter to continue")#debug
        #drawBoard(board)
        if checkWin(board):
          print("o win")
          machineLoss(1)
          #machineWin(0)
          break
        if checkTie(board):
          print("tie")
          ties += 1
          #machineTie(0)
          break

      #preparation before the next game
      board = [
        [" ", " ", " "], 
        [" ", " ", " "],
        [" ", " ", " "]
      ]
      machineMoveList = [[],[]]
      machineBoardList = [[],[]]
      
    #move buffer goes into JSON file every 10 games
    with open("moves.json", "wt") as f:
      f.write(json.dumps(moveDictBuffer))#, indent = 2))
  
  print("\n\nFinished at",MAX_GAMES,"games")
except KeyboardInterrupt: 
  print("\n\nInterrupted. Games played:",gamesChunks * 10 + subGames)
finally: # print all of this after interrupt or finish, and send to log.txt
  printAndLog("games:",str(gamesChunks * 10 + subGames))
  timeTaken = time.time() - startTime
  printAndLog("time taken:", str(timeTaken), "s")
  try:
    printAndLog("time per game:", str(timeTaken / (gamesChunks * 10 + subGames)), "s")
  except ZeroDivisionError:
    printAndLog("time per game: N/A s")
  printAndLog("ties:", str(ties))
  printAndLog("guaranteed losses:", str(guaranteedLosses))
  printAndLog("times didn\'t learn:",str(didntLearn))
  printAndLog("learning experiences:",str(gamesChunks * 10 + subGames -ties-guaranteedLosses-didntLearn))
  
  if input("Indent to get data on time per line and added lines. Indent moves.json? (y/n) "):
    text = filetext("moves.json")
    with open("moves.json", "wt") as file:
      file.write(json.dumps(json.loads(text), indent = 2))
    printAndLog("Indented successfully")
  printAndLog("added lines:",str(len(filelines("moves.json")) - len(originalfile)))
  
  try:
    printAndLog("time per line:",str(timeTaken / (len(filelines("moves.json")) \
  - len(originalfile))), "s")
  except ZeroDivisionError:
    printAndLog("time per line: N/A s")
    
  if len(filelines("moves.json")) - len(originalfile) < 0:
    if input("Moves.json may be corrupt. Revert? (y/n) ") == "y":
      with open("moves.json", "wt") as file:
        file.write("".join(originalfile))
        printAndLog("Reverted successfully")
    else:
      print("Did not revert")
      
  
  printAndLog()