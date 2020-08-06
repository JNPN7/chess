import pygame
import sys

#initializing display width and height
DWIDTH = 560
DHEIGHT = 560
EXTRA_DHEIGHT = 50
DIMENSION = 8
SQSIZE = DWIDTH // DIMENSION
TEXT_X_POS = DWIDTH //3
TEXT_Y_POS = DHEIGHT + 10
RADIUS = 8

FPS = 20

#colors
WHITE = (255,255,255)
GRAY = (105,105,105)
GOLD = (218,165,32)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

which_section = ['menu']

def printText(turn, screen, checked, checkMate):
	font = pygame.font.SysFont("Carousel", 30)
	screen.blit(font.render('Space => undo',2 ,RED), (5, DHEIGHT))
	if checkMate:
		screen.blit(font.render('Press z to continue..',2 ,RED), (5, DHEIGHT+22))
	font = pygame.font.SysFont("Carousel", 40)
	screen.blit(font.render('Turn :', 2, GRAY), (TEXT_X_POS, TEXT_Y_POS))
	if turn == 'w':
		turn = 'White'
		turn = font.render(turn, 2, WHITE)
	else:
		turn = 'Black'
		turn = font.render(turn, 2, BLACK)
		# print (turn)
	screen.blit(turn, (TEXT_X_POS + 90, TEXT_Y_POS))
	if checked:
		if not checkMate:
			turn = 'Checked'
		else:
			turn = 'CheckMate'
		turn = font.render(turn, 2, WHITE)
		screen.blit(turn, (TEXT_X_POS + 90 + 125, TEXT_Y_POS))
	# if checked('b'):
	# 	turn = 'Checked'
	# 	turn = font.render(turn, 2, BLACK)
	# 	screen.blit(turn, (TEXT_X_POS + 90 + 125, TEXT_Y_POS))


class ChessState():
	"""docstring for chessState"""
	def __init__(self):
		self.board = [
		['br', 'bh', 'bb', 'bq', 'bk', 'bb', 'bh', 'br'],
		['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
		['--', '--', '--', '--', '--', '--', '--', '--'],
		['--', '--', '--', '--', '--', '--', '--', '--'],
		['--', '--', '--', '--', '--', '--', '--', '--'],
		['--', '--', '--', '--', '--', '--', '--', '--'],
		['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
		['wr', 'wh', 'wb', 'wq', 'wk', 'wb', 'wh', 'wr'],
		]
		self.turn = 'w'
		self.log=[]
	
	def movePiece(self, move):
		self.board[move.from_box[0]][move.from_box[1]] = '--'
		self.board[move.to_box[0]][move.to_box[1]] = move.pieceMoved
		self.log.append(move.chesslog())
		if self.turn == 'w':
			self.turn = 'b'
		else:
			self.turn = 'w'
		
	
	def undoMove(self):
		if self.log:
			prevmove = (self.log.pop())
			# print(prevmove)
			from_box = prevmove[0]
			to_box = prevmove[1]
			moved_piece = prevmove[2]
			captured_piece = prevmove[3]
			self.board[from_box[0]][from_box[1]] = moved_piece
			self.board[to_box[0]][to_box[1]] = captured_piece
			if self.turn == 'w':
				self.turn = 'b'
			else:
				self.turn = 'w'
		pass
	
	def getValidMoves(self):
		#check checked for black
		moves = self.getAllMoves(self.board)
		for i in range(len(moves) - 1, -1,-1):
			self.movePiece(moves[i])
			if self.turn == 'w':
				self.turn = 'b'
			else:  
				self.turn = 'w'
			if self.check():
				moves.remove(moves[i])
			if self.turn == 'w':
				self.turn = 'b'
			else:
				self.turn = 'w'
			self.undoMove()
		return moves

	def getAllMoves(self, board):
		moves = []
		for i in range(len(board)):
			for j in range(len(board[i])):
				if board[i][j][1] == 'p':
					self.getPawnMoves(i, j, moves, board)
				elif board[i][j][1] == 'r':
					self.getRookMoves(i, j, moves, board)
				elif board[i][j][1] == 'h':
					self.getKnightMoves(i, j, moves, board)
				elif board[i][j][1] == 'b':
					self.getBishopMoves(i, j, moves, board)
				elif board[i][j][1] == 'q':
					self.getQueenMoves(i, j, moves, board)
				elif board[i][j][1] == 'k':
					self.getKingMoves(i, j, moves, board)
				pass
			pass
		return moves

	def checkCheck(self, of_which):
		moves = self.getAllMoves(self.board)
		# print(self.getKingsPosition(of_which))
		for move in moves:
			if move.to_box == self.getKingsPosition(of_which):
				return True
		return False

	def check(self):
		result =  False
		if self.turn == 'w':
			self.turn = 'b'
			result = self.checkCheck('w')
			self.turn = 'w'
		elif self.turn == 'b':
			self.turn = 'w'
			result = self.checkCheck('b')
			self.turn = 'b'
		return result


	def getKingsPosition(self, of_which):
		for i in range(len(self.board)):
			for j in range(len(self.board[i])):
				if self.board[i][j][0] == of_which:
					if self.board[i][j][1] == 'k':
						return (i, j)
		return False
	
	def getHint(self, box, screen):
		moves = []
		piece = self.board[box[0]][box[1]]
		validMoves = self.getValidMoves()
		if piece[1] == 'p':
			self.getPawnMoves(box[0], box[1], moves, self.board)
		elif piece[1] == 'r':
			self.getRookMoves(box[0], box[1], moves, self.board)
		elif piece[1] == 'h':
			self.getKnightMoves(box[0], box[1], moves, self.board)
		elif piece[1] == 'b':
			self.getBishopMoves(box[0], box[1], moves, self.board)
		elif piece[1] == 'q':
			self.getQueenMoves(box[0], box[1], moves, self.board)
		elif piece[1] == 'k':
			self.getKingMoves(box[0], box[1], moves, self.board)
		for move in moves:
			for validMove in validMoves:
				if move == validMove:
					pygame.draw.circle(screen, RED, (move.to_box[1]*SQSIZE + SQSIZE//2, move.to_box[0]*SQSIZE + SQSIZE//2), RADIUS)

	
	def getPawnMoves(self, row, col, moves, board):
		#check for white ones
		if self.turn == 'w':
			if 0 <= row-1 <= 7 and 0 <= col <=7 and board[row-1][col] == '--':
				if row == 6:
					moves.append(Move((row,col), (row-1, col), board))
					if 0 <= row-2 <= 7 and board[row-2][col] == '--':
						moves.append(Move((row, col), (row-2, col), board))
				else:
					moves.append(Move((row,col), (row-1, col), board))
			#check for kill
			if 0 <= row-1 <= 7 and 0 <= col-1 <=7:
				if board[row-1][col-1] != '--' and board[row][col][0] != board[row-1][col-1][0]:
					moves.append(Move((row,col), (row-1, col-1), board))	
			if 0 <= row-1 <= 7 and 0 <= col+1 <=7:
				if board[row-1][col+1] != '--' and board[row][col][0] != board[row-1][col+1][0]:
					moves.append(Move((row,col), (row-1, col+1), board))
		#check for black ones
		elif self.turn == 'b':
			if  0 <= row+1 <= 7 and 0 <= col <=7 and board[row+1][col] == '--':
				if row == 1:
					moves.append(Move((row,col), (row+1, col), board))
					if 0 <= row+2 <= 7 and board[row+2][col] == '--':
						moves.append(Move((row, col), (row+2, col), board))
				else:
					moves.append(Move((row,col), (row+1, col), board))
			#check for kill
			if 0 <= row+1 <= 7 and 0 <= col-1 <=7:
				if board[row+1][col-1] != '--' and board[row][col][0] != board[row+1][col-1][0]:
					moves.append(Move((row,col), (row+1, col-1), board))	
			if 0 <= row+1 <= 7 and 0 <= col+1 <=7:
				if board[row+1][col+1] != '--' and board[row][col][0] != board[row+1][col+1][0]:
					moves.append(Move((row,col), (row+1, col+1), board))		
		
	def getRookMoves(self, row, col, moves, board):
		#check left side of rook
		count = col
		while True:
			if count == 0:
				break
			if board[row][col][0] != board[row][count-1][0] and board[row][col][0] == self.turn:
				moves.append(Move((row, col), (row, count-1), board))
			if board[row][count-1] != '--':
				break
			count -= 1
		#check right side of rook
		count = col
		while True:
			if count == 7:
				break
			if board[row][col][0] != board[row][count+1][0] and board[row][col][0] == self.turn:
				moves.append(Move((row, col), (row, count+1), board))
			if board[row][count+1] != '--':
				break
			count += 1
		#check top of rook
		count = row
		while True:
			if count == 0:
				break
			if board[row][col][0] != board[count-1][col][0] and board[row][col][0] == self.turn:
				moves.append(Move((row, col), (count-1, col), board))
			if board[count-1][col] != '--':
				break
			count -= 1
		#check bottom of rook
		count = row
		while True:
			if count == 7:
				break
			if board[row][col][0] != board[count+1][col][0] and board[row][col][0] == self.turn:
				moves.append(Move((row, col), (count+1, col), board))
			if board[count+1][col] != '--':
				break
			count += 1
		pass
	def getKnightMoves(self, row, col, moves, board):
		if 0 <= row-2 <= 7 and 0 <= col-1 <= 7 and board[row][col][0] != board[row-2][col-1][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row-2, col-1), board))
		if 0 <= row-2 <= 7 and 0 <= col+1 <= 7 and board[row][col][0] != board[row-2][col+1][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row-2, col+1), board))
		
		if 0 <= row-1 <= 7 and 0 <= col-2 <= 7 and board[row][col][0] != board[row-1][col-2][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row-1, col-2), board))
		if 0 <= row-1 <= 7 and 0 <= col+2 <= 7 and board[row][col][0] != board[row-1][col+2][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row-1, col+2), board))
		
		if 0 <= row+1 <= 7 and 0 <= col-2 <= 7 and board[row][col][0] != board[row+1][col-2][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row+1, col-2), board))
		if 0 <= row+1 <= 7 and 0 <= col+2 <= 7 and board[row][col][0] != board[row+1][col+2][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row+1, col+2), board))
		
		if 0 <= row+2 <= 7 and 0 <= col-1 <= 7 and board[row][col][0] != board[row+2][col-1][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row+2, col-1), board))
		if 0 <= row+2 <= 7 and 0 <= col+1 <= 7 and board[row][col][0] != board[row+2][col+1][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row+2, col+1), board))
		pass
	def getBishopMoves(self, row, col, moves, board):
		#check top-left
		crow = row
		ccol = col
		while True:
			if crow == 0:
				break
			if ccol == 0:
				break
			if board[row][col][0] != board[crow-1][ccol-1][0] and board[row][col][0] == self.turn:
				moves.append(Move((row, col), (crow-1, ccol-1), board))
			if board[crow-1][ccol-1] != '--':
				break
			crow -= 1
			ccol -= 1
		#check top-right
		crow = row
		ccol = col
		while True:
			if crow == 0:
				break
			if ccol == 7:
				break
			if board[row][col][0] != board[crow-1][ccol+1][0] and board[row][col][0] == self.turn:
				moves.append(Move((row, col), (crow-1, ccol+1), board))
			if board[crow-1][ccol+1] != '--':
				break
			crow -= 1
			ccol += 1
		#check bottom-left
		crow = row
		ccol = col
		while True:
			if crow == 7:
				break
			if ccol == 0:
				break
			if board[row][col][0] != board[crow+1][ccol-1][0] and board[row][col][0] == self.turn:
				moves.append(Move((row, col), (crow+1, ccol-1), board))
			if board[crow+1][ccol-1] != '--':
				break
			crow += 1
			ccol -= 1
		#check bottom-right
		crow = row
		ccol = col
		while True:
			if crow == 7:
				break
			if ccol == 7:
				break
			if board[row][col][0] != board[crow+1][ccol+1][0] and board[row][col][0] == self.turn:
				moves.append(Move((row, col), (crow+1, ccol+1), board))
			if board[crow+1][ccol+1] != '--':
				break
			crow += 1
			ccol += 1
		pass
	def getQueenMoves(self, row, col, moves, board):
		self.getRookMoves(row, col, moves, board)
		self.getBishopMoves(row, col, moves, board)
		pass
	def getKingMoves(self, row, col, moves, board):
		#check top
		if row != 0 and board[row][col][0] != board[row-1][col][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row-1, col), board))
		#check bottom
		if row != 7 and board[row][col][0] != board[row+1][col][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row+1, col), board))
		#check left
		if col != 0 and board[row][col][0] != board[row][col-1][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row, col-1), board))
		#check right
		if col != 7 and board[row][col][0] != board[row][col+1][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row, col+1), board))
		#check top-left
		if row != 0 and col != 0 and board[row][col][0] != board[row-1][col-1][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row-1, col-1), board))
		#check top-right
		if row != 0 and col != 7 and board[row][col][0] != board[row-1][col+1][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row-1, col+1), board))
		#check bottom-left
		if row != 7 and col != 0 and board[row][col][0] != board[row+1][col-1][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row+1, col-1), board))
		#check bottom-right
		if row != 7 and col != 7 and board[row][col][0] != board[row+1][col+1][0] and board[row][col][0] == self.turn:
			moves.append(Move((row, col), (row+1, col+1), board))
		pass
			

class Move():
	def __init__(self, from_box, to_box, board):
		self.from_box = from_box
		self.to_box = to_box
		self.pieceMoved = board[from_box[0]][from_box[1]]
		self.pieceCaptured = board[to_box[0]][to_box[1]]
	
	def chesslog(self):
		return (self.from_box, self.to_box, self.pieceMoved, self.pieceCaptured)
	
	def __eq__(self, other):
		if (self.from_box == other.from_box and self.to_box == other.to_box):
			return True
		return False


def loadimage(piece):
	path = 'images/'
	destination = path+piece+'.png'
	return pygame.transform.scale((pygame.image.load(destination)), (SQSIZE, SQSIZE))

def drawBoard(screen):
	colors = [WHITE, GRAY]
	for i in range(DIMENSION):
		for j in range(DIMENSION):
			color = colors[(i+j)%2]
			pygame.draw.rect(screen, color, (i*SQSIZE, j*SQSIZE, SQSIZE, SQSIZE))

def drawPieces(screen, board):
	for i in range(DIMENSION):
		for j in range(DIMENSION):
			if board[i][j] != '--':
				image = loadimage(board[i][j])
				screen.blit(image,(j*SQSIZE, i*SQSIZE))


def drawGameState(screen, gs):
	'''
	Draw background board 
	'''
	drawBoard(screen)
	#Draw pieces
	drawPieces(screen, gs.board)
	pass

########################################## MENU ###############################################
def menu(screen):
	screen.fill(GOLD)
	gameOver = False
	titlePos = [DWIDTH//2-146, DHEIGHT//10]
	playMultiplayerBoxPos = [DWIDTH//2-115 , DHEIGHT*2//3]
	playBotBoxPos = [DWIDTH//2-139 , DHEIGHT*2//3+70]
	playMultiplayerBoxSize = [230, 50]
	playBotBoxSize = [278, 50]
	while not gameOver:
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				sys.exit()
			elif e.type == pygame.MOUSEBUTTONDOWN:
				postion = pygame.mouse.get_pos()
				# print(postion)
				if playMultiplayerBoxPos[0] < postion[0] < playMultiplayerBoxPos[0]+playMultiplayerBoxSize[0]:
					if playMultiplayerBoxPos[1] < postion[1] < playMultiplayerBoxPos[1]+playMultiplayerBoxSize[1]:
						which_section = 'multiplayerChess'
						gameOver = True
						return [which_section]
				pass
			drawBoard(screen)
			
			screen.blit(pygame.image.load('images/chesspiece.png'),(titlePos[0], titlePos[1]))
			
			pygame.draw.rect(screen, RED, (playMultiplayerBoxPos[0] , playMultiplayerBoxPos[1], playMultiplayerBoxSize[0], playMultiplayerBoxSize[1]))
			font = pygame.font.SysFont("Carousel", 40)
			screen.blit(font.render('Play Multiplayer', 2, BLACK), (playMultiplayerBoxPos[0] + 10, playMultiplayerBoxPos[1] + 10))

			pygame.draw.rect(screen, RED, (playBotBoxPos[0] , playBotBoxPos[1], playBotBoxSize[0], playBotBoxSize[1]))
			font = pygame.font.SysFont("Carousel", 40)
			screen.blit(font.render('Play With Computer', 2, BLACK), (playBotBoxPos[0] + 10, playBotBoxPos[1] + 10))
			pygame.display.flip()
			
			
########################################### MULTIPLAYER CHESS ####################################
def multiplayerChess(screen):
	#initializing pygame
	screen.fill(GOLD)

	gamestate = ChessState()
	gameOver = False #flag variable to check game is on or over
	clock = pygame.time.Clock()
	firstloc = ()
	secondloc = ()
	checked = False
	checkMate = False
	validMoves = gamestate.getValidMoves() #check valid moves
	movemade = False #falg variable to check valid moves
	while not gameOver:
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				sys.exit()
			elif e.type == pygame.MOUSEBUTTONDOWN:
				postion = pygame.mouse.get_pos()
				if postion[0] < DHEIGHT and postion[1] < DWIDTH:
					col = postion[0]//SQSIZE
					row = postion[1]//SQSIZE
					if (firstloc == ()):  #first click
						firstloc = (row, col)
					elif (firstloc == (row, col)):  #if both click in same box 
						firstloc = ()
					else:                   # second click loc
						secondloc = (row, col)
					# print(firstloc, secondloc)
			elif e.type == pygame.KEYDOWN:
				if e.key == pygame.K_SPACE:
					gamestate.undoMove()
					movemade = True
				elif e.key == pygame.K_z:
					if checkMate:
						which_section = 'result'
						gameOver = True
						return [which_section, gamestate.turn]
			#check if first click is empty
			if firstloc:
				if (gamestate.board[firstloc[0]][firstloc[1]]) == '--': 
					firstloc = ()
			#check for turn
			if firstloc: 
				checkWhiteorBlack = gamestate.board[firstloc[0]][firstloc[1]] 
				# print(checkWhiteorBlack[0])
				if (checkWhiteorBlack[0] != gamestate.turn):
					firstloc = ()
			
			#game state	
			screen.fill(GOLD)
			drawGameState(screen, gamestate)

			#Give hint with dot
			if firstloc and not secondloc:
				gamestate.getHint(firstloc, screen)

			if firstloc and secondloc: #after 2nd click 
				move = Move(firstloc, secondloc, gamestate.board)
				if move in validMoves:  #check valid move
					gamestate.movePiece(move)
					movemade = True
				firstloc = secondloc =()
		
			#check if valid moves is made
			if movemade:
				validMoves = gamestate.getValidMoves()
				checked = gamestate.check()
				movemade = False
				if not validMoves:
					checkMate = True
				else:
					checkMate = False
			
		printText(gamestate.turn, screen, checked, checkMate)
		
		pygame.display.flip()
		clock.tick(FPS)

################################################# RESULT ###########################################
def result(screen, turn):
	screen.fill(GOLD)
	gameOver = False
	titlePos = [DWIDTH//2-146, DHEIGHT//10]
	winnerTxtPos = [DWIDTH//5 - 15 , DHEIGHT*2//3]
	while not gameOver:
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				sys.exit()
			if e.type == pygame.KEYDOWN:
				if e.key == pygame.K_z:
					which_section = 'menu'
					gameOver = True
					return [which_section]	
			
			drawBoard(screen)
			font = pygame.font.SysFont("Carousel", 30)
			screen.blit(font.render('Press z to continue..',2 ,RED), (5, DHEIGHT))

			screen.blit(pygame.image.load('images/chesspiece.png'),(titlePos[0], titlePos[1]))
			if turn == 'w':
				winnerTxt = "White Wins"
			else:
				winnerTxt = "Black Wins"
			font = pygame.font.SysFont("Carousel", 100)
			screen.blit(font.render(winnerTxt, 2, GOLD), (winnerTxtPos[0], winnerTxtPos[1]))
			pygame.display.flip()

if __name__  == '__main__':
	pygame.init()
	screen = pygame.display.set_mode((DWIDTH,DHEIGHT+EXTRA_DHEIGHT))
	while True:
		if which_section[0] == 'menu':
			which_section = menu(screen)
		elif which_section[0] == 'multiplayerChess':
			which_section = multiplayerChess(screen)
		elif which_section[0] == 'result':
			which_section = result(screen, which_section[1])
	