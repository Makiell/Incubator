from settings import *
import math
from tetromino import Tetromino
import pygame.freetype as ft
import pygame_menu


class Text:
    def __init__(self, app):
        self.app = app
        self.font = ft.Font(FONT_PATH)

    def get_color(self):
        time = pg.time.get_ticks() * 0.001
        n_sin = lambda t: (math.sin(t) * 0.5 + 0.5) * 255
        return n_sin(time * 0.5), n_sin(time * 0.2), n_sin(time * 0.9)

    def draw(self):
        self.font.render_to(self.app.screen, (WIN_W * 0.595, WIN_H * 0.02),
                            text='TETRIS', fgcolor=self.get_color(),
                            size=TILE_SIZE * 1.65, bgcolor='black')
        self.font.render_to(self.app.screen, (WIN_W * 0.65, WIN_H * 0.22),
                            text='next', fgcolor='orange',
                            size=TILE_SIZE * 1.4, bgcolor='black')
        self.font.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.67),
                            text='score', fgcolor='orange',
                            size=TILE_SIZE * 1.4, bgcolor='black')
        self.font.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.8),
                            text=f'{self.app.tetris.score}', fgcolor='white',
                            size=TILE_SIZE * 1.8)
        self.font.render_to(self.app.screen, (WIN_W * 0.64,950), text=f'record: {self.app.tetris.record}', fgcolor='orange', size=TILE_SIZE*0.7, bgcolor='black')
        print(self.app.tetris.last)
        self.font.render_to(self.app.screen, (0,0), text=f'Last score: {self.app.tetris.last}', fgcolor='orange', size=TILE_SIZE*0.7, bgcolor='black')
        


class Tetris:
    def __init__(self, app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self.speed_up = False

        self.score = 0
        self.record = self.get_record()
        self.last = self.get_last_score()
        self.full_lines = 0
        self.points_per_lines = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

    def get_score(self):
        self.score += self.points_per_lines[self.full_lines]
        self.full_lines = 0

    def get_record(self):
        try:
            with open('D:\Git\\nFactorial\\tetr\scores\\record.txt') as f:
                return f.readline()
        except FileNotFoundError:
            with open('record', 'w') as f:
                f.write('0')

    def get_last_score(self):
        try:
            with open('D:\Git\\nFactorial\\tetr\scores\last.txt') as f:
                return f.readline()
        except FileNotFoundError:
            with open('last', 'w') as f:
                f.write('0')

    def check_full_lines(self):
        row = FIELD_H - 1
        for y in range(FIELD_H - 1, -1, -1):
            for x in range(FIELD_W):
                self.field_array[row][x] = self.field_array[y][x]

                if self.field_array[y][x]:
                    self.field_array[row][x].pos = vec(x, y)

            if sum(map(bool, self.field_array[y])) < FIELD_W:
                row -= 1
            else:
                for x in range(FIELD_W):
                    self.field_array[row][x].alive = False
                    self.field_array[row][x] = 0

                self.full_lines += 1

    def put_tetromino_blocks_in_array(self):
        for block in self.tetromino.blocks:
            x, y = int(block.pos.x), int(block.pos.y)
            self.field_array[y][x] = block

    def get_field_array(self):
        return [[0 for x in range(FIELD_W)] for y in range(FIELD_H)]

    def is_game_over(self):
        if self.tetromino.blocks[0].pos.y == INIT_POS_OFFSET[1]:
            self.set_record(self.app.tetris.record, self.app.tetris.score)
            self.set_score(self.app.tetris.score)
            pg.time.wait(300)
            return True

    def check_tetromino_landing(self):
        if self.tetromino.landing:
            if self.is_game_over():
                self.__init__(self.app)
            else:
                self.speed_up = False
                self.put_tetromino_blocks_in_array()
                self.next_tetromino.current = True
                self.tetromino = self.next_tetromino
                self.next_tetromino = Tetromino(self, current=False)

    def control(self, pressed_key):
        if pressed_key == pg.K_LEFT:
            self.tetromino.move(direction='left')
        elif pressed_key == pg.K_RIGHT:
            self.tetromino.move(direction='right')
        elif pressed_key == pg.K_UP:
            self.tetromino.rotate()
        elif pressed_key == pg.K_DOWN:
            self.speed_up = True

    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'black',
                             (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    def update(self):
        print((self.app.tetris.record, self.app.tetris.last))
        trigger = [self.app.anim_trigger, self.app.fast_anim_trigger][self.speed_up]
        if trigger:
            self.check_full_lines()
            self.tetromino.update()
            self.check_tetromino_landing()
            self.get_score()
        self.sprite_group.update()

    def draw(self):
        self.draw_grid()
        self.sprite_group.draw(self.app.screen)

    def set_record(self, record, score):
        rec = max(int(record), score)
        with open('D:\Git\\nFactorial\\tetr\scores\\record.txt', 'w') as f:
            f.write(str(rec))

    def set_score(self, score):
        with open('D:\Git\\nFactorial\\tetr\scores\\last.txt', 'w') as f:
            f.write(str(score))

    # def menu(self):
    #     menu = pygame_menu.Menu('Snake', 400, 300,
    #                    theme=pygame_menu.themes.THEME_GREEN.set_background_color_opacity(1))
    #     menu.add.text_input('Name :', default='Player 1')
    #     menu.add.button('Play', self.__init__(self.app))
    #     menu.add.button('Quit', pygame_menu.events.EXIT)

    #     while True:


    #         events = pg.event.get()
    #         for event in events:
    #             if event.type == pg.QUIT:
    #                 exit()

    #         if menu.is_enabled():
    #             menu.update(events)
    #             menu.draw(self.app.screen)
    #         font= ft.Font(FONT_PATH)
    #         font.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.67),
    #                         text='score', fgcolor='orange',
    #                         size=TILE_SIZE * 1.4, bgcolor='black')
    #         font.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.8),
    #                         text=f'{self.app.tetris.score}', fgcolor='white',
    #                         size=TILE_SIZE * 1.8)
    #         font.render_to(self.app.screen, (WIN_W * 0.64,950), text=f'record: {self.app.tetris.record}', fgcolor='orange', size=TILE_SIZE*0.7, bgcolor='black')
    #         pg.display.flip()

