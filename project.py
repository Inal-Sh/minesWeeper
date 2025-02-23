import pygame
import random
import sys

# Константы
WIDTH, HEIGHT = 400, 400
CELL_SIZE = 40
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
MINES = 10

# Цвета
LIGHT_BLUE = (173, 216, 230)
WHITE = (255, 255, 255)
GREEN = (60, 222, 60)
LIGHT_GREY = (211, 211, 211)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_revealed = False
        self.flagged = False
        self.neighbor_mines = 0

    def reveal(self):
        if not self.is_revealed and not self.flagged:
            self.is_revealed = True
            return not self.is_mine  # Возвращает True, если игра продолжается
        return True  # Если уже раскрыта или отмечена флагом

    def toggle_flag(self):
        if not self.is_revealed:
            self.flagged = not self.flagged

    def draw(self, screen):
        cell_rect = pygame.Rect(self.col * CELL_SIZE, self.row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        # Рисуем клетку
        if self.is_revealed:
            pygame.draw.rect(screen, LIGHT_GREY, cell_rect)
            if self.is_mine:
                pygame.draw.circle(screen, RED, cell_rect.center, CELL_SIZE // 4)
            elif self.neighbor_mines > 0:
                font = pygame.font.Font(None, 36)
                text_surface = font.render(str(self.neighbor_mines), True, BLACK)
                screen.blit(text_surface, (cell_rect.x + (CELL_SIZE - text_surface.get_width()) // 2,
                                           cell_rect.y + (CELL_SIZE - text_surface.get_height()) // 2))
        else:
            pygame.draw.rect(screen, LIGHT_BLUE, cell_rect)
            if self.flagged:
                font = pygame.font.Font(None, 36)
                text_surface = font.render('🚩', True, GREEN)
                screen.blit(text_surface, (cell_rect.x + (CELL_SIZE - text_surface.get_width()) // 2,
                                           cell_rect.y + (CELL_SIZE - text_surface.get_height()) // 2))

        # Рисуем границы клетки
        pygame.draw.rect(screen, GREEN, cell_rect, 2)


class Minesweeper:
    def __init__(self, rows=ROWS, cols=COLS, mines=MINES):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.cells = [[Cell(r, c) for c in range(cols)] for r in range(rows)]
        self.place_mines()
        self.calculate_neighbors()
        self.game_over_flag = False
        self.win_flag = False

    def place_mines(self):
        mine_positions = random.sample(range(self.rows * self.cols), self.mines)
        for pos in mine_positions:
            row = pos // self.cols
            col = pos % self.cols
            self.cells[row][col].is_mine = True

    def calculate_neighbors(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c].is_mine:
                    continue
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        neighbor_row = r + dr
                        neighbor_col = c + dc
                        if 0 <= neighbor_row < self.rows and 0 <= neighbor_col < self.cols:
                            if self.cells[neighbor_row][neighbor_col].is_mine:
                                self.cells[r][c].neighbor_mines += 1

    def reveal_cell(self, r, c):
        if not self.cells[r][c].reveal():
            self.game_over()  # Игра окончена
            return False

        if self.cells[r][c].neighbor_mines == 0:
            self.reveal_adjacent_cells(r, c)  # Раскрываем соседние клетки

        return True

    def reveal_adjacent_cells(self, x, y):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                neighbor_x = x + dr
                neighbor_y = y + dc
                if 0 <= neighbor_x < self.rows and 0 <= neighbor_y < self.cols:
                    neighbor_cell = self.cells[neighbor_x][neighbor_y]
                    if not neighbor_cell.is_revealed and not neighbor_cell.flagged:
                        if neighbor_cell.reveal() and neighbor_cell.neighbor_mines == 0:
                            # Рекурсивно раскрываем соседние клетки
                            self.reveal_adjacent_cells(neighbor_x, neighbor_y)

    def toggle_cell_flag(self, r, c):
        self.cells[r][c].toggle_flag()

    def check_win(self):
        revealed_cells = sum(cell.is_revealed for row in self.cells for cell in row)
        if revealed_cells == (self.rows * self.cols - self.mines):
            self.win_flag = True

    def game_over(self):
        self.game_over_flag = True

    def reset_game(self):
        for row in self.cells:
            for cell in row:
                cell.is_revealed = False
                cell.is_mine = False
                cell.neighbor_mines = 0
                cell.flagged = False

        self.place_mines()
        self.calculate_neighbors()
        self.game_over_flag = False
        self.win_flag = False

    def draw(self, screen):
        for row in self.cells:
            for cell in row:
                cell.draw(screen)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Сапер")
    clock = pygame.time.Clock()

    game = Minesweeper()

    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                row = mouse_pos[1] // CELL_SIZE
                col = mouse_pos[0] // CELL_SIZE

                if event.button == 1:  # ЛКМ для раскрытия клетки
                    game.reveal_cell(row, col)
                    game.check_win()
                elif event.button == 3:  # ПКМ для установки флага
                    game.toggle_cell_flag(row, col)

        game.draw(screen)

        if game.game_over_flag:
            font = pygame.font.Font(None, 48)
            text_surface = font.render("Игра окончена!", True, RED)
            screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2,
                        HEIGHT // 2 - text_surface.get_height() // 2))

        if game.win_flag:
            font = pygame.font.Font(None, 48)
            text_surface = font.render("Вы победили!", True, BLACK)
            screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2,
                        HEIGHT // 2 - text_surface.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
