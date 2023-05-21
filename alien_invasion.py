import sys
from time import sleep
import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from stars import Star

class AlienInvision:
    """Класс для управления ресурсами и поведением игры."""

    def __init__(self):
        """Инициализирует игру и создает игровые ресурсы."""
        pygame.init()
        self.settings = Settings()

        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Создание экземпляра для хранения игровой статистики и панели результатов
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.star = Star(self)

        self._create_fleet()
        self._create_stars()

        # Создание кнопки Play
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Запуск основного цикла игры."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()



    def _check_events(self):
        """Отслеживание событий клавиатуры и мыши."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

            # Переместить корабль непрерывно по значению флага
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _start_game(self):
        # Сброс игровой статистики
        self.stats.reset_stats()
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        # Очистка списков пришельцев и снарядов
        self.aliens.empty()
        self.bullets.empty()

        # Создание нового флота и размещение корабля в центре
        self._create_fleet()
        self.ship.center_ship()

        # Указатель мыши скрывается
        pygame.mouse.set_visible(False)


    def _check_play_button(self, mouse_pos=None):
        """Запускает новую игру при нажатии Play"""
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        key_click = self.play_button
        if button_clicked or key_click and not self.stats.game_active:
            # Сброс игровых настроек
            self.settings.initialize_dynamic_settings()
            self._start_game()



    def _check_keydown_events(self, event):
        """Реагирует на нажатие клавиш"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_p:
            self._check_play_button()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()


    def _check_keyup_events(self, event):
        """Реагирует на отпускание клавиш"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False


    def _fire_bullet(self):
        """Создание новго снаряда и включение его в группу bullets"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _update_bullets(self):
        """Обновляет позиции снарядов и уничтожает старые снаряды"""
        # Обновление позиций снарядов
        self.bullets.update()

        # Удаление снарядов, вышедших за край экрана
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # print(len(self.bullets))
        self._check_bullet_allien_collisions()


    def _check_bullet_allien_collisions(self):
        """Обработка коллизий снарядов с пришельцами"""
        # При обнаружении попадания удалить пришельца и снаряд
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.stats.score += self.settings.alien_points
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            # Уничтожение существующих снарядов и создание нового флота
            self.bullets.empty()
            self.settings.increase_speed()
            self._create_fleet()

            # Увеличение уровня
            self.stats.level += 1
            self.sb.prep_level()


    def _update_aliens(self):
        """Обновляет позиции всех пришельцев во флоте"""
        self._check_fleet_edges()
        self.aliens.update()

        # Проверка коллизий "пришелец - корабль"
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Проверить, добрались ли пришельцы до нижнего края экрана
        self._check_aliens_bottom()


    def _ship_hit(self):
        """Обрабатывает столкновение коробля с пришельцем"""
        if self.stats.ships_left > 0:
            # Уменьшение ships_left и обновление панели счета
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Пауза
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

        # Очистка списков пришельцев и снарядов
        self.aliens.empty()
        self.bullets.empty()

        # Создание нового флота и размещение корабля в центре
        self._create_fleet()
        self.ship.center_ship()


    def _create_stars(self):
        """Создание рандомного расположения звезд"""
        stars = []
        for i in range(40):
            star = Star(self)
            stars.append(star)
        self.stars = stars


    def _create_fleet(self):
        """Создание флота вторжения"""
        # Создание пришельца
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        """Определяет количество рядов, помещающихся на экран"""
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Создание флота вторжения
        for row_number in range(number_rows):
            # Создание первого ряда пришельцев
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)


    def _create_alien(self, alien_number, row_number):
        """Создание пришельца и размещение его в ряду"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)


    def _check_fleet_edges(self):
        """Реагирует на достижение пришельцем края экрана"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        """Опускает весь флот и меняет направление флота"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def _check_aliens_bottom(self):
        """Проверяет, добрались ли пришельцы до нижнего края экрана"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Происходит тоже, что и при столкновении с кораблем
                self._ship_hit()
                break


    def _update_screen(self):
        """Обновляет изобраэения на экране и отображает новый экран"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        for star in self.stars:
            star.update()
            star.blitme()
        self.aliens.draw(self.screen)

        # Вывод информации о счете
        self.sb.show_score()

        # Кнопка Play отображается в том случае, если игра неактивна
        if not self.stats.game_active:
            self.play_button.draw_button()

        # Отображение последнего прорисованного экрана.
        pygame.display.flip()

if __name__ == '__main__':
    # Создание экземпляра и создание игры.
    ai = AlienInvision()
    ai.run_game()
