import pygame
import random
import os


GRID_SIZE = 8
CELL_SIZE = 64
FPS = 60

WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE + 60

CANDY_FILES = [
    "candy_blue.png",
    "candy_red.png",
    "candy_green.png",
    "candy_yellow.png"
]


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Candy Crush Clone")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)


candies = []
for f in CANDY_FILES:
    img = pygame.image.load(os.path.join("assets", f)).convert_alpha()
    img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
    candies.append(img)

CANDY_COUNT = len(candies)


def create_board():
    board = [[random.randint(0, CANDY_COUNT - 1) for _ in range(GRID_SIZE)]
             for _ in range(GRID_SIZE)]
    return board

board = create_board()
selected = None
score = 0


def draw_board():
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            screen.blit(candies[board[r][c]], (c * CELL_SIZE, r * CELL_SIZE))
            pygame.draw.rect(screen, (0,0,0),
                             (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    if selected:
        pygame.draw.rect(
            screen, (255,255,255),
            (selected[1]*CELL_SIZE, selected[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3
        )

def draw_score():
    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10, HEIGHT-40))


def find_matches():
    matches = set()
    directions = [(1,0), (0,1), (1,1), (1,-1)]  # include diagonals

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            candy = board[r][c]
            for dr, dc in directions:
                chain = [(r,c)]
                nr, nc = r+dr, c+dc
                while 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and board[nr][nc] == candy:
                    chain.append((nr,nc))
                    nr += dr
                    nc += dc
                if len(chain) >= 3:
                    matches.update(chain)
    return matches

def remove_matches(matches):
    global score
    for r,c in matches:
        board[r][c] = None
    score += len(matches)*10


def causes_match(r, c, candy):
    directions = [(1,0), (0,1), (1,1), (1,-1)]
    for dr, dc in directions:
        count = 1
        for sign in (-1, 1):
            nr, nc = r + sign*dr, c + sign*dc
            while 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and board[nr][nc] == candy:
                count += 1
                nr += sign*dr
                nc += sign*dc
        if count >= 3:
            return True
    return False

def apply_gravity():
    for c in range(GRID_SIZE):
        # Pull existing candies down
        new_col = [board[r][c] for r in range(GRID_SIZE) if board[r][c] is not None]

        # Fill from bottom to top
        for r in range(GRID_SIZE - 1, -1, -1):
            if new_col:
                board[r][c] = new_col.pop()
            else:
                # Generate safe candy
                while True:
                    candy = random.randint(0, CANDY_COUNT-1)
                    if not causes_match(r, c, candy):
                        board[r][c] = candy
                        break


def cell_from_mouse(pos):
    x,y = pos
    if y >= GRID_SIZE*CELL_SIZE:
        return None
    return y//CELL_SIZE, x//CELL_SIZE

def swap(a,b):
    board[a[0]][a[1]], board[b[0]][b[1]] = board[b[0]][b[1]], board[a[0]][a[1]]


running = True
while running:
    screen.fill((40,40,40))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            cell = cell_from_mouse(pygame.mouse.get_pos())
            if cell:
                if not selected:
                    selected = cell
                else:
                    if abs(selected[0]-cell[0]) + abs(selected[1]-cell[1]) == 1:
                        swap(selected, cell)
                        matches = find_matches()
                        if matches:
                            while matches:
                                remove_matches(matches)
                                apply_gravity()
                                matches = find_matches()
                        else:
                            swap(selected, cell)
                    selected = None

    draw_board()
    draw_score()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
