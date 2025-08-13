from .entity import Entity
from . import config

class Tile(Entity):
    def __init__(self, collision, *args, **kwargs):
        self.collision = collision
        super().__init__(*args, **kwargs)

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

    TILE_MAP = {
            '0': 'ground',
            '1': 'wall',
        }

    COLLISION_TILES = ('1',)

    def __init__(self):
        self.tiles = []

        array_layout = [row.strip() for row in GameMap.MAP_LAYOUT.split('\n') if row.strip()]
        print(array_layout)
        for i, row in enumerate(array_layout):
            for j, str_tile in enumerate(row):
                name = GameMap.TILE_MAP[str_tile]
                self.tiles.append(Tile(pos=(j*config.TILE_SIZE[0],
                                            i*config.TILE_SIZE[1]), name=name,
                                       collision=str_tile in GameMap.COLLISION_TILES),
                                  )

    def render(self, surf):
        for tile in self.tiles:
            tile.render(surf)
