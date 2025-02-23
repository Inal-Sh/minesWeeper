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
LIGHT_GREY = (211, 211, 211)
BLACK = (0, 0, 0)


class Cell(pygame.sprite.Sprite):
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_revealed = False
        self.flagged = False
        self.neighbor_mines = 0
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect(topleft=(col * CELL_SIZE, row * CELL_SIZE))

    def reveal(self):
        if not self.is_revealed and not self.flagged:
            self.is_revealed = True
            return not self.is_mine  # Возвращает True, если игра продолжается
        return True  # Если уже раскрыта или отмечена флагом

    def toggle_flag(self):
        if not self.is_revealed:
            self.flagged = not self.flagged

    def update(self, bomb_image, flag_image):
        if self.is_revealed:
            self.image.fill(LIGHT_GREY)
            if self.is_mine:
                # Отображаем изображение бомбы
                bomb_resized = pygame.transform.scale(bomb_image, (CELL_SIZE, CELL_SIZE))
                self.image.blit(bomb_resized, (0, 0))
            elif self.neighbor_mines > 0:
                font = pygame.font.Font(None, 36)
                text_surface = font.render(str(self.neighbor_mines), True, BLACK)
                self.image.blit(text_surface, (CELL_SIZE // 2 - text_surface.get_width() // 2,
                                               CELL_SIZE // 2 - text_surface.get_height() // 2))
        else:
            self.image.fill(LIGHT_BLUE)
            if self.flagged:
                # Отображаем изображение флага
                flag_resized = pygame.transform.scale(flag_image, (CELL_SIZE, CELL_SIZE))
                self.image.blit(flag_resized, (0, 0))


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
        if not self.game_over_flag:  # Проверка на состояние игры
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
        if not self.game_over_flag:  # Проверка на состояние игры
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

    def update(self, bomb_image, flag_image):
        for row in self.cells:
            for cell in row:
                cell.update(bomb_image, flag_image)

    def draw(self, screen):
        for row in self.cells:
            for cell in row:
                screen.blit(cell.image, cell.rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Сапер")
    clock = pygame.time.Clock()

    # Загружаем изображения и изменяем их размер до CELL_SIZE x CELL_SIZE
    bomb_image = pygame.image.load('bomb.png').convert_alpha()
    flag_image = pygame.image.load('flag.png').convert_alpha()

    game = Minesweeper()

    running = True
    while running:
        screen.fill((255, 255, 255))

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

        game.update(bomb_image, flag_image)  # Обновляем спрайты

        game.draw(screen)  # Отрисовываем спрайты

        # Проверка завершения игры и отображение сообщения
        if game.game_over_flag:
            font = pygame.font.Font(None, 48)
            text_surface = font.render("Игра окончена!", True, (255, 0, 0))
            screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2,
                                        HEIGHT // 2 - text_surface.get_height() // 2))

        if game.win_flag:
            font = pygame.font.Font(None, 48)
            text_surface = font.render("Вы победили!", True, (0, 0, 0))
            screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2,
                                        HEIGHT // 2 - text_surface.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
