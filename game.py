import pygame as pg
import pickle
import sys
from utils import *

SCALE = 2
TILE_SIZE = 16 * SCALE

class Player:
    def __init__(self, game, pos):
        self.game = game
        self.pos = list(pos)
        self.velocity = [0,0]
        self.isGrounded = False

    def rect(self):
        return pg.Rect(self.pos[0], self.pos[1], 32, 32)

    def render(self, surf):
        pg.draw.rect(surf, '#ffffff', self.rect(), 2, 6)

    def movement(self):
        keys = pg.key.get_pressed()

        if keys[pg.K_a]:
            self.velocity[0] = -4
        elif keys[pg.K_d]:
            self.velocity[0] = 4
        else:
            self.velocity[0] = 0

        if keys[pg.K_SPACE] and self.isGrounded:
            self.velocity[1] = -8

    def update(self, tiles):
        self.movement()
        self.isGrounded = False

        self.pos[0] += self.velocity[0]
        e_rect = self.rect()
        for _, _, _, tile in tiles:
            if e_rect.colliderect(tile):
                if self.velocity[0] < 0:
                    e_rect.left = tile.right
                if self.velocity[0] > 0:
                    e_rect.right = tile.left
                self.pos[0] = e_rect.x
        self.pos[1] += self.velocity[1]
        e_rect = self.rect()
        for _, _, _, tile in tiles:
            if e_rect.colliderect(tile):
                if self.velocity[1] < 0:
                    e_rect.top = tile.bottom
                    self.velocity[1] = 0
                if self.velocity[1] > 0:
                    e_rect.bottom = tile.top
                    self.velocity[1] = 0
                    self.isGrounded = True
                self.pos[1] = e_rect.y

        self.velocity[1] = min(10, self.velocity[1] + 0.4)

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((1280, 720))
        self.clock = pg.time.Clock()

        # Load tiles
        self.assets = {
            'tileset': load_image('tiles.png', 2),
        }

        # Store tiles
        self.tiles = []
        self.offtiles = []

        self.new_game()

    def new_game(self):
        # Get tiles from map data
        self.tiles, self.offtiles = self.load('MAPONE') # ----------------
        self.player = Player(self, (600, 100))

    def load(self, filename):
        try:
            self.status = 'loaded'
            with open(filename, 'rb') as file:
                map_data = pickle.load(file)
                return map_data.get('tiles', []), map_data.get('offtiles', [])
        except FileNotFoundError:
            return [], []

    def inputs(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

    def update(self):
        self.player.update(self.tiles)
        pg.display.flip()
        self.clock.tick(60)
        pg.display.set_caption(f'FPS: {self.clock.get_fps():0.0f}')

    def render(self):
        self.screen.fill('#282828')

        # Draw offtiles
        for pos, tile, y in self.offtiles:
            self.screen.blit(self.assets['tileset'], (pos[0], pos[1]), (tile*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE))
        # Draw tiles
        for pos, tile, y, _ in self.tiles:
            self.screen.blit(self.assets['tileset'], (pos[0], pos[1]), (tile*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE)) 

        self.player.render(self.screen)

    def run(self):
        while True:
            self.inputs()
            self.update()
            self.render()

Game().run()
