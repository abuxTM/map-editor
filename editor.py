import pygame as pg
import pickle
import sys

SCALE = 2
TILE_SIZE = 16 * SCALE

class Editor:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((1280, 720))
        self.clock = pg.time.Clock()
        
        self.assets = {
            'tileset': self.load_image('tiles.png', SCALE),
        }

        self.tiles = []
        self.offtiles = []

        self.current_tile_img = self.assets['tileset'].copy()
        self.current_tile_img.set_alpha(150)

        self.current_tile = 0
        self.current_tile_y = 0

        self.place_offtiles = False
        self.show_tiles = False
        self.show_tiles_rect = False
        self.show_grid = True
        self.show_gui = True

        self.font = pg.font.Font('FFFFORWA.TTF', 32)
        self.filename = ''
        self.status = ''

        # Camera
        self.camera = [0, 0]
        self.pos = [self.screen.get_width()/2, self.screen.get_height()/2]
        self.isMoving = False

    def save(self, filename):
        self.status = 'saved'
        map_data = {
            'tiles': self.tiles,
            'offtiles': self.offtiles
        }
        with open(filename, 'wb') as file:
            pickle.dump(map_data, file)

    def load(self, filename):
        try:
            self.status = 'loaded'
            with open(filename, 'rb') as file:
                map_data = pickle.load(file)
                return map_data.get('tiles', []), map_data.get('offtiles', [])
        except FileNotFoundError:
            return [], []

    def place_tile(self, m_pos):
        self.remove_tile(m_pos)
        self.status = 'edited'
        if self.place_offtiles:
            self.offtiles.append((m_pos, self.current_tile, self.current_tile_y))
        else:
            self.tiles.append((m_pos, self.current_tile, self.current_tile_y, pg.Rect(m_pos[0], m_pos[1], TILE_SIZE, TILE_SIZE)))

    def remove_tile(self, m_pos):
        if self.place_offtiles:
            for tile in self.offtiles:
                pos, _, _ = tile
                rect = pg.Rect(pos, (TILE_SIZE, TILE_SIZE))
                if rect.collidepoint(m_pos):
                    self.status = 'edited'
                    self.offtiles.remove(tile)
        else:
            for tile in self.tiles:
                pos, _, _, _ = tile
                rect = pg.Rect(pos, (TILE_SIZE, TILE_SIZE))
                if rect.collidepoint(m_pos):
                    self.status = 'edited'
                    self.tiles.remove(tile)

    def draw_text(self, text, pos, color, rect=False, rect_pos=''):
        img = self.font.render(text, True, color)
        if rect_pos=='mid': self.screen.blit(img, (pos[0]-img.get_width()/2, pos[1]))
        else: self.screen.blit(img, pos)
        if rect:
            if rect_pos=='mid':
                pg.draw.rect(self.screen, color, ((pos[0]-img.get_width()/2)-10, pos[1]-10, img.get_width()+20, img.get_height()+20), 2, 5)

    def load_image(self, path, scale=1):
        img = pg.image.load(path).convert_alpha()
        scaled_img = pg.transform.scale(img, (img.get_width()*scale, img.get_height()*scale))
        return scaled_img

    def update(self):
        pg.display.flip()
        self.clock.tick(60)
        pg.display.set_caption(f'TILES: {len(self.tiles)} FPS: {self.clock.get_fps():0.0f}')

        # Update camera
        self.camera[0] += (self.pos[0] - self.screen.get_width()/2 - self.camera[0]) / 5
        self.camera[1] += (self.pos[1] - self.screen.get_height()/2 - self.camera[1]) / 5
        self.render_camera = (int(self.camera[0]), int(self.camera[1]))

        # Get mouse position and then get the grid coordinate
        self.mouse = pg.mouse.get_pos()
        self.gx = (self.mouse[0] // TILE_SIZE) * TILE_SIZE
        self.gy = (self.mouse[1] // TILE_SIZE) * TILE_SIZE

        # Add tiles
        if pg.mouse.get_pressed()[0] and not self.isMoving:
            self.place_tile((self.gx+self.render_camera[0],self.gy+self.render_camera[1]))
        # Remove tiles
        if pg.mouse.get_pressed()[2]:
            self.remove_tile((self.gx+self.render_camera[0],self.gy+self.render_camera[1]))

    def render(self):
        self.screen.fill('#282828')

        # Draw offtiles
        for pos, tile, y in self.offtiles:
            self.screen.blit(self.assets['tileset'], (pos[0]-self.render_camera[0], pos[1]-self.render_camera[1]), (tile*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE))
        # Draw tiles
        for pos, tile, y, rct in self.tiles:
            self.screen.blit(self.assets['tileset'], (pos[0]-self.render_camera[0], pos[1]-self.render_camera[1]), (tile*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE))
            if self.show_tiles_rect:
                pg.draw.rect(self.screen, '#ffffff', (rct.x-self.render_camera[0], rct.y-self.render_camera[1], rct.w, rct.h), 2, 5) 

        # Render preview
        self.screen.blit(self.current_tile_img, (self.gx,self.gy), (self.current_tile*TILE_SIZE,self.current_tile_y*TILE_SIZE,TILE_SIZE,TILE_SIZE))
        if self.show_tiles:
            self.screen.blit(self.current_tile_img, (self.screen.get_width()/2-self.assets['tileset'].get_width()/2,
                                                      self.screen.get_height()/2-self.assets['tileset'].get_height()/2))

         # Draw grid
        if self.show_grid:
            for x in range(0, 1280, TILE_SIZE):
                pg.draw.line(self.screen, 'BLACK', (x, 0), (x, 720))
            for y in range(0, 1280, TILE_SIZE):
                pg.draw.line(self.screen, 'BLACK', (0, y), (1280, y))

        # Render font
        if self.show_gui:
            self.draw_text(str(self.current_tile)+' | '+str(self.current_tile_y), (10, 10), '#ffffff')
            self.draw_text(str(self.place_offtiles), (10, self.screen.get_height()-100), '#ffffff')
            self.draw_text(self.status, (10, self.screen.get_height()-50), '#ffffff')
        if self.status == 'saving' or self.status == 'loading':
            self.draw_text(self.filename, (self.screen.get_width()/2, self.screen.get_height()/2), '#ffffff', True, 'mid')

    def inputs(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

            if event.type == pg.TEXTINPUT:
                if self.status == 'saving' or self.status == 'loading':
                    self.filename += event.text

            if event.type == pg.KEYDOWN:
                # _____SAVE&LOADING_____
                if self.status != 'loading' and event.key == pg.K_o: # Save map
                    self.status = 'saving'

                if self.status != 'saving' and event.key == pg.K_p: # Load map
                    self.status = 'loading'

                if (self.status == 'saving' or self.status == 'loading') and event.key == pg.K_BACKSPACE:
                    self.filename = self.filename[:-1] 

                if self.status == 'saving' and event.key == pg.K_RETURN:
                    self.save(self.filename)
                if self.status == 'loading' and event.key == pg.K_RETURN:
                    self.tiles, self.offtiles = self.load(self.filename)
                # ______________________

                # ______USER&INPUTS_____
                if self.status != 'saving' and self.status != 'loading':
                    if event.key == pg.K_e:
                        self.current_tile_y += 1
                    if event.key == pg.K_q:
                        self.current_tile_y -= 1
                    if event.key == pg.K_c: # Place offtiles:
                        self.place_offtiles = not self.place_offtiles
                    if event.key == pg.K_t: # Show tiles preview
                        self.show_tiles = not self.show_tiles 
                    if event.key == pg.K_r: # Show tiles rect
                        self.show_tiles_rect = not self.show_tiles_rect
                    if event.key == pg.K_g: # Show grid
                        self.show_grid = not self.show_grid
                    if event.key == pg.K_TAB: # Show gui
                        self.show_gui = not self.show_gui
                # _______________________

                # Move camera
                if self.status != 'saving' and self.status != 'loading':
                    if event.key == pg.K_w:
                        self.isMoving = True
                        self.pos[1] += -TILE_SIZE
                    if event.key == pg.K_s:
                        self.isMoving = True
                        self.pos[1] += TILE_SIZE
                    if event.key == pg.K_a:
                        self.isMoving = True
                        self.pos[0] += -TILE_SIZE
                    if event.key == pg.K_d:
                        self.isMoving = True
                        self.pos[0] += TILE_SIZE

            if event.type == pg.KEYUP:
                if self.status != 'saving' and self.status != 'loading':
                    # Move camera
                    if event.key == pg.K_w:
                        self.isMoving = False
                    if event.key == pg.K_s:
                        self.isMoving = False
                    if event.key == pg.K_a:
                        self.isMoving = False
                    if event.key == pg.K_d:
                        self.isMoving = False

            if event.type == pg.MOUSEBUTTONDOWN:
                if self.status != 'saving' and self.status != 'loading':
                    if event.button == 4:
                        self.current_tile += 1
                    if event.button == 5:
                        self.current_tile -= 1

    def run(self):
        while True:
            self.update()
            self.render()
            self.inputs()

Editor().run()

