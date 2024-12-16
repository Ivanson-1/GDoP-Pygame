import random

import pygame
import os
import sys

from pygame.math import Vector2
from pygame import mixer


size = WIDTH, HEIGHT = 900, 600
tile_width = tile_height = 50
GRAVITY = Vector2(0, 0.5)

current_level = "level1.txt"


def window_title(title):
    pygame.display.set_caption(title)
    Icon = load_image("pict/player.png")
    pygame.display.set_icon(Icon)


def load_image(name, colorkey=None):
    fullname = os.path.join("data", name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def play_sound(filename, volume=0.5, channel=0):
    sound = mixer.Sound(filename)
    sound.set_volume(volume)
    mixer.Channel(channel).play(sound)


def gameplay():
    window_title("PLAY")

    global cnt, death_player, win, death, running
    while True:
        if not win and not death:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_UP
                    or event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    player.jump()
                elif event.type == MYEVENTTYPE:
                    if not win and not death:
                        player.move()
                        if not player.is_jump:
                            create_particles((player.rect.x - 3, player.rect.y + 45))
                        cnt += 1
                        if cnt >= 4:
                            cnt = 0
                            coin_sprite.update()
                            fin_flag_sprite.update()
                    else:
                        if death_player is None:
                            death_player = DeathWin()
                        death_player.update()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif (
                    event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN
                ):
                    return
                elif event.type == MYEVENTTYPE:
                    if death_player is None:
                        death_player = DeathWin()
                    death_player.update()

        if not win and not death:
            screen.fill((0, 0, 0))
            camera.update(background)
            camera.update(player)
            for sprite in all_sprites:
                if sprite != background and sprite != bank:
                    camera.apply(sprite)
            block_sprites.update()
            particle_sprite.update()
            peak_sprites.update()
            player_sprite.update()
            bank_sprite.update()
            all_sprites.draw(screen)
            player_sprite.draw(screen)
        else:
            if death_player is None:
                death_player = DeathWin()
            death_player.draw(screen)
        pygame.display.flip()


def start_screen():
    window_title("MENU")

    global screen, running, current_level
    intro_text = [
        "СОБЕРИТЕ ВСЕ МОНЕТЫ И КОСНИТЕСЬ ФЛАШКА ФИНИША",
        "",
        "нажмите чтобы начать игру",
    ]

    logo = load_image("pict/logo.png")
    fon = pygame.transform.scale(load_image("pict/menu.jpg"), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    screen.blit(logo, (350, 50))

    font = pygame.font.Font("data/font/impact regular.ttf", 28)
    font_2 = pygame.font.Font("data/font/impact regular.ttf", 18)
    text_coord = 200
    for line in range(len(intro_text)):
        if line <= 1:
            string_rendered = font.render(
                intro_text[line], 1, pygame.Color(200, 50, 200)
            )
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 150
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        else:
            string_rendered = font_2.render(
                intro_text[line], 1, pygame.Color(180, 100, 250)
            )
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 340
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

    level_1 = LevelButton(1)
    level_2 = LevelButton(2)
    level_3 = LevelButton(3)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                generate_level(load_level(current_level))
                play_sound(f"data/sound/{current_level[:-4]}.mp3")
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if check_click(pygame.mouse.get_pos()):
                    current_level = check_click(pygame.mouse.get_pos())
                    generate_level(load_level(current_level))
                    background.update(current_level)
                    play_sound(f"data/sound/{current_level[:-4]}.mp3")
                    return True

        level_1.update(pygame.mouse.get_pos())
        level_2.update(pygame.mouse.get_pos())
        level_3.update(pygame.mouse.get_pos())
        button_sprite.draw(screen)
        pygame.display.flip()
        clock.tick(50)


def check_click(pos):
    for i in button_sprite:
        if i.rect.x < pos[0] < i.rect.x + 180 and i.rect.y < pos[1] < i.rect.y + 120:
            return f"{i.current_level}.txt"
    return False


class LevelButton(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__(button_sprite, all_sprites)
        self.current_level = f"level{level}"
        self.image_a = load_image(f"pict/level_{level}.png")
        self.image_b = load_image(f"pict/level_{level}_tup.png")
        self.image = self.image_a
        self.rect = self.image.get_rect()

        self.rect.x = 150 + (level - 1) * 220
        self.rect.y = 400

    def update(self, pos):
        if (
            self.rect.x < pos[0] < self.rect.x + 180
            and self.rect.y < pos[1] < self.rect.y + 120
        ):
            self.image = self.image_b
        else:
            self.image = self.image_a


class Background(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__(all_sprites)
        self.image = load_image(
            f"pict/background{level[5]}.png"
        )  # pygame.Surface(size)
        self.rect = self.image.get_rect()

    def update(self, level):
        self.image = load_image(f"pict/background{level[5]}.png")


class Block(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(block_sprites, all_sprites)
        self.image = load_image("pict/block.png")
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Peak(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(peak_sprites, all_sprites)
        self.image = load_image("pict/peak.png")
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class FinishFlag(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(fin_flag_sprite, all_sprites)
        self.frames = [
            load_image("pict/fin_flag_1.png"),
            load_image("pict/fin_flag_2.png"),
        ]
        self.rect = (
            self.frames[0]
            .get_rect()
            .move(tile_width * (pos_x - 1), tile_height * (pos_y - 1))
        )
        self.image = load_image("pict/fin_flag_2.png")
        self.cur_frames = 0

    def update(self, *args, **kwargs):
        self.cur_frames = (self.cur_frames + 1) % len(self.frames)
        self.image = self.frames[self.cur_frames]


class Bank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(bank_sprite, all_sprites)
        pygame.font.init()
        self.font = pygame.font.Font("data/font/EBENYA.ttf", 100)
        self.image = self.font.render(str(money), False, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 50, 10
        self.all_coin = all_coin

    def update(self):
        self.image = self.font.render(
            f"{money}/{self.all_coin}", False, (255, 255, 255)
        )


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(coin_sprite, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(
            0, 0, sheet.get_width() // columns, sheet.get_height() // rows
        )
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(
                    sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                )

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_sprite, all_sprites)
        self.image = load_image("pict/player.png")
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

        self.is_jump = True
        self.count_jump = 0
        self.is_died = False
        self.is_won = False
        self.correct_position = False
        self.angle = 0

        self.vel = Vector2(0, 0)
        self.gravity = GRAVITY
        self.jump_gravity = Vector2(0, 0.9)
        self.vel.x = 6

        self.particles = []

    def move(self):
        global money
        if pygame.sprite.spritecollide(self, block_sprites, False):
            self.is_jump = False
            self.count_jump = 0
            self.vel = Vector2(6, 0)

            self.check_collide_in_jump()
            if self.check_collide_top_border() and not pygame.sprite.spritecollide(
                self, peak_sprites, False
            ):
                if not self.correct_position:
                    self.check_position()
            else:
                self.is_died = True
                self.is_won = False

        else:
            self.is_jump = True
            self.correct_position = False

            self.vel += self.gravity
            self.rect.y += self.vel.y

        for i in coin_sprite:
            if self.rect.colliderect(i.rect):
                i.kill()
                money += 1
                bank.update()
                if money == all_coin:
                    play_sound("data/sound/check_all_coins.mp3", channel=1, volume=0.8)
                else:
                    play_sound("data/sound/coin.mp3", channel=1, volume=0.7)

        if (
            any([self.rect.colliderect(i.rect) for i in fin_flag_sprite])
            and money == all_coin
        ):
            self.is_won = True
            self.is_died = False
        elif not self.rect.colliderect(screen_rect):
            self.is_won = False
            self.is_died = True
        self.check_life()
        self.rect.x += self.vel.x

    def jump(self):
        if self.count_jump < 2:
            self.vel.y = -10
            self.rect.y += self.vel.y
            self.count_jump += 1

    def check_position(self):
        if not self.correct_position:
            for i in block_sprites:
                if i.rect.colliderect(self.rect):
                    self.rect.y = i.rect.y - 49
            self.correct_position = True

    def check_collide_top_border(self):
        return any(
            [
                self.rect.collidepoint(i.rect.topleft)
                or self.rect.collidepoint(i.rect.midtop)
                or self.rect.collidepoint(i.rect.topright)
                for i in block_sprites
            ]
        ) and not any(
            [
                self.rect.collidepoint(i.rect.midleft)
                and self.rect.collidepoint(i.rect.bottomleft)
                for i in block_sprites
            ]
        )

    def check_collide_in_jump(self):
        return all(
            [
                self.rect.bottom <= i.rect.top
                for i in block_sprites
                if self.rect.colliderect(i.rect)
            ]
        )

    def check_life(self):
        if self.is_died:
            for i in all_sprites:
                i.kill()
            player_die()
        elif self.is_won:
            for i in all_sprites:
                i.kill()
            player_win()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Particle(pygame.sprite.Sprite):
    fire = [load_image("pict/particle.png")]
    for scale in (1, 3, 5):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(particle_sprite, all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = 0.2

    def update(self):
        self.velocity[1] += self.gravity

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        dist = pygame.math.Vector2(self.rect.x + 5, self.rect.y + 5).distance_to(
            (player.rect.x, player.rect.y)
        )
        if (
            any([self.rect.colliderect(i.rect) for i in block_sprites])
            or not self.rect.colliderect(screen_rect)
            or dist > 100
        ):
            self.kill()


class DeathWin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if win:
            self.image = load_image("pict/win_screen.jpg")
            self.text_image = pygame.transform.scale(
                load_image("pict/winner.png"), (300, 200)
            )
        else:
            self.image = load_image("pict/die_screen.jpg")
            self.text_image = pygame.transform.scale(
                load_image("pict/lose.png"), (300, 200)
            )

        self.rect = self.image.get_rect()
        self.text_rect = self.text_image.get_rect()
        self.text_rect.x = (WIDTH - self.text_rect.width) // 2
        self.text_rect.y = 0 - self.text_rect.height

        self.vel = Vector2(0, 0)

    def update(self):
        if self.text_rect.y < 200:
            self.vel += Vector2(0, 0.4)
            self.text_rect.y += self.vel.y
        else:
            self.text_rect.y = 200

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text_image, self.text_rect)


def create_particles(position):
    particle_count = 5
    numbers = range(-3, 1)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def player_win():
    global win
    win = True
    play_sound("data/sound/tadaam.mp3")


def player_die():
    global death
    death = True
    play_sound("data/sound/death.mp3")


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2 + 200)


def generate_level(level):
    global all_coin
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == ".":
                pass
            elif level[y][x] == "_":
                Block(x, y)
            elif level[y][x] == "^":
                Peak(x, y)
            elif level[y][x] == "$":
                AnimatedSprite(load_image("pict/coin_6x2.png"), 6, 2, x * 50, y * 50)
                all_coin += 1
            elif level[y][x] == ">":
                FinishFlag(x, y)
    return x, y


def load_level(filename):
    global width_level

    filename = "data/levels/" + filename
    with open(filename, "r") as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    width_level = max_width

    return list(map(lambda x: x.ljust(max_width, "."), level_map))


while True:
    pygame.init()
    mixer.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    running = True

    width_level = 0
    win = False
    death = False

    death_player = None

    MYEVENTTYPE = pygame.USEREVENT + 1
    pygame.time.set_timer(MYEVENTTYPE, 15)

    time_in_jump = 0
    screen_rect = (0, 0, WIDTH, HEIGHT)

    all_sprites = pygame.sprite.Group()
    block_sprites = pygame.sprite.Group()
    peak_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    particle_sprite = pygame.sprite.Group()
    coin_sprite = pygame.sprite.Group()
    bank_sprite = pygame.sprite.Group()
    fin_flag_sprite = pygame.sprite.Group()
    button_sprite = pygame.sprite.Group()

    camera = Camera()
    background = Background(current_level)
    player = Player(100, 100)

    cnt = 0
    all_coin = len(coin_sprite)
    money = 0

    if start_screen():
        bank = Bank()
        for i in button_sprite:
            i.kill()
        gameplay()
