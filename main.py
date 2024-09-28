# Setup
import copy
import math
import os
import random

from colorama import Fore, Style

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

pygame.mixer.init()
pygame.init()
window = pygame.display.set_mode((304, 304))
pygame.display.set_caption('Chess')

width = window.get_width()
height = window.get_height()
size = width / 8 if width < height else height / 8

move_sound = pygame.mixer.Sound('move.wav')

# Classes
class Pawn:
    def __init__(self, image, pos, dir, color):
        if image is not None:    
            self.image = pygame.transform.scale(pygame.image.load(image), (size, size))
        self.pos = pos
        self.dir = dir
        self.color = color

    def give_valids(self, board):
        valids = []
        for y in range(8):
            for x in range(8):
                if ((self.color == 'W' and self.pos[0] == 6) or (self.color == 'B' and self.pos[0] == 1)):
                    if x == self.pos[1] and y == self.pos[0] + (self.dir * 2) and board[y][x] == ' ' and board[y - self.dir][x] == ' ':
                        valids.append((y, x))
                if x == self.pos[1] and y == self.pos[0] + self.dir and board[y][x] == ' ':
                    valids.append((y, x))
                if board[y][x] != ' ' and board[y][x].color != self.color and y == self.pos[0] + self.dir and (x == self.pos[1] + 1 or x == self.pos[1] - 1):
                    valids.append((y, x))
        # Remove Moves That Put in Check
        for (y, x) in valids:
            val = board[y][x]
            sy, sx = self.pos
            board[y][x] = board[sy][sx]
            board[sy][sx] = ' '
            if in_check(board, self.color):
                valids = [i for i in valids if i != (y, x)]
            board[sy][sx] = board[y][x]
            board[y][x] = val
        return valids

    def give_attacked(self, board):
        valids = []
        for y in range(8):
            for x in range(8):
                if board[y][x] != ' ' and board[y][x].color != self.color and y == self.pos[0] + self.dir and (x == self.pos[1] + 1 or x == self.pos[1] - 1):
                    valids.append((y, x))
        return valids

    def __deepcopy__(self, memo):
        return Pawn(None, self.pos, self.dir, self.color)

class Rook:
    def __init__(self, image, pos, color):
        if image is not None:    
            self.image = pygame.transform.scale(pygame.image.load(image), (size, size))
        self.pos = pos
        self.color = color
        self.moved = False

    def give_valids(self, board):
        valids = []
        y, x = self.pos
        # Down
        for i in range(8):
            if i != 0 and y + i <= 7 and (board[y + i][x] == ' ' or board[y + i][x].color != self.color):
                valids.append((y + i, x))
            if i != 0 and y + i <= 7 and board[y + i][x] != ' ':
                break
        # Up
        for i in range(8):
            if i != 0 and y - i >= 0 and (board[y - i][x] == ' ' or board[y - i][x].color != self.color):
                valids.append((y - i, x))
            if i != 0 and y - i >= 0 and board[y - i][x] != ' ':
                break
        # Right
        for i in range(8):
            if i != 0 and x + i <= 7 and (board[y][x + i] == ' ' or board[y][x + i].color != self.color):
                valids.append((y, x + i))
            if i != 0 and x + i <= 7 and board[y][x + i] != ' ':
                break
        # Left
        for i in range(8):
            if i != 0 and x - i >= 0 and (board[y][x - i] == ' ' or board[y][x - i].color != self.color):
                valids.append((y, x - i))
            if i != 0 and x - i >= 0 and board[y][x - i] != ' ':
                break
        # Remove Moves That Put in Check
        for (y, x) in valids:
            val = board[y][x]
            sy, sx = self.pos
            board[y][x] = board[sy][sx]
            board[sy][sx] = ' '
            if in_check(board, self.color):
                valids = [i for i in valids if i != (y, x)]
            board[sy][sx] = board[y][x]
            board[y][x] = val
        return valids

    def give_attacked(self, board):
        valids = []
        y, x = self.pos
        # Down
        for i in range(8):
            if i != 0 and y + i <= 7 and (board[y + i][x] == ' ' or board[y + i][x].color != self.color):
                valids.append((y + i, x))
            if i != 0 and y + i <= 7 and board[y + i][x] != ' ':
                valids.append((y + i, x))
                break
        # Up
        for i in range(8):
            if i != 0 and y - i >= 0 and (board[y - i][x] == ' ' or board[y - i][x].color != self.color):
                valids.append((y - i, x))
            if i != 0 and y - i >= 0 and board[y - i][x] != ' ':
                valids.append((y - i, x))
                break
        # Right
        for i in range(8):
            if i != 0 and x + i <= 7 and (board[y][x + i] == ' ' or board[y][x + i].color != self.color):
                valids.append((y, x + i))
            if i != 0 and x + i <= 7 and board[y][x + i] != ' ':
                valids.append((y, x + i))
                break
        # Left
        for i in range(8):
            if i != 0 and x - i >= 0 and (board[y][x - i] == ' ' or board[y][x - i].color != self.color):
                valids.append((y, x - i))
            if i != 0 and x - i >= 0 and board[y][x - i] != ' ':
                valids.append((y, x - i))
                break
        return valids

    def __deepcopy__(self, memo):
        return Rook(None, self.pos, self.color)

class Knight:
    def __init__(self, image, pos, color):
        if image is not None:
            self.image = pygame.transform.scale(pygame.image.load(image), (size, size))
        self.pos= pos
        self.color = color

    def give_valids(self, board):
        valids = []
        yv, xv = self.pos
        for y in range(8):
            for x in range(8):
                if (board[y][x] == ' ' or board[y][x].color != self.color):
                    if (xv + 1 == x or xv - 1 == x) and (yv + 2 == y or yv - 2 == y):
                        valids.append((y, x))
                    if (yv + 1 == y or yv - 1 == y) and (xv + 2 == x or xv - 2 == x):
                        valids.append((y, x))
        # Remove Moves That Put in Check
        for (y, x) in valids:
            val = board[y][x]
            sy, sx = self.pos
            board[y][x] = board[sy][sx]
            board[sy][sx] = ' '
            if in_check(board, self.color):
                valids = [i for i in valids if i != (y, x)]
            board[sy][sx] = board[y][x]
            board[y][x] = val
        return valids

    def give_attacked(self, board):
        valids = []
        yv, xv = self.pos
        for y in range(8):
            for x in range(8):
                if (xv + 1 == x or xv - 1 == x) and (yv + 2 == y or yv - 2 == y):
                    valids.append((y, x))
                if (yv + 1 == y or yv - 1 == y) and (xv + 2 == x or xv - 2 == x):
                    valids.append((y, x))
        return valids

    def __deepcopy__(self, memo):
        return Knight(None, self.pos, self.color)

class Bishop:
    def __init__(self, image, pos, color):
        if image is not None:
            self.image = pygame.transform.scale(pygame.image.load(image), (size, size))
        self.pos = pos
        self.color = color

    def give_valids(self, board):
        valids = []
        y, x = self.pos
        # Down - Right
        for i in range(8):
            if i != 0 and y + i <= 7 and x + i <= 7 and (board[y + i][x + i] == ' ' or board[y + i][x + i].color != self.color):
                valids.append((y + i, x + i))
            if i != 0 and y + i <= 7 and x + i <= 7 and board[y + i][x + i] != ' ':
                break
        # Down - Left
        for i in range(8):
            if i != 0 and y + i <= 7 and x - i >= 0 and (board[y + i][x - i] == ' ' or board[y + i][x - i].color != self.color):
                valids.append((y + i, x - i))
            if i != 0 and y + i <= 7 and x - i <= 7 and board[y + i][x - i] != ' ':
                break
        # Up - Right
        for i in range(8):
            if i != 0 and y - i >= 0 and x + i <= 7 and (board[y - i][x + i] == ' ' or board[y - i][x + i].color != self.color):
                valids.append((y - i, x + i))
            if i != 0 and y - i >= 0 and x + i <= 7 and board[y - i][x + i] != ' ':
                break
        # Down - Left
        for i in range(8):
            if i != 0 and y - i >= 0 and x - i >= 0 and (board[y - i][x - i] == ' ' or board[y - i][x - i].color != self.color):
                valids.append((y - i, x - i))
            if i != 0 and y - i >= 0 and x - i <= 7 and board[y - i][x - i] != ' ':
                break
        # Remove Moves That Put in Check
        for (y, x) in valids:
            val = board[y][x]
            sy, sx = self.pos
            board[y][x] = board[sy][sx]
            board[sy][sx] = ' '
            if in_check(board, self.color):
                valids = [i for i in valids if i != (y, x)]
            board[sy][sx] = board[y][x]
            board[y][x] = val
        return valids

    def give_attacked(self, board):
        valids = []
        y, x = self.pos
        # Down - Right
        for i in range(8):
            if i != 0 and y + i <= 7 and x + i <= 7 and (board[y + i][x + i] == ' ' or board[y + i][x + i].color != self.color):
                valids.append((y + i, x + i))
            if i != 0 and y + i <= 7 and x + i <= 7 and board[y + i][x + i] != ' ':
                valids.append((y + i, x + i))
                break
        # Down - Left
        for i in range(8):
            if i != 0 and y + i <= 7 and x - i >= 0 and (board[y + i][x - i] == ' ' or board[y + i][x - i].color != self.color):
                valids.append((y + i, x - i))
            if i != 0 and y + i <= 7 and x - i <= 7 and board[y + i][x - i] != ' ':
                valids.append((y + i, x - i))
                break
        # Up - Right
        for i in range(8):
            if i != 0 and y - i >= 0 and x + i <= 7 and (board[y - i][x + i] == ' ' or board[y - i][x + i].color != self.color):
                valids.append((y - i, x + i))
            if i != 0 and y - i >= 0 and x + i <= 7 and board[y - i][x + i] != ' ':
                valids.append((y - i, x + i))
                break
        # Down - Left
        for i in range(8):
            if i != 0 and y - i >= 0 and x - i >= 0 and (board[y - i][x - i] == ' ' or board[y - i][x - i].color != self.color):
                valids.append((y - i, x - i))
            if i != 0 and y - i >= 0 and x - i <= 7 and board[y - i][x - i] != ' ':
                valids.append((y - i, x - i))
                break
        return valids

    def __deepcopy__(self, memo):
        return Bishop(None, self.pos, self.color)

class Queen:
    def __init__(self, image, pos, color):
        if image is not None:
            self.image = pygame.transform.scale(pygame.image.load(image), (size, size))
        self.pos = pos
        self.color = color

    def give_valids(self, board):
        valids = []
        y, x = self.pos
        # Down
        for i in range(8):
            if i != 0 and y + i <= 7 and (board[y + i][x] == ' ' or board[y + i][x].color != self.color):
                valids.append((y + i, x))
            if i != 0 and y + i <= 7 and board[y + i][x] != ' ':
                break
        # Up
        for i in range(8):
            if i != 0 and y - i >= 0 and (board[y - i][x] == ' ' or board[y - i][x].color != self.color):
                valids.append((y - i, x))
            if i != 0 and y - i >= 0 and board[y - i][x] != ' ':
                break
        # Right
        for i in range(8):
            if i != 0 and x + i <= 7 and (board[y][x + i] == ' ' or board[y][x + i].color != self.color):
                valids.append((y, x + i))
            if i != 0 and x + i <= 7 and board[y][x + i] != ' ':
                break
        # Left
        for i in range(8):
            if i != 0 and x - i >= 0 and (board[y][x - i] == ' ' or board[y][x - i].color != self.color):
                valids.append((y, x - i))
            if i != 0 and x - i >= 0 and board[y][x - i] != ' ':
                break
        # Down - Right
        for i in range(8):
            if i != 0 and y + i <= 7 and x + i <= 7 and (board[y + i][x + i] == ' ' or board[y + i][x + i].color != self.color):
                valids.append((y + i, x + i))
            if i != 0 and y + i <= 7 and x + i <= 7 and board[y + i][x + i] != ' ':
                break
        # Down - Left
        for i in range(8):
            if i != 0 and y + i <= 7 and x - i >= 0 and (board[y + i][x - i] == ' ' or board[y + i][x - i].color != self.color):
                valids.append((y + i, x - i))
            if i != 0 and y + i <= 7 and x - i <= 7 and board[y + i][x - i] != ' ':
                break
        # Up - Right
        for i in range(8):
            if i != 0 and y - i >= 0 and x + i <= 7 and (board[y - i][x + i] == ' ' or board[y - i][x + i].color != self.color):
                valids.append((y - i, x + i))
            if i != 0 and y - i >= 0 and x + i <= 7 and board[y - i][x + i] != ' ':
                break
        # Down - Left
        for i in range(8):
            if i != 0 and y - i >= 0 and x - i >= 0 and (board[y - i][x - i] == ' ' or board[y - i][x - i].color != self.color):
                valids.append((y - i, x - i))
            if i != 0 and y - i >= 0 and x - i <= 7 and board[y - i][x - i] != ' ':
                break
        # Remove Moves That Put in Check
        for (y, x) in valids:
            val = board[y][x]
            sy, sx = self.pos
            board[y][x] = board[sy][sx]
            board[sy][sx] = ' '
            if in_check(board, self.color):
                valids = [i for i in valids if i != (y, x)]
            board[sy][sx] = board[y][x]
            board[y][x] = val
        return valids

    def give_attacked(self, board):
        valids = []
        y, x = self.pos
        # Down
        for i in range(8):
            if i != 0 and y + i <= 7 and (board[y + i][x] == ' ' or board[y + i][x].color != self.color):
                valids.append((y + i, x))
            if i != 0 and y + i <= 7 and board[y + i][x] != ' ':
                valids.append((y + i, x))
                break
        # Up
        for i in range(8):
            if i != 0 and y - i >= 0 and (board[y - i][x] == ' ' or board[y - i][x].color != self.color):
                valids.append((y - i, x))
            if i != 0 and y - i >= 0 and board[y - i][x] != ' ':
                valids.append((y - i, x))
                break
        # Right
        for i in range(8):
            if i != 0 and x + i <= 7 and (board[y][x + i] == ' ' or board[y][x + i].color != self.color):
                valids.append((y, x + i))
            if i != 0 and x + i <= 7 and board[y][x + i] != ' ':
                valids.append((y, x + i))
                break
        # Left
        for i in range(8):
            if i != 0 and x - i >= 0 and (board[y][x - i] == ' ' or board[y][x - i].color != self.color):
                valids.append((y, x - i))
            if i != 0 and x - i >= 0 and board[y][x - i] != ' ':
                valids.append((y, x - i))
                break
        # Down - Right
        for i in range(8):
            if i != 0 and y + i <= 7 and x + i <= 7 and (board[y + i][x + i] == ' ' or board[y + i][x + i].color != self.color):
                valids.append((y + i, x + i))
            if i != 0 and y + i <= 7 and x + i <= 7 and board[y + i][x + i] != ' ':
                valids.append((y + i, x + i))
                break
        # Down - Left
        for i in range(8):
            if i != 0 and y + i <= 7 and x - i >= 0 and (board[y + i][x - i] == ' ' or board[y + i][x - i].color != self.color):
                valids.append((y + i, x - i))
            if i != 0 and y + i <= 7 and x - i <= 7 and board[y + i][x - i] != ' ':
                valids.append((y + i, x - i))
                break
        # Up - Right
        for i in range(8):
            if i != 0 and y - i >= 0 and x + i <= 7 and (board[y - i][x + i] == ' ' or board[y - i][x + i].color != self.color):
                valids.append((y - i, x + i))
            if i != 0 and y - i >= 0 and x + i <= 7 and board[y - i][x + i] != ' ':
                valids.append((y - i, x + i))
                break
        # Down - Left
        for i in range(8):
            if i != 0 and y - i >= 0 and x - i >= 0 and (board[y - i][x - i] == ' ' or board[y - i][x - i].color != self.color):
                valids.append((y - i, x - i))
            if i != 0 and y - i >= 0 and x - i <= 7 and board[y - i][x - i] != ' ':
                valids.append((y - i, x - i))
                break
        return valids

    def __deepcopy__(self, memo):
        return Queen(None, self.pos, self.color)

class King:
    def __init__(self, image, pos, color):
        if image is not None:
            self.image = pygame.transform.scale(pygame.image.load(image), (size, size))
        self.pos = pos
        self.color = color
        self.moved = False
        self.castled = False

    def give_valids(self, board):
        valids = []
        sy, sx = self.pos
        for y in range(8):
            for x in range(8):
                if board[y][x] == ' ' or board[y][x].color != self.color and (y, x) not in get_attacked(board, colors[1 - colors.index(self.color)]):
                    if ((sx + 1 == x or sx - 1 == x) and sy == y) or ((sy + 1 == y or sy - 1 == y) and sx == x):
                        valids.append((y, x))
                    if (sx + 1 == x or sx - 1 == x) and (sy + 1 == y or sy - 1 == y):
                        valids.append((y, x))
        # Castling
        if self.color == 'W':
            if can_castle(board, self, WR1, 'W'):
                valids.append((7, 2))
            if can_castle(board, self, WR2, 'W'):
                valids.append((7, 6))
        elif self.color == 'B':
            if can_castle(board, self, BR1, 'B'):
                valids.append((0, 2))
            if can_castle(board, self, BR2, 'B'):
                valids.append((0, 6))
        # Remove Moves That Put in Check
        for (y, x) in valids:
            val = board[y][x]
            sy, sx = self.pos
            board[y][x] = board[sy][sx]
            board[sy][sx] = ' '
            board[y][x].pos = (y, x)
            if in_check(board, self.color):
                valids = [i for i in valids if i != (y, x)]
            board[sy][sx] = board[y][x]
            board[y][x] = val
            board[sy][sx].pos = (sy, sx)
        return valids

    def give_attacked(self, board):
        valids = []
        sy, sx = self.pos
        for y in range(8):
            for x in range(8):
                if ((sx + 1 == x or sx - 1 == x) and sy == y) or ((sy + 1 == y or sy - 1 == y) and sx == x):
                    valids.append((y, x))
                if (sx + 1 == x or sx - 1 == x) and (sy + 1 == y or sy - 1 == y):
                    valids.append((y, x))
        return valids

    def __deepcopy__(self, memo):
        return King(None, self.pos, self.color)

class Marker:
    def __init__(self, image, pos):
        self.image = image
        self.pos = pos

# Functions
def draw_board():
    for y in range(8):
        for x in range(8):
            if (y, x) == hover:    
                pygame.draw.rect(window, (242, 239, 73), (x * size, y * size, size, size))
            elif (y, x) in possibles:
                if (y + x) % 2 == 0:
                    pygame.draw.rect(window, (200, 238, 255), (x * size, y * size, size, size))
                else:
                    pygame.draw.rect(window, (115, 211, 255), (x * size, y * size, size, size))
            elif (in_check(board, 'W') and (y, x) == WK.pos) or (in_check(board, 'B') and (y, x) == BK.pos):
                pygame.draw.rect(window, (255, 79, 104), (x * size, y * size, size, size))
            else:
                pygame.draw.rect(window, boardColors[(y + x) % 2], (x * size, y * size, size, size))

def draw_pieces():
    pieces.clear()
    piecesClass.clear()
    for y in range(8):
        for x in range(8):
            if board[y][x] != ' ':    
                piece = window.blit(board[y][x].image, (x * size, y * size))
                pieceClass = board[y][x]
                pieces.append(piece)
                piecesClass.append(pieceClass)

def draw_markers():
    markers.clear()
    if hover != ('_', '_') and board[hover[0]][hover[1]] != ' ':   
        valids = board[hover[0]][hover[1]].give_valids(board)
        possibles.clear()
        for (y, x) in valids:
            center_x = x * size + (size / 2)
            center_y = y * size + (size / 2)
            if (y + x) % 2 == 0:
                marker = Marker(pygame.draw.circle(window, (200, 238, 255), (center_x, center_y), width / 16), (y, x))
            else:
                marker = Marker(pygame.draw.circle(window, (115, 211, 255), (center_x, center_y), width / 16), (y, x))
            position = (y, x)
            possibles.append(position)
            markers.append((marker, position))

def event():
    global hover, turn, turnTotal
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Piece Click
            if (player1 and turn == 0) or (player2 and turn == 1):
                for piece in pieces:
                    if piece.collidepoint(pygame.mouse.get_pos()) and piecesClass[pieces.index(piece)].color == colors[turn]:
                        hover = piecesClass[pieces.index(piece)].pos
                        break
            # Marker Click
            for marker, position in markers:
                if marker.image.collidepoint(pygame.mouse.get_pos()) and hover != ('_', '_'):
                    ey, ex = position
                    sy, sx = hover
                    if isinstance(board[sy][sx], King) and abs(ex - sx) > 1:
                        board[sy][sx].castled = True
                        if board[sy][sx].color == 'W':
                            if (ey, ex) == (7, 2):
                                make_move(board, 0, 7, 3, 7)
                                board[7][3].moved = True
                            elif (ey, ex) == (7, 6):
                                make_move(board, 7, 7, 5, 7)
                                board[7][5].moved = True
                        elif board[sy][sx].color == 'B':
                            if (ey, ex) == (0, 2):
                                make_move(board, 0, 0, 3, 0)
                                board[0][3].moved = True
                            elif (ey, ex) == (0, 6):
                                make_move(board, 7, 0, 5, 0)
                                board[0][5].moved = True
                    # Print Eval and move name
                    temp = copy.deepcopy(board)
                    make_move(temp, sx, sy, ex, ey)
                    if isinstance(board[ey][ex], King) or isinstance(board[ey][ex], Rook):
                        board[ey][ex].moved = True
                    score = eval(temp, temp[ey][ex].color)
                    os.system('clear')
                    aiMoves.append(f'{type(board[sy][sx]).__name__} to {letters[ex]}{8 - ey}, Eval: {score}')
                    counter = 0
                    for item in aiMoves:
                        if counter % 2 == 0:    
                            print(Fore.WHITE + item)
                        else:
                            print(Fore.LIGHTBLACK_EX + item)
                        counter += 1
                    # Update
                    moveLog.append(make_algebraic(sx, sy, ex, ey))
                    make_move(board, sx, sy, ex, ey)
                    possibles.clear()
                    move_sound.play()
                    if isinstance(board[ey][ex], King) or isinstance(board[ey][ex], Rook):
                        board[ey][ex].moved = True
                    hover = ('_', '_')
                    boardLog.append(store_data(board))
                    turn = 1 - turn
                    turnTotal += 1
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f and len(boardLog) > 0:
                os.system('clear')
                print(boardLog[len(boardLog) - 1])
            elif event.key == pygame.K_m:
                os.system('clear')
                counter = 1
                for item in moveLog:
                    if counter % 2 == 1:    
                        print(Fore.WHITE + str(math.ceil(counter / 2)) + '.' + item, end = ' ')
                    else:
                        print(Fore.LIGHTBLACK_EX + item, end = ' ')
                    counter += 1
                print(Style.RESET_ALL)
            elif event.key == pygame.K_a:
                os.system('clear')
                counter = 0
                for item in aiMoves:
                    if counter % 2 == 0:    
                        print(Fore.WHITE + item)
                    else:
                        print(Fore.LIGHTBLACK_EX + item)
                    counter += 1
            elif event.key == pygame.K_q:
                os.system('clear')
                fen = input('Enter the FEN board: ')
                t = input('Enter whose turn as W or B: ')
                edit_board(fen)
                if t == 'W':
                    turn = 0
                elif t == 'B':
                    turn = 1
                os.system('clear')

def get_attacked(board, color):
    # Fills all squares that (color) is attacking
    attacked = []
    for y in range(8):
        for x in range(8):
            if board[y][x] != ' ' and board[y][x].color == color:
                attacked = attacked + board[y][x].give_attacked(board)
    return attacked

def get_valids(board, color):
    valids = []
    for y in range(8):
        for x in range(8):
            if board[y][x] != ' ' and board[y][x].color == color:
                for move in board[y][x].give_valids(board):
                    valids.append(((y, x), move))
    return valids

def make_move(board, sx, sy, ex, ey):
    if board[sy][sx] != ' ':    
        board[ey][ex] = board[sy][sx]
        board[sy][sx] = ' '
        board[ey][ex].pos = (ey, ex)
        return board

def can_castle(board, king, rook, color):
    if color == 'W' and king.pos == (7, 4) and (not in_check(board, 'W')) and (not king.moved):
            return (rook.pos == (7, 0) and (board[7][1] == ' ' and (7, 1) not in get_attacked(board, colors[1 - colors.index(color)])) and (board[7][2] == ' ' and (7, 2) not in get_attacked(board, colors[1 - colors.index(color)])) and (board[7][3] == ' ' and (7, 3) not in get_attacked(board, colors[1 - colors.index(color)])) and (not rook.moved)) or (rook.pos == (7, 7) and (board[7][5] == ' ' and (7, 5) not in get_attacked(board, colors[1 - colors.index(color)])) and (board[7][6] == ' ' and (7, 6) not in get_attacked(board, colors[1 - colors.index(color)])) and (not rook.moved))
    elif color == 'B' and king.pos == (0, 4) and (not in_check(board, 'B')) and (not king.moved):
        return (rook.pos == (0, 0) and (board[0][1] == ' ' and (0, 1) not in get_attacked(board, colors[1 - colors.index(color)])) and (board[0][2] == ' ' and (0, 2) not in get_attacked(board, colors[1 - colors.index(color)])) and (board[0][3] == ' ' and (0, 3) not in get_attacked(board, colors[1 - colors.index(color)])) and (not rook.moved)) or (rook.pos == (0, 7) and (board[0][5] == ' ' and (0, 5) not in get_attacked(board, colors[1 - colors.index(color)])) and (board[0][6] == ' ' and (0, 6) not in get_attacked(board, colors[1 - colors.index(color)])) and (not rook.moved))
    else:
        return False
        

def in_check(board, color):
    attacked = get_attacked(board, colors[1 - colors.index(color)])
    return (color == 'W' and WK.pos in attacked) or (color == 'B' and BK.pos in attacked)

def in_checkmate(board, color):
    # For some reason, returns True when the king has no valid moves, but other pieces do.
    return in_check(board, color) and len(get_valids(board, color)) == 0

def in_stalemate(board, color):
    attacked = get_attacked(board, colors[1 - colors.index(color)])
    return (color == 'W' and WK.pos not in attacked and len(get_valids(board, color)) == 0) or (color == 'B' and BK.pos not in attacked and len(get_valids(board, color)) == 0)

def insufficient(board):
    # Check for a queen, a rook, two bishops, or a bishop and knight
    pass

def piece_score(type, color, y, x):
    corr = {Pawn: pawn, Bishop: bishop, Knight: knight, Rook: rook, Queen: queen, King: king}
    if corr[type] is not None:    
        if color == 'B':
            return corr[type][y][x]
        else:
            reversed_array = list(reversed(corr[type]))
            return reversed_array[y][x]
    else:
        return 0

def promote(board):
    for y in range(8):
        for x in range(8):
            if board[y][x] != ' ' and isinstance(board[y][x], Pawn) and (y == 0 or y == 7):
                if board[y][x].color == 'W':
                    board[y][x] = Queen('Pieces/WQ.png', (y, x), 'W')
                    return True
                else:
                    board[y][x] = Queen('Pieces/BQ.png', (y, x), 'B')
                    return True
    return False

def inverse(board):
    for y in range(8):
        for x in range(8):
            if board[y][x] != ' ':
                board[y][x].color = colors[1 - colors.index(board[y][x].color)]

    return board

def make_random(color):
    all = get_valids(board, color)
    if len(all) != 0:    
        moveset = all[random.randrange(0, len(all))]
        sy, sx = moveset[0]
        ey, ex = moveset[1]
        make_move(board, sx, sy, ex, ey)

def make_best(color):
    global total
    if not in_checkmate(board, color) and not in_stalemate(board, color):
        total = 0 
        sTime = pygame.time.get_ticks()
        score, move = AI(board, color, 1, DEPTH, -float('inf'), float('inf'))
        eTime = pygame.time.get_ticks()
        speed = round((eTime - sTime) / 1000, 2)
        sy, sx = move[0]
        ey, ex = move[1]
        os.system('clear')
        aiMoves.append(f'{type(board[sy][sx]).__name__} to {letters[ex]}{8 - ey}, Eval: {score}, TC: {total}, Time: {speed}')
        counter = 0
        for item in aiMoves:
            if counter % 2 == 0:    
                print(Fore.WHITE + item)
            else:
                print(Fore.LIGHTBLACK_EX + item)
            counter += 1
        moveLog.append(make_algebraic(sx, sy, ex, ey))
        make_move(board, sx, sy, ex, ey)
        move_sound.play()
        boardLog.append(store_data(board))

def AI(board, color, mod, depth, alpha, beta):
    global transTable, total
    # Check transposition table
    boardHash = hash_board(board)
    if boardHash in transTable:
        stored_score, stored_move, stored_depth = transTable[boardHash]
        if stored_depth >= depth:
            return stored_score, stored_move

    inversedBoard = inverse(hash_board(copy.deepcopy(board)))
    if inversedBoard in transTable:
        stored_score, stored_move, stored_depth = transTable[inversedBoard]
        if stored_depth >= depth:
            return stored_score, stored_move
    # Check Terminal Cases
    if in_checkmate(board, color):
        return -500 * mod, None
    elif in_checkmate(board, colors[1 - colors.index(color)]):
        return 500 * mod, None
    elif in_stalemate(board, color):
        return 0, None
    total += 1
    # Check Depth Limit
    if depth <= 0:
        return eval(board, color) * mod, None
    # Setup
    valids = order_moves(board, get_valids(board, color), color)
    best_score = -float('inf') if mod == 1 else float('inf')
    best_move = None
    # Recursive AI
    temp = copy.deepcopy(board)
    for ((sy, sx), (ey, ex)) in valids:
        value = temp[ey][ex]
        startValue = temp[sy][sx]
        make_move(temp, sx, sy, ex, ey)
        score, move = AI(temp, colors[1 - colors.index(color)], -mod, depth - 1, alpha, beta)
        promoted = promote(temp)
        # Calculate if best
        if (mod == 1 and score > best_score) or (mod == -1 and score < best_score):
            best_score = score
            best_move = ((sy, sx), (ey, ex))
        # Alpha Beta Update
        if mod == 1:
            alpha = max(alpha, best_score)
        elif mod == -1:
            beta = min(beta, best_score)
        if alpha >= beta:
            # Undo Move
            make_move(temp, ex, ey, sx, sy)
            temp[ey][ex] = value
            if promoted:
                temp[sy][sx] = startValue
            transTable[boardHash] = (best_score, best_move, depth)
            # Return
            del(temp)
            return best_score, best_move
        # Undo Move
        make_move(temp, ex, ey, sx, sy)
        temp[ey][ex] = value
        if promoted:
            temp[sy][sx] = startValue
    # Return
    transTable[boardHash] = (best_score, best_move, depth)
    del(temp)
    return best_score, best_move

def hash_board(board):
    return tuple(tuple(row) for row in board)

def order_moves(board, list, color):
    rlist = []
    for move in list:
        (sy, sx), (ey, ex) = move
        # Is a capture
        if board[ey][ex] != ' ':
            rlist.append(move)
        # Moves an attacked piece
        if (sy, sx) in get_attacked(board, colors[1 - colors.index(color)]):
            rlist.append(move)
        # Is a pawn promote
        if isinstance(board[sy][sx], Pawn) and (ey == 0 or ey == 7):
            rlist.append(move)
    # Adds remaining
    for move in list:
        if move not in rlist:
            rlist.append(move)
    # Return
    return rlist

def eval(board, color):
    global turnTotal
    scores = {Pawn: 20, Bishop: 70, Knight: 60, Rook: 100, Queen: 180, King: 2000}
    points = 0
    promote(board)
    # Score
    for y in range(8):
        for x in range(8):
            # Score Material
            if board[y][x] != ' ':
                if board[y][x].color == color:
                    points += scores.get(type(board[y][x]), 0)
                    points += piece_score(type(board[y][x]), color, y, x) / 12
                else:
                    points -= scores.get(type(board[y][x]), 0)
                    points -= piece_score(type(board[y][x]), color, y, x) / 15
    # Can Castle
    if color == 'W':
        if can_castle(board, WK, WR1, 'W'):
            points += 7
        if can_castle(board, WK, WR2, 'W'):
            points += 7
        if can_castle(board, BK, BR1, 'B'):
            points -= 7
        if can_castle(board, BK, BR2, 'B'):
            points -= 7
        if WK.castled:
            points += 30
        if BK.castled:
            points -= 30
    elif color == 'B':
        if can_castle(board, WK, WR1, 'W'):
            points -= 7
        if can_castle(board, WK, WR2, 'W'):
            points -= 7
        if can_castle(board, BK, BR1, 'B'):
            points += 7
        if can_castle(board, BK, BR2, 'B'):
            points += 7
        if WK.castled:
            points -= 30
        if BK.castled:
            points += 30
    # Return
    return round(points, 2)

def store_data(board):
    # Compress to str of FEN Notation
    names = {Pawn: 'p', Bishop: 'b', Knight: 'n', Rook: 'r', Queen: 'q', King: 'k'}
    FEN = ''
    for y in range(8):
        for x in range(8):
            if board[y][x] == ' ':
                FEN = FEN + '_'
            elif board[y][x].color == 'W':
                FEN = FEN + names.get(type(board[y][x]), '_').upper()
            else:
                FEN = FEN + names.get(type(board[y][x]), '_')
        if y != 7:
            FEN = FEN + '/'
    return FEN

def convert_num(board):
    colors = {'W': 2, 'B': 1, ' ': 0}
    pieces = {Pawn: 1100, Knight: 1001, Bishop: 1011, Rook: 1101, Queen: 1110, King: 1111, str: 1000}
    bitboard = ''
    for y in range(8):
        for x in range(8):
            if board[y][x] != ' ':
                bitboard = int(str(bitboard) + str(colors[board[y][x].color]) + str(pieces[type(board[y][x])]))
            else:
                bitboard = int(str(bitboard) + '0' + str(pieces[type(board[y][x])]))
    return bitboard

def make_algebraic(sx, sy, ex, ey):
    names = {Pawn: '', Bishop: 'B', Knight: 'N', Rook: 'R', Queen: 'Q', King: 'K'}
    temp = copy.deepcopy(board)
    make_move(temp, sx, sy, ex, ey)
    if isinstance(board[sy][sx], King) and abs(ex - sx) > 1:
        if ex == 6:
            return 'O-O'
        elif ex == 2:
            return 'O-O-O'
    fin = ''
    if in_checkmate(temp, colors[1 - turn]):
        fin = '#'
    elif in_check(temp, colors[1 - turn]):
        fin = '+'
    if board[ey][ex] == ' ':
        return names.get(type(board[sy][sx])) + letters[ex] + str(8 - ey) + fin
    else:
        if type(board[sy][sx]) != Pawn:
            return names.get(type(board[sy][sx]), '') + 'x' + letters[ex] + str(8 - ey) + fin
        else:
            return letters[sx] + 'x' + letters[ex] + str(8 - ey) + fin

def edit_board(FEN):
    global board, WK, BK
    board.clear()
    FEN.replace('/', '')
    for r in range(8):
        board.append([])
        for c in range(8):
            if FEN[(r * 8) + c] == '_':
                board[r].append(' ')
            elif FEN[(r * 8) + c].upper() == 'P':
                letters = ['P', 'p']
                ps = [Pawn('Pieces/WP.png', (r, c), -1, 'W'), Pawn('Pieces/BP.png', (r, c), 1, 'B')]
                board[r].append(ps[letters.index(FEN[(r * 8) + c])])
            elif FEN[(r * 8) + c].upper() == 'R':
                letters = ['R', 'r']
                ps = [Rook('Pieces/WR.png', (r, c), 'W'), Rook('Pieces/BR.png', (r, c), 'B')]
                board[r].append(ps[letters.index(FEN[(r * 8) + c])])
            elif FEN[(r * 8) + c].upper() == 'B':
                letters = ['B', 'b']
                ps = [Bishop('Pieces/WB.png', (r, c), 'W'), Bishop('Pieces/BB.png', (r, c), 'B')]
                board[r].append(ps[letters.index(FEN[(r * 8) + c])])
            elif FEN[(r * 8) + c].upper() == 'N':
                letters = ['N', 'n']
                ps = [Knight('Pieces/WN.png', (r, c), 'W'), Knight('Pieces/BN.png', (r, c), 'B')]
                board[r].append(ps[letters.index(FEN[(r * 8) + c])])
            elif FEN[(r * 8) + c].upper() == 'Q':
                letters = ['Q', 'q']
                ps = [Queen('Pieces/WQ.png', (r, c), 'W'), Queen('Pieces/BQ.png', (r, c), 'B')]
                board[r].append(ps[letters.index(FEN[(r * 8) + c])])
            elif FEN[(r * 8) + c].upper() == 'K':
                if FEN[(r * 8) + c] == 'K':
                    WK = King('Pieces/WK.png', (r, c), 'W')
                    board[r].append(WK)
                else:
                    BK = King('Pieces/BK.png', (r, c), 'B')
                    board[r].append(BK)
            
# On start
WP1 = Pawn('Pieces/WP.png', (6, 0), -1, 'W')
WP2 = Pawn('Pieces/WP.png', (6, 1), -1, 'W')
WP3 = Pawn('Pieces/WP.png', (6, 2), -1, 'W')
WP4 = Pawn('Pieces/WP.png', (6, 3), -1, 'W')
WP5 = Pawn('Pieces/WP.png', (6, 4), -1, 'W')
WP6 = Pawn('Pieces/WP.png', (6, 5), -1, 'W')
WP7 = Pawn('Pieces/WP.png', (6, 6), -1, 'W')
WP8 = Pawn('Pieces/WP.png', (6, 7), -1, 'W')
WR1 = Rook('Pieces/WR.png', (7, 0), 'W')
WR2 = Rook('Pieces/WR.png', (7, 7), 'W')
WN1 = Knight('Pieces/WN.png', (7, 1), 'W')
WN2 = Knight('Pieces/WN.png', (7, 6), 'W')
WB1 = Bishop('Pieces/WB.png', (7, 2), 'W')
WB2 = Bishop('Pieces/WB.png', (7, 5), 'W')
WQ = Queen('Pieces/WQ.png', (7, 3), 'W')
WK = King('Pieces/WK.png', (7, 4), 'W')
BP1 = Pawn('Pieces/BP.png', (1, 0), 1, 'B')
BP2 = Pawn('Pieces/BP.png', (1, 1), 1, 'B')
BP3 = Pawn('Pieces/BP.png', (1, 2), 1, 'B')
BP4 = Pawn('Pieces/BP.png', (1, 3), 1, 'B')
BP5 = Pawn('Pieces/BP.png', (1, 4), 1, 'B')
BP6 = Pawn('Pieces/BP.png', (1, 5), 1, 'B')
BP7 = Pawn('Pieces/BP.png', (1, 6), 1, 'B')
BP8 = Pawn('Pieces/BP.png', (1, 7), 1, 'B')
BR1 = Rook('Pieces/BR.png', (0, 0), 'B')
BR2 = Rook('Pieces/BR.png', (0, 7), 'B')
BN1 = Knight('Pieces/BN.png', (0, 1), 'B')
BN2 = Knight('Pieces/BN.png', (0, 6), 'B')
BB1 = Bishop('Pieces/BB.png', (0, 2), 'B')
BB2 = Bishop('Pieces/BB.png', (0, 5), 'B')
BQ = Queen('Pieces/BQ.png', (0, 3), 'B')
BK = King('Pieces/BK.png', (0, 4), 'B')

board = [
    [BR1, BN1, BB1, BQ, BK, BB2, BN2, BR2],
    [BP1, BP2, BP3, BP4, BP5, BP6, BP7, BP8],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [WP1, WP2, WP3, WP4, WP5, WP6, WP7, WP8],
    [WR1, WN1, WB1, WQ, WK, WB2, WN2, WR2]
]

# White's Perspective
pawn =  [
    [ 0,  0,  0,    0,   0,   0,  0,  0],
    [50, 50, 50,   50,  50,  50, 50, 50],
    [10, 10, 20,   45,  45,  20, 10, 10],
    [ 5,  5, 10,   40,  40,  10,  5,  5],
    [ 0,  0,  0,   30,  30, -40,  0,  0],
    [ 5, -5, 0,   0,   0, -40, -5,  5],
    [ 5, 10,  10, -45, -45,  10, 10,  5],
    [ 0,  0,  0,    0,   0,   0,  0,  0]
]

knight =  [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20,   0,   0,   0,   0, -20, -40],
    [-30,   0,  10,  15,  15,  10,   0, -30],
    [-30,   5,  15,  20,  20,  15,   5, -30],
    [-30,   0,  15,  20,  20,  15,   0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, 0, -30, -30, -30, -30, 0, -50]
]

bishop =  [
    [-20, -10, -10, -10, -10 ,-10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]

rook =  [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [5, 0, 0, 5, 5, 0, 0, 5]
]

queen =  [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]

king =  [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20]
]

player1 = True
player2 = False

turn = 0
turnTotal = 0

boardColors = [(255, 230, 195), (138, 88, 0)]

hover = ('_', '_')

pieces = []
piecesClass = []

markers = []

colors = ['W', 'B']

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

cAttacked = []

boardLog = []
moveLog = []
aiMoves = []

possibles = []

transTable = {}
running = True

DEPTH = 3

boardLog.append(store_data(board))

while running:
    # Possibles Reset
    if hover == ('_', '_'):
        possibles.clear()
    # Draw Board
    window.fill((0, 0, 0))
    draw_board()
    draw_markers()
    draw_pieces()
    pygame.display.update()
    # AI makes move
    if (turn == 0 and not player1) or (turn == 1 and not player2) and not in_checkmate(board, colors[turn]) and not in_stalemate(board, colors[turn]):
        make_best(colors[turn])
        turn = 1 - turn
        turnTotal += 1
    promote(board)
    # Handle Events
    event()
    promote(board)
    window.fill((0, 0, 0))
    draw_board()
    draw_markers()
    draw_pieces()
    pygame.display.update()
    # Check Terminal Cases
    for i in range(2):
        if in_checkmate(board, colors[i]):
            running = False
        if in_stalemate(board, colors[i]):
            running = False

while True:
    pygame.display.update()
    for even in pygame.event.get():
        if even.type == pygame.KEYDOWN:
            if even.key == pygame.K_f and len(boardLog) > 0:
                os.system('clear')
                print(boardLog[len(boardLog) - 1])
            elif even.key == pygame.K_m:
                os.system('clear')
                counter = 1
                for item in moveLog:
                    if counter % 2 == 1:    
                        print(Fore.WHITE + str(math.ceil(counter / 2)) + '.' + item, end = ' ')
                    else:
                        print(Fore.LIGHTBLACK_EX + item, end = ' ')
                    counter += 1
                print(Style.RESET_ALL)
            elif even.key == pygame.K_a:
                os.system('clear')
                counter = 0
                for item in aiMoves:
                    if counter % 2 == 0:    
                        print(Fore.WHITE + item)
                    else:
                        print(Fore.LIGHTBLACK_EX + item)
                    counter += 1
