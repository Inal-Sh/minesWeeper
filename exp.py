import pygame
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Настройка окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Сапер")


# Класс для кнопки
class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.original_width = width
        self.original_height = height
        self.scale_factor = 5  # Количество пикселей для изменения размера
        self.is_scaling_up = True
        self.animation_speed = 0.1

    def draw(self):
        # Изменение размера кнопки
        if self.is_scaling_up:
            self.rect.width += self.scale_factor * self.animation_speed
            self.rect.height += self.scale_factor * self.animation_speed
            if self.rect.width >= self.original_width + 10 or self.rect.height >= self.original_height + 10:
                self.is_scaling_up = False
        else:
            self.rect.width -= self.scale_factor * self.animation_speed
            self.rect.height -= self.scale_factor * self.animation_speed
            if self.rect.width <= self.original_width or self.rect.height <= self.original_height:
                self.is_scaling_up = True

        # Рисуем кнопку
        pygame.draw.rect(screen, BLUE, self.rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


# Создание кнопок
easy_button = Button("Легкий", 300, 250, 200, 50)
medium_button = Button("Средний", 300, 320, 200, 50)
hard_button = Button("Сложный", 300, 390, 200, 50)

# Основной цикл игры
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(WHITE)

    # Обновление и рисование кнопок
    easy_button.draw()
    medium_button.draw()
    hard_button.draw()

    pygame.display.flip()
    clock.tick(FPS)
