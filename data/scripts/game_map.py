from .entity import Entity
from . import config
from .animation import Animation
import pygame

top_wall = Animation.img_db['top_wall']
Animation.add_img(pygame.transform.flip(top_wall, False, True), 'bottom_wall')
Animation.add_img(pygame.transform.rotate(top_wall, -90), 'right_wall')
Animation.add_img(pygame.transform.rotate(top_wall, 90), 'left_wall')

tl_wall = Animation.img_db['tl_wall']
Animation.add_img(pygame.transform.rotate(tl_wall, -90), 'tr_wall')
Animation.add_img(pygame.transform.rotate(tl_wall, -180), 'br_wall')
Animation.add_img(pygame.transform.rotate(tl_wall, -270), 'bl_wall')


class Tile(Entity):
    def __init__(self, collision, *args, **kwargs):
        self.collision = collision
        super().__init__(*args, **kwargs)

class GameMap:

    MAP_LAYOUT = '''
    6222222222222227
    500r000000000004
    500r000000000r04
    5000000000000004
    5000000000000004
    5000000000000004
    500r000000000r04
    5000000000000004
    8333333333333339
    '''

    TILE_MAP = {
            '0': 'ground',
            '1': 'wall',
            '2': 'top_wall',
            '3': 'bottom_wall',
            '4': 'right_wall',
            '5': 'left_wall',
            '6': 'tl_wall',
            '7': 'tr_wall',
            '8': 'bl_wall',
            '9': 'br_wall',
            'r': 'rock',
        }

    COLLISION_TILES = tuple('12345679r')

    def __init__(self):
        self.tiles = []
        self.collision_tiles = []

        array_layout = [row.strip() for row in GameMap.MAP_LAYOUT.split('\n') if row.strip()]
        for i, row in enumerate(array_layout):

            for j, str_tile in enumerate(row):
                name = GameMap.TILE_MAP[str_tile]
                collision = str_tile in GameMap.COLLISION_TILES
                tile = Tile(pos=(j*config.TILE_SIZE[0],
                                            i*config.TILE_SIZE[1]), name=name,
                                       collision=collision)
                self.tiles.append(tile)
                if collision: self.collision_tiles.append(tile.rect)

    def render(self, surf):
        for tile in self.tiles:
            tile.render(surf)
