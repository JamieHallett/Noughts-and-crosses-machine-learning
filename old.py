def machineinput(player: int) -> None:
  machineBoardList[player].append(json.dumps(invertBoard(board, player))) #boardlist must be updated before move made, it is also inverted if machine is playing x
  text = filetext("moves.json")
  if json.dumps(invertBoard(board, player)) not in json.loads(text):
    # if move dict does not contain board, update moves with the board and possible moves
    moveDict = dict(json.loads(text))
    moveDict.update({json.dumps(invertBoard(board, player)): weightedEmptyTiles(invertBoard(board, player))}) 
    with open("moves.json", "wt") as f:
      f.write(json.dumps(moveDict, indent = 2))
    text = filetext("moves.json") #update text to include new board
    # -- old code --
    #file = open("moves.txt", "at")
    #file.write(json.dumps(invertBoard(board, player)) + "\n" \
    #+ json.dumps(weightedEmptyTiles(invertBoard(board, player))) + "\n/\n\n")
    #file.close()
  startmatch = None #re.search(re.escape(json.dumps(invertBoard(board, player))), text) #find current board in json
  if startmatch is not None and False: #this is the old code so I made it unreachable
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
      if len(weightedMoves) > 0 and board != [[" ", " ", " "], [" ", " ", " "],[" ", " ", " "]]: #the first move does this for training purposes
        move = random.choice(weightedMoves)
      else:
        move = random.choice(emptyTiles(invertBoard(board, player))) #random move if no items in moves (no moves appear if situation is guaranteed loss, or if the ai gets confused)
        #global guaranteedLosses
        #guaranteedLosses += 1 
      #print("chosen move",move) #debug
      board[int(move[0])][int(move[1])] = "o" if player == 0 else "x"
      machineMoveList[player].append(move)
      #print("movelist",machineMoveList[player]) #debug
      #print("boardlist",machineBoardList[player],"end of boardlist") #debug
      pass
  moveDict = dict(json.loads(text)) #store dict of moves as a variable
  moves = moveDict[(json.dumps(invertBoard(board, player)))] #moves are in the dict entry for the board
  print("moves",moves) #debug
  weightedMovesHalf = [[moves[i][0]] * int(moves[i][1]) for i in range(len(moves))]
  print("weighted moves step 1",weightedMovesHalf) #debug
  weightedMoves = [item for sublist in weightedMovesHalf for item in sublist]
  print("weighted moves step 2",weightedMoves) #debug
  if len(weightedMoves) > 0 and board != [[" ", " ", " "], [" ", " ", " "],[" ", " ", " "]]: #the first move is random for training purposes
    move = random.choice(weightedMoves)
  else:
    move = random.choice(emptyTiles(invertBoard(board, player))) #random move if no items in moves (no moves appear if situation is guaranteed loss, or if the ai gets confused)
  print("chosen move",move) #debug
  board[int(move[0])][int(move[1])] = "o" if player == 0 else "x"
  machineMoveList[player].append(move)

def machineLoss(player: int) -> None:
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
      if len(moveset) == 0:
        global guaranteedLosses
        guaranteedLosses += 1
        #print("no moves: guaranteed loss") #debug
      badMoveSpan = re.search(machineMoveList[player][-1], json.dumps(moveset))
      #print("badmove span",badMoveSpan) #debug
      if badMoveSpan is not None:
        #badMovePos = badMoveSpan.span()[0] + starts + 1 #This badmove position stuff is not necessary but I will not remove it (for machineLoss at least)
        #print("badmove pos",badMovePos) #debug
        #print("badmove but complicated",text[badMovePos:badMovePos+2],) #debug
        moveset = [[x[0], x[1] + 1] for x in moveset if x[0] != machineMoveList[player][-1]] \
        + [[machineMoveList[player][-1], 0]] #sets weight to 0 for bad move, increases weight by 1 for other moves
        #print("new moves",moveset) #debug
        newText = text[:starts] + json.dumps(moveset) + text[ends:]
        #print("move is in:", newText[(starts-10):(ends+10)]) #debug
        for i in range(len(machineBoardList[player])): #iterates through all played moves
          startmatch = re.search(re.escape(machineBoardList[player][i]), newText)
          #print("startmatch",startmatch) #debug
          if startmatch is not None:
            starts = startmatch.span()[1]
            endmatch = re.search("/", newText[starts:]) #find end
            if endmatch is not None:
              ends = endmatch.span()[0] + starts
              moveset = json.loads(newText[starts:ends])
              #dangerousMovePos = [x for x in moveset if x[0] == machineMoveList[player][i] else]
              newMoveset = [[x[0], x[1] + 1] for x in moveset if x[0] != machineMoveList[player][i]] \
              + [[x[0], (x[1] - 3 if x[1] > 0 else 0)] for x in moveset if x[0] == machineMoveList[player][i]] #reduces weight by 3 for moves that led to bad move, increases weight by 1 for other moves
              #print("new moveset",newMoveset) #debug
              newText = newText[:starts] + "\n" + json.dumps(newMoveset) + newText[ends:]
        file = open("moves.txt", "wt")
        file.write(newText) #saves changes to moves.txt
        if newText == text:
          global didntLearn
          didntLearn += 1
        file.close()


def machineWin(player: int) -> None:
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
      print("move is in:", newText[(starts-10):(ends+10)]) #debug
      for i in range(len(machineBoardList[player])): #iterates through all played moves
        startmatch = re.search(re.escape(machineBoardList[player][i]), newText)
        #print("startmatch",startmatch) #debug
        if startmatch is not None:
          starts = startmatch.span()[1]
          endmatch = re.search("/", newText[starts:]) #find end
          if endmatch is not None:
            ends = endmatch.span()[0] + starts
            moveset = json.loads(newText[starts:ends])
            newMoveset = [[x[0], (x[1] - 1 if x[1] > 0 else 0)] for x in moveset if x[0] != machineMoveList[player][i]] \
            + [[x[0], (x[1] + 3 if x[1] <= 20 else 20)] for x in moveset if x[0] == machineMoveList[player][i]] #increases weight by 3 for moves that led to winning move, decreases weight by 1 for other moves
            #print("new moveset",newMoveset) #debug
            newText = newText[:starts] + "\n\n" + json.dumps(newMoveset) + newText[ends:]
      file = open("moves.txt", "wt")
      file.write(newText) #saves changes to moves.txt
      if newText == text:
        global didntLearn
        didntLearn += 1
      file.close()


def machineTie(player: int) -> None: #machineTie(0) will call machineTie(1)
  text = filetext("moves.json")
  prevBoard = machineBoardList[player][-1]
  newText = "".join(text.split(prevBoard))
  # last move is not punished for ties
  for i in range(len(machineBoardList[player])): #iterates through all played moves
    startmatch = re.search(re.escape(machineBoardList[player][i]), newText)
    #print("startmatch",startmatch) #debug
    if startmatch is not None:
      starts = startmatch.span()[1]
      endmatch = re.search("/", newText[starts:]) #find end
      if endmatch is not None:
        ends = endmatch.span()[0] + starts
        moveset = json.loads(newText[starts:ends])
        newMoveset = [x for x in moveset if x[0] != machineMoveList[player][i]] \
        + [[x[0], (x[1] - 1 if x[1] > 0 else 0)] for x in moveset if x[0] == machineMoveList[player][i]] #decreases weight by 1 for moves leading to tie
        #print("new moveset",newMoveset) #debug
        newText = newText[:starts] + "\n" + json.dumps(newMoveset) + newText[ends:]
  file = open("moves.json", "wt")
  file.write(newText) #saves changes to moves.json
  if newText == text:
    global didntLearn
    didntLearn += 1
  file.close()
  if player == 0:
    machineTie(1)