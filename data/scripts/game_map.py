from .entity import Entity
from . import config

class Tile(Entity):
    pass

class GameMap:

    MAP_LAYOUT = '''
    1111111111111111111
    1001000000000001
    1001000000000101
    1000000000000001
    1000000000000001
    1000000000000001
    1001000000000101
    1000000000000001
    1111111111111111
    '''

    def __init__(self):
        self.tiles = []

        array_layout = [row.strip() for row in GameMap.MAP_LAYOUT.split('\n') if row.strip()]
        print(array_layout)
        for i, row in enumerate(array_layout):
            for j, str_tile in enumerate(row):
                if str_tile == '1':
                    self.tiles.append(Tile(pos=(j*config.TILE_SIZE[0],
                                                i*config.TILE_SIZE[1]), name='wall'))

    def render(self, surf):
        for tile in self.tiles:
            tile.render(surf)
