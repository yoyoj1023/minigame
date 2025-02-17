import pygame
import sys
import random

# 初始化 Pygame
pygame.init()

# 遊戲格子寬度與高度（以格數計，非像素）
GRID_WIDTH = 10
GRID_HEIGHT = 20

# 一個格子的像素邊長
BLOCK_SIZE = 30

# 遊戲螢幕大小
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# 設定顏色（RGB）
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# 方塊形狀（以 4x4 的配置表示），X 代表方塊在此處
SHAPES = [
    ["....",
     "XXXX",
     "....",
     "...."],  # I

    ["XX..",
     "XX..",
     "....",
     "...."],  # O

    ["XXX.",
     ".X..",
     "....",
     "...."],  # T

    [".XX.",
     "XX..",
     "....",
     "...."],  # S

    ["XX..",
     ".XX.",
     "....",
     "...."],  # Z

    ["XXX.",
     "X...",
     "....",
     "...."],  # J

    ["XXX.",
     "..X.",
     "....",
     "...."],  # L
]


# 將 SHAPES 轉成多種旋轉可能以方便後續呼叫
# 這裡簡化實作：遇到旋轉時，直接選擇下一個輪轉形狀
def rotate_shape(shape):
    # 形狀 shape 是一個 4 行 (strings) 的列表
    # 進行順時針旋轉
    rotated = zip(*shape[::-1])
    return ["".join(row) for row in rotated]


class Piece:
    def __init__(self, x, y, shape):
        self.x = x  # 以格子數計的 x 位置
        self.y = y  # 以格子數計的 y 位置
        self.shape = shape  # 目前的形狀（4x4）
        self.color = WHITE  # 可以再加自定義顏色

    def get_positions(self):
        # 回傳當前形狀對應在棋盤上的 (x, y) 格子位置清單
        positions = []
        for row_idx, row in enumerate(self.shape):
            for col_idx, val in enumerate(row):
                if val == "X":
                    positions.append((self.x + col_idx, self.y + row_idx))
        return positions

    def rotate(self):
        self.shape = rotate_shape(self.shape)


def create_grid(locked_positions):
    """
    建立遊戲網格，將已鎖定的方塊位置在網格中標示。
    grid[row][col] 以顏色或 None 代表該格狀態。
    """
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    for (col, row), color in locked_positions.items():
        if row >= 0:
            grid[row][col] = color
    return grid


def valid_space(piece, grid):
    # 檢查方塊是否在網格範圍內，且未與已鎖定的方塊重疊
    for x, y in piece.get_positions():
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False
        if grid[y][x] != BLACK:  # 代表該格已被填上（非空格）
            return False
    return True


def check_lost(locked_positions):
    # 如果有任何鎖定方塊超出棋盤頂部，代表遊戲結束
    for (x, y) in locked_positions:
        if y < 0:
            return True
    return False


def clear_rows(grid, locked_positions):
    """
    消除已填滿的橫行，
    並回傳消除的行數（可用於加分或難度增長）。
    """
    cleared = 0
    for row in range(GRID_HEIGHT):
        if BLACK not in grid[row]:  # 該行沒有空格，代表已滿
            cleared += 1
            # 刪除該行
            for col in range(GRID_WIDTH):
                del locked_positions[(col, row)]
            # 將更上方的行都向下移一行
            for (col, r) in sorted(list(locked_positions), key=lambda x: x[1])[::-1]:
                if r < row:
                    locked_positions[(col, r + 1)] = locked_positions.pop((col, r))
    return cleared


def draw_window(screen, grid, score=0):
    screen.fill(BLACK)
    # 繪製網格方塊
    for row_idx in range(GRID_HEIGHT):
        for col_idx in range(GRID_WIDTH):
            color = grid[row_idx][col_idx]
            pygame.draw.rect(
                screen,
                color,
                (col_idx * BLOCK_SIZE, row_idx * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                0
            )
    # 繪製格線
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(
            screen,
            GRAY,
            (x * BLOCK_SIZE, 0),
            (x * BLOCK_SIZE, SCREEN_HEIGHT)
        )
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(
            screen,
            GRAY,
            (0, y * BLOCK_SIZE),
            (SCREEN_WIDTH, y * BLOCK_SIZE)
        )
    # 顯示分數
    font = pygame.font.SysFont("Arial", 24)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

    pygame.display.update()


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("簡易俄羅斯方塊")

    locked_positions = {}  # {(x, y): color}
    grid = create_grid(locked_positions)

    current_piece = Piece(GRID_WIDTH // 2 - 2, 0, random.choice(SHAPES))
    next_piece = Piece(GRID_WIDTH // 2 - 2, 0, random.choice(SHAPES))

    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # 方塊下落速度（秒數可自行調整）
    score = 0

    run = True
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # 控制方塊下落
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                # 鎖定當前方塊
                for x, y in current_piece.get_positions():
                    locked_positions[(x, y)] = current_piece.color
                # 消除行
                cleared_rows = clear_rows(grid, locked_positions)
                if cleared_rows > 0:
                    score += cleared_rows * 100
                # 切換下一個方塊
                current_piece = next_piece
                next_piece = Piece(GRID_WIDTH // 2 - 2, 0, random.choice(SHAPES))
                # 如果遊戲結束
                if check_lost(locked_positions):
                    run = False

        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        # 旋轉後無效，轉回去
                        # 反向旋轉三次 = 順時針旋轉一次的逆操作
                        for _ in range(3):
                            current_piece.rotate()

        draw_window(screen, grid, score=score)
        # 繪製「正在下落」的方塊
        for x, y in current_piece.get_positions():
            if y >= 0:  # 在螢幕範圍內再繪圖
                pygame.draw.rect(
                    screen,
                    current_piece.color,
                    (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    0
                )
        pygame.display.update()

    # 結束畫面
    screen.fill(BLACK)
    font = pygame.font.SysFont("Arial", 48)
    text = font.render("Game Over", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                       SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.update()
    pygame.time.delay(2000)


def main_menu():
    main()


if __name__ == "__main__":
    main_menu()