import pygame
import socket
import sys
from time import sleep
import json
from threading import Thread

################################ Socket ##############################
HEADER = 64
FORMAT = 'utf-8'
PORT = 5051
#For getting machine ip address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
SERVER = s.getsockname()[0]
s.close()
ADDR = (SERVER, PORT)
DISCONNECT_MSG = "!disconnect"

MODE = ''
audiance_mode = 'audiance'

def send(msg, client):
	msg_length = len(msg)
	msg_length = str(msg_length).encode(FORMAT)
	msg_length += b' ' * (HEADER - len(msg_length))
	msg = msg.encode(FORMAT)
	client.send(msg_length)
	client.send(msg)

def recv(client):
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
    return msg

def stop_app():
	pass
######################################################################

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

def print_text(turn, screen, checked, checkMate):
	font = pygame.font.SysFont("Carousel", 30)
	if checkMate:
		screen.blit(font.render('Press z to continue..',2 ,RED), (5, DHEIGHT))
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

def local_multiplayer(screen):
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

    # #connecting to the server
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(ADDR)
    
	MODE = recv(client)
	# print(MODE)
	test = 1
	turn_test = True
	move_send = False
	
	while not gameOver:
		if MODE != audiance_mode:
			if turn_test:
				turn = recv(client)
				# print(turn)
				turn_test = False
			if turn != 'waiting':
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
							print(firstloc, secondloc)

					#check if first click is empty

					if firstloc:
						if (gamestate.board[firstloc[0]][firstloc[1]]) == '--' or turn != MODE: 
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
					if firstloc and not secondloc and turn == MODE:
						gamestate.getHint(firstloc, screen)
					
					if firstloc and secondloc: #after 2nd click
						move = Move(firstloc, secondloc, gamestate.board)
						if move in validMoves:  #check valid move
							# gamestate.movePiece(move)
							msg = {
								'firstloc': firstloc,
								'secondloc': secondloc,
								'gamestate_board': gamestate.board
							}
							msg = json.dumps(msg)
							send(msg, client)
							msg = ''
							move_send = True
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
			
				print_text(gamestate.turn, screen, checked, checkMate)
				pygame.display.flip()
				clock.tick(FPS)
				if move_send or turn != MODE:
					move_send = False
					# print('0000000000000')
					message = recv(client)
					# print('1111111111111111')
					if message:
						dict_msg = json.loads(message)
						move_server = Move(dict_msg['firstloc'], dict_msg['secondloc'], gamestate.board)
						gamestate.movePiece(move_server)
						movemade = True
						turn_test = True
						message =  ''
					#game state	
					screen.fill(GOLD)
					drawGameState(screen, gamestate)

					pygame.display.flip()
					clock.tick(FPS)

			else:
				turn_test = True
		



	# while True:
	# 	if MODE != audiance_mode:
	# 		turn = recv(client)
	# 		print(turn)
	# 		if turn != 'waiting':
	# 			if (turn == MODE):
	# 				if test == 1 and MODE == 'white':
	# 					print("Other connected")
	# 					test = 2
	# 				msg = input()
	# 				send(msg, client)
	# 			message = recv(client)
	# 			print(message)
	# 			# print('dfs')

	# 		else:
	# 			print("Waiting for other")
		
	# 	else:
	# 		turn = recv(client)
	# 		if turn:
	# 			print(turn)
	# 			turn = ''
	# 		msg = recv(client)
	# 		if msg:
	# 			print(msg)
	# 			msg = ''


if __name__ == "__main__":
	pygame.init()
	screen = pygame.display.set_mode((DWIDTH,DHEIGHT+EXTRA_DHEIGHT))
	stopapp = Thread(target=stop_app)
	stopapp.start()
	while True:
		local_multiplayer(screen)
    