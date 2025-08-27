from .entity import Entity
from . import config
from .animation import Animation
import pygame

top_wall = Animation.img_db['top_wall']
Animation.add_img(pygame.transform.flip(top_wall, False, True), 'bottom_wall', save=True)
Animation.add_img(pygame.transform.rotate(top_wall, -90), 'right_wall', save=True)
Animation.add_img(pygame.transform.rotate(top_wall, 90), 'left_wall', save=True)

tl_wall = Animation.img_db['tl_wall']
Animation.add_img(pygame.transform.rotate(tl_wall, -90), 'tr_wall', save=True)
Animation.add_img(pygame.transform.rotate(tl_wall, -180), 'br_wall', save=True)
Animation.add_img(pygame.transform.rotate(tl_wall, -270), 'bl_wall', save=True)


class Tile(Entity):
    def __init__(self, collision, *args, **kwargs):
        init_args = (args, kwargs)
        self.collision = collision
        super().__init__(*args, **kwargs)

    def get_serialized(self):
        # d = self.__dict__
        # d['real_pos'] = tuple(d['real_pos'])
        # d = 
        return {
            'name': self.name,
                'pos': tuple(self.pos),
        }

    @classmethod
    def get_deserialized(cls, **args):
        # d = self.__dict__
        # d['real_pos'] = tuple(d['real_pos'])
        # d = 
        return cls(collision=True, **args)



class GameMap:

    map_size = (16, 9)
    map_px_size = (map_size[0]*config.TILE_SIZE[0],
                   map_size[1]*config.TILE_SIZE[1])

    MAP_LAYOUT = '''
    6222222222222227
    500r000000000004
    500r000000000r04
    5000000000000004
    500rrrr000000004
    500r000000000004
    500r000000000r04
    5000000000000004
    8333333333333339
    '''

    MAP_LAYOUT = '''
    6222222222222227
    5000000000000004
    500rr0rr0r0rr004
    500000000r000004
    50000r000rr0r004
    50000r0r0000r004
    50000r000000r004
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
        self.center = [0.5*(config.CANVAS_SIZE[0]-GameMap.map_px_size[0]),
                        0.5*(config.CANVAS_SIZE[1]-GameMap.map_px_size[1])]
        # print(GameMap.map_px_size[1], config.CANVAS_SIZE[1])
        self.real_offset = self.center.copy()

        self.edges = (
            (0, 2*self.center[0]),
            (0, 2*self.center[1]),
        )

        self.tiles = []
        self.collision_tiles = []

        self.grid = []

        array_layout = [row.strip() for row in GameMap.MAP_LAYOUT.split('\n') if row.strip()]
        for i, row in enumerate(array_layout):

            self.grid.append([])

            for j, str_tile in enumerate(row):
                name = GameMap.TILE_MAP[str_tile]
                collision = str_tile in GameMap.COLLISION_TILES
                tile = Tile(pos=(j*config.TILE_SIZE[0],
                                            i*config.TILE_SIZE[1]), name=name,
                                       collision=collision)
                self.tiles.append(tile)
                if collision: self.collision_tiles.append(tile.rect)

                grid_id = 1 if collision else 0
                self.grid[i].append(grid_id)

    def update_offset(self, player):
        target = 0.5*pygame.Vector2(config.CANVAS_SIZE) - player.pos
        # self.offset = target
        self.real_offset += (target-self.real_offset) * 0.1
        for i in range(2):

            for direction, edge in enumerate(self.edges[i]):
                adjusting = False
                if direction == 0:  # left
                    if self.real_offset[i] < edge:
                        print(f'{i} {self.real_offset[i]} < {edge}')
                        adjusting = True
                elif direction == 1:  # right
                    if self.real_offset[i] > edge:
                        print(f'{i} {self.real_offset[i]} > {edge}')
                        adjusting = True

                if adjusting:
                    self.real_offset[i] += (-self.real_offset[i] + edge) * 0.3
                    # self.real_offset[i] = 0.1*(self.real_offset[i] - edge)**2
                    # from random import uniform
                    # print(f'too big {uniform(0, 1)}')

        # self.real_offset = self.center
        self.offset = pygame.Vector2(int(self.real_offset[0]), int(self.real_offset[1]))

    def render(self, surf):
        for tile in self.tiles:
            tile.render(surf, offset=self.offset)
