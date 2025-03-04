import pygame

import random

import sys

import tkinter as tk

from tkinter import messagebox

from tkinter import filedialog

# Константы для уровней сложности
DIFFICULTY_SETTINGS = {
    'Легкий': (16, 16, 15),  # (ROWS, COLS, MINES)
    'Средний': (16, 16, 40),
    'Сложный': (24, 24, 99)
}

pygame.init()
pygame.font.init()
flag_type = 'flag.png'

WIDTH, HEIGHT = 400, 400
CELL_SIZE = 40
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
MINES = 10

# Цвета
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREY = (211, 211, 211)
BLACK = (0, 0, 0)
GREEN = (70, 210, 70)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
L_B = (0, 0, 255)

# Переменные для управления временем
the_world = True  # Условие для отслеживания времени
last_time = 0  # Переменная для хранения последнего результата времени
start_time = pygame.time.get_ticks()  # Запоминаем время начала


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
            return not self.is_mine
        return True

    def toggle_flag(self):
        if not self.is_revealed:
            self.flagged = not self.flagged

    def update(self, bomb_image, flag_image):
        if self.is_revealed:
            self.image.fill(LIGHT_GREY)
            if self.is_mine:
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
                flag_resized = pygame.transform.scale(flag_image, (CELL_SIZE, CELL_SIZE))
                self.image.blit(flag_resized, (0, 0))

        pygame.draw.rect(self.image, GREEN, (0, 0, CELL_SIZE, CELL_SIZE), 1)


class Minesweeper:
    def __init__(self, rows=8, cols=8, mines=10):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.cells = [[Cell(r, c) for c in range(cols)] for r in range(rows)]
        self.place_mines()
        self.calculate_neighbors()
        self.game_over_flag = False
        self.win_flag = False
        self.clock = pygame.time.Clock()
        self.running = True
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

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
        if not self.game_over_flag:
            if not self.cells[r][c].reveal():
                self.game_over()
                return False

            if self.cells[r][c].neighbor_mines == 0:
                self.reveal_adjacent_cells(r, c)

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
                            self.reveal_adjacent_cells(neighbor_x, neighbor_y)

    def toggle_cell_flag(self, r, c):
        if not self.game_over_flag:
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


def display_difficulty_menu(screen):
    font = pygame.font.Font(None, 48)
    title_surface = font.render("Выберите сложность", True, BLACK)
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, HEIGHT // 4))

    difficulties = list(DIFFICULTY_SETTINGS.keys())
    buttons = []

    for i, difficulty in enumerate(difficulties):
        button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 4 + (i + 1) * 60, 200, 50)
        buttons.append((difficulty, button_rect))

        pygame.draw.rect(screen, LIGHT_BLUE if i % 2 == 0 else LIGHT_GREY, button_rect)
        difficulty_surface = font.render(difficulty, True, GREEN)
        screen.blit(difficulty_surface,
                    (button_rect.x + button_rect.width // 2 - difficulty_surface.get_width() // 2,
                     button_rect.y + button_rect.height // 2 - difficulty_surface.get_height() // 2))

    return buttons


def open_file_dialog():
    global flag_type
    root = tk.Tk()
    root.withdraw()  # Скрыть основное окно tkinter
    file_path = filedialog.askopenfilename(title="Выберите изображение флага")
    if file_path:
        flag_type = file_path
        print(f"Выбранный файл: {flag_type}")


# Функция для отображения главного меню
def main_menu():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ДОБРО ПОЖАЛОВАТЬ!!")

    font1 = pygame.font.Font(None, 48)
    font2 = pygame.font.Font(None, 30)
    start_button = font1.render("Начать игру", True, BLACK)
    settings_button = font2.render("выбрать изображение флага", True, BLACK)

    while True:
        screen.fill(WHITE)

        # Отображение кнопок
        screen.blit(start_button, (WIDTH // 2 - start_button.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(settings_button, (WIDTH // 2 - settings_button.get_width() // 2, HEIGHT // 2 + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if (WIDTH // 2 - start_button.get_width() // 2 < mouse_pos[
                    0] < WIDTH // 2 + start_button.get_width() // 2 and
                        HEIGHT // 2 - 50 < mouse_pos[1] < HEIGHT // 2 - 50 + start_button.get_height()):
                    main()  # Запускаем игру
                    pygame.quit()
                    return

                if (WIDTH // 2 - settings_button.get_width() // 2 < mouse_pos[0] < WIDTH // 2 +
                        settings_button.get_width() // 2 and
                        HEIGHT // 2 + 10 < mouse_pos[1] < HEIGHT // 2 + 10 + settings_button.get_height()):
                    open_file_dialog()  # Открываем окно настроек

        pygame.display.flip()


def main():
    pygame.init()

    global WIDTH, HEIGHT
    WIDTH, HEIGHT = 400, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Сапер - Выбор сложности")

    running = True
    while running:
        screen.fill((255, 255, 255))

        buttons = display_difficulty_menu(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos
                    for difficulty, button_rect in buttons:
                        if button_rect.collidepoint(mouse_pos):
                            start_game(difficulty)
        pygame.display.flip()


def start_game(difficulty):
    rows, cols, mines = DIFFICULTY_SETTINGS[difficulty]
    global CELL_SIZE, WIDTH, HEIGHT, the_world, last_time, flag_type
    WIDTH, HEIGHT = cols * CELL_SIZE, rows * CELL_SIZE
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    game = Minesweeper(rows=rows, cols=cols, mines=mines)

    # Загружаем изображения и изменяем их размер до CELL_SIZE x CELL_SIZE
    bomb_image = pygame.image.load('bomb.png').convert_alpha()
    flag_image = pygame.image.load(flag_type).convert_alpha()

    clock = pygame.time.Clock()

    while True:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                row = mouse_pos[1] // CELL_SIZE
                col = mouse_pos[0] // CELL_SIZE

                if event.button == 1:
                    game.reveal_cell(row, col)
                    game.check_win()
                elif event.button == 3:
                    game.toggle_cell_flag(row, col)
        screen.fill(WHITE)
        if the_world:
            current_time = pygame.time.get_ticks()  # Получаем текущее время
            last_time = current_time - start_time  # Вычисляем прошедшее время
        else:
            pass
            the_world = not the_world
        pygame.display.set_caption(f"Сапер - Время: {int(last_time / 1000)} сек")

        # Ограничение до 60 кадров в секунду
        pygame.time.delay(16)  # ~60 FPS (1000ms / 60)
        game.update(bomb_image, flag_image)
        game.draw(screen)

        if game.game_over_flag:
            the_world = False
            font = pygame.font.Font(None, 48)
            text_surface = font.render(f"Вы проиграли. Время: {int(last_time / 1000)} сек", True, RED)

            screen.blit(text_surface,
                        (WIDTH // 2 - text_surface.get_width() // 2,
                         HEIGHT // 2 - text_surface.get_height() // 2))

            if event.type == pygame.KEYDOWN:
                main_menu()

        if game.win_flag:
            the_world = False
            font = pygame.font.Font(None, 48)
            text_surface = font.render(f"Вы победили! Время: {int(last_time / 1000)} сек", True, L_B)
            screen.blit(text_surface,
                        (WIDTH // 2 - text_surface.get_width() // 2,
                         HEIGHT // 2 - text_surface.get_height() // 2))
            if event.type == pygame.KEYDOWN:
                main_menu()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()
