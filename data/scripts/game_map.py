from copy import deepcopy
from .entity import Entity
from . import config
from . import utils
from .animation import Animation
import pygame

# TODO: Make less redundant
top_wall = Animation.img_db['top_wall']
Animation.add_img(pygame.transform.flip(top_wall, False, True), 'bottom_wall', save=True)
Animation.add_img(pygame.transform.rotate(top_wall, -90), 'right_wall', save=True)
Animation.add_img(pygame.transform.rotate(top_wall, 90), 'left_wall', save=True)

top_door = Animation.img_db['top_door']
Animation.add_img(pygame.transform.flip(top_door, False, True), 'bottom_door', save=True)
Animation.add_img(pygame.transform.rotate(top_door, -90), 'right_door', save=True)
Animation.add_img(pygame.transform.rotate(top_door, 90), 'left_door', save=True)

tl_wall = Animation.img_db['tl_wall']
Animation.add_img(pygame.transform.rotate(tl_wall, -90), 'tr_wall', save=True)
Animation.add_img(pygame.transform.rotate(tl_wall, -180), 'br_wall', save=True)
Animation.add_img(pygame.transform.rotate(tl_wall, -270), 'bl_wall', save=True)

class Tile(Entity):
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

    NO_COLLISION_TILES = 'ground'.split()

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
        name = args['name']
        return cls(collision=not name in Tile.NO_COLLISION_TILES, **args)



class GameMap:

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

    EDGE_PAN = 12
    ROOMS_PATH = 'rooms.json'

    def load_all_rooms(self):
        rooms = utils.read_json(GameMap.ROOMS_PATH)
        self.rooms = deepcopy(rooms)

        for category, rooms in rooms['all'].items():
            for i, room in enumerate(rooms):
                print(f'{room=}')
                for j, tile in enumerate(room):
                    print(f'{tile=}')
                    self.rooms['all'][category][i][j] = Tile.get_deserialized(**tile)

    def load_room(self):
        self.room_size = (18+6, 12)

        self.grid = [[0]*self.room_size[0] for _ in range(self.room_size[1])]
        self.collision_tiles = []
        
        for tile in self.tiles:
            if tile.collision:
                self.collision_tiles.append(tile.rect)
                x, y = int(tile.pos[0] // config.TILE_SIZE[0]), int(tile.pos[1] // config.TILE_SIZE[1])
                self.grid[y][x] = 1


        self.room_px_size = (self.room_size[0]*config.TILE_SIZE[0],
                            self.room_size[1]*config.TILE_SIZE[1])

        self.center = [0.5*(config.CANVAS_SIZE[0]-self.room_px_size[0]),
                        0.5*(config.CANVAS_SIZE[1]-self.room_px_size[1])]
        self.real_offset = self.center.copy()

        self.edges = (
            (GameMap.EDGE_PAN, 2*self.center[0] - GameMap.EDGE_PAN),
            (GameMap.EDGE_PAN, 2*self.center[1] - GameMap.EDGE_PAN),
        )



    @property
    def tiles(self):
        return self.rooms['all'][self.room_id[0]][self.room_id[1]]

    def __init__(self):
        self.load_all_rooms()

        self.room_id = ('normal', 0)
        self.load_room()


            # self.grid.append([])
            #
            # for j, str_tile in enumerate(row):
            #     name = GameMap.TILE_MAP[str_tile]
            #     collision = str_tile in GameMap.COLLISION_TILES
            #     tile = Tile(pos=(j*config.TILE_SIZE[0],
            #                                 i*config.TILE_SIZE[1]), name=name,
            #                            collision=collision)
            #     self.tiles.append(tile)
            #     if collision: self.collision_tiles.append(tile.rect)
            #
            #     grid_id = 1 if collision else 0
            #     self.grid[i].append(grid_id)

    def update_offset(self, player):
        target = 0.5*pygame.Vector2(config.CANVAS_SIZE) - player.pos
        # self.offset = target
        self.real_offset += (target-self.real_offset) * 0.05
        for i in range(2):
            if abs(self.edges[i][0] - self.edges[i][1]) < self.room_px_size[i] + 2*GameMap.EDGE_PAN:
                continue

            for direction, edge in enumerate(self.edges[i]):
                adjusting = False
                if direction == 0:  # left
                    if self.real_offset[i] > edge:
                        print(f'{i} {self.real_offset[i]} < {edge}')
                        adjusting = True
                elif direction == 1:  # right
                    if self.real_offset[i] < edge:
                        print(f'{i} {self.real_offset[i]} > {edge}')
                        adjusting = True

                if adjusting:
                    self.real_offset[i] = edge
                    # self.real_offset[i] += (-self.real_offset[i] + edge) * 1
                    # self.real_offset[i] = 0.1*(self.real_offset[i] - edge)**2
                    # from random import uniform
                    # print(f'too big {uniform(0, 1)}')

        # self.real_offset = self.center
        self.offset = pygame.Vector2(int(self.real_offset[0]), int(self.real_offset[1]))

    def render(self, surf):
        for tile in self.tiles:
            tile.render(surf, offset=self.offset)
