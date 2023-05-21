import pygame
from random import randint

class Star:
    """Класс для представления звезд на экране."""

    def __init__(self, ai_game):
        """Инициализирует звезду и ее начальную позицию."""
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Загружает изображение звезды.
        self.image = pygame.image.load('images/star.bmp')
        self.rect = self.image.get_rect()
        self.rect.x = randint(-10, 10) + randint(0, self.screen.get_width() - self.rect.width)
        self.rect.y = randint(-10, 10) + randint(0, self.screen.get_height() - self.rect.height)

        # Прозрачность звезды.
        self.alpha = 255
        self.alpha_step = -5  # Уменьшаем прозрачность на каждом шаге

        # Флаг, указывающий, мерцает ли звезда.
        self.twinkle = False


    def blitme(self):
        """Отображает звезду на экране."""
        self.image.set_alpha(self.alpha)  # Устанавливаем прозрачность звезды
        self.screen.blit(self.image, self.rect)

    def update(self):
        """Обновляет прозрачность звезды."""
        if self.twinkle:
            if self.alpha <= 90:
                self.alpha_step = 5  # Изменяем направление изменения прозрачности
            elif self.alpha >= 255:
                self.alpha_step = -5  # Изменяем направление изменения прозрачности

            self.alpha += self.alpha_step
            # Решаем, мерцает ли звезда на этом шаге.
        self.twinkle = randint(0, 10) == 0
