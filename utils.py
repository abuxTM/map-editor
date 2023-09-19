import pygame as pg

def load_image(path, scale=1):
    img = pg.image.load(path).convert_alpha()
    scaled_img = pg.transform.scale(img, (img.get_width()*scale, img.get_height()*scale))
    return scaled_img
