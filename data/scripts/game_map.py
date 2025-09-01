from copy import deepcopy
from .creatures import Player
from .entity import Entity
from . import config
from . import utils
from .animation import Animation
from math import ceil
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

    def __init__(self, *args, **kwargs):
        init_args = (args, kwargs)
        super().__init__(*args, **kwargs)
        self.collision=not self.name in Tile.NO_COLLISION_TILES

    def get_serialized(self):
        # d = self.__dict__
        # d['real_pos'] = tuple(d['real_pos'])
        # d = 
        return {
            'name': self.name,
                'pos': tuple(self.pos),
        }

    def collide(self, entity: Entity, direction):
        pass

    @classmethod
    def get_deserialized(cls, **args):
        # d = self.__dict__
        # d['real_pos'] = tuple(d['real_pos'])
        # d = 
        name = args['name']
        return cls(**args)

class DoorTile(Tile):

    def collide(self, entity: Entity, direction):
        if isinstance(entity, Player):
            print(f'Collision with door ({self.name=})')
            game_map = entity.state_manager.game_map

            # entity.real_pos = pygame.Vector2(100, 100)
            # entity.real_pos = Room.PLAYER_TRANSITION_POS[direction] - 0.5*pygame.Vector2(entity.rect.w, entity.rect.h)
            # entity.real_pos = Room.PLAYER_TRANSITION_POS[direction] - 0.5*pygame.Vector2(entity.animation.rect.center)
            # entity.real_pos = list(Room.PLAYER_TRANSITION_POS[direction]) # - 0.5*pygame.Vector2(entity.rect.w, entity.rect.h)

            entity.real_pos = Room.PLAYER_TRANSITION_POS[direction]
            rect = entity.rect
            rect.center = Room.PLAYER_TRANSITION_POS[direction]
            rect.topleft -= pygame.Vector2(entity.animation.rect.topleft)
            entity.real_pos = pygame.Vector2(rect.topleft)

            game_map.change_room(direction)


class Room:

    ROOMS_PATH = 'rooms.json'

    # Cell pos
    BASE_ROOM_SIZE = (17, 9)
    DOOR_POSITIONS = {
        'top': (int(BASE_ROOM_SIZE[0] / 2), 0),
        'bottom': (int(BASE_ROOM_SIZE[0] / 2), BASE_ROOM_SIZE[1]-1),
        'left': (0, int(BASE_ROOM_SIZE[1] / 2)),
        'right': (BASE_ROOM_SIZE[0]-1, int(BASE_ROOM_SIZE[1] / 2)),
    }

    # Px pos
    ROOM_POS_CHANGE = int(config.TILE_SIZE[0] * 1.5)
    PLAYER_TRANSITION_POS = {
        'bottom': config.TILE_SIZE[1] * pygame.Vector2(DOOR_POSITIONS['top']) + (config.TILE_SIZE[0]*0.5, 1.5*config.TILE_SIZE[0]),
        'top': config.TILE_SIZE[1] * pygame.Vector2(DOOR_POSITIONS['bottom']) + (config.TILE_SIZE[0]*0.5, -0.5*config.TILE_SIZE[0]),
        'right': config.TILE_SIZE[0] * pygame.Vector2(DOOR_POSITIONS['left']) + (1.5*config.TILE_SIZE[0], config.TILE_SIZE[0]*0.5),
        'left': config.TILE_SIZE[0] * pygame.Vector2(DOOR_POSITIONS['right']) + (-0.5*config.TILE_SIZE[0], config.TILE_SIZE[0]*0.5),
    }

    # for key in PLAYER_TRANSITION_POS:
    #     PLAYER_TRANSITION_POS[key] = (2*config.TILE_SIZE[0], 2*config.TILE_SIZE[0])

    @classmethod
    def load_all_rooms(cls):
        print('[Importing rooms]')
        rooms = utils.read_json(cls.ROOMS_PATH)
        cls.rooms = deepcopy(rooms)

        for category, rooms in rooms['all'].items():
            for i, room in enumerate(rooms):
                cls.rooms['all'][category][i] = {}
                # print(f'{room=}')
                for j, tile in enumerate(room):
                    # print(f'{tile=}')
                    # cls.rooms['all'][category][i][j] = Tile.get_deserialized(**tile)
                    tile_obj = Tile.get_deserialized(**tile)
                    key = (int(tile_obj.pos[0] // config.TILE_SIZE[0]),
                           int(tile_obj.pos[1] // config.TILE_SIZE[1]))
                    cls.rooms['all'][category][i][key] = tile_obj

    def add_collision_tile(self, tile):
        if tile.collision:
            # self.collision_tiles.append(tile.rect)
            self.collision_tiles.append(tile)
            x, y = int(tile.pos[0] // config.TILE_SIZE[0]), int(tile.pos[1] // config.TILE_SIZE[1])
            self.grid[y][x] = 1


    def __init__(self, id_, adj_rooms=None):

        self.id = id_
        # self.room_size = (18+6, 12)
        self.room_size = (17, 9)

        self.grid = [[0]*self.room_size[0] for _ in range(self.room_size[1])]
        self.collision_tiles = []
        
        for tile in self.tiles:
            self.add_collision_tile(tile)


        self.room_px_size = (self.room_size[0]*config.TILE_SIZE[0],
                            self.room_size[1]*config.TILE_SIZE[1])

        self.center = [0.5*(config.CANVAS_SIZE[0]-self.room_px_size[0]),
                        0.5*(config.CANVAS_SIZE[1]-self.room_px_size[1])]
        self.real_offset = self.center.copy()

        self.edges = (
            (GameMap.EDGE_PAN, 2*self.center[0] - GameMap.EDGE_PAN),
            (GameMap.EDGE_PAN, 2*self.center[1] - GameMap.EDGE_PAN),
        )



        if adj_rooms is None: adj_rooms = {}
        self.adj_rooms = {
            'top': None,
            'bottom': None,
            'left': None,
            'right': None, } | adj_rooms

        self.update_connections()

    def update_connections(self):
        for direction, room in self.adj_rooms.items():
            if not room:
                continue

            door_cell_pos = Room.DOOR_POSITIONS[direction]
            # door_cell_pos = (door_cell_pos[0]+10, door_cell_pos[1]+5)
            og_tile = self.tiles_dict[door_cell_pos]
            if og_tile in self.collision_tiles: self.collision_tiles.remove(og_tile)
            door_px_pos = og_tile.pos

            door_name = f'{direction}_door'
            # TODO: Change door for special adjacent rooms
            # Also for door to work on any background, maybe door should be
            # transparent

            door_tile = DoorTile(pos=door_px_pos, name=door_name)

            self.tiles_dict[door_cell_pos] = door_tile
            self.add_collision_tile(door_tile)

    @property
    def tiles(self):
        return self.rooms['all'][self.id[0]][self.id[1]].values()

    @property
    def tiles_dict(self):
        return self.rooms['all'][self.id[0]][self.id[1]]

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

    def generate_map(self):
        self.map_rooms = [
            Room(('normal', 0)),
            Room(('normal', 1)),
            Room(('normal', 2)),
            Room(('normal', 3)),
        ]

        self.map_rooms[0].adj_rooms |= {'right': self.map_rooms[1], 'bottom': self.map_rooms[2]}
        self.map_rooms[1].adj_rooms |= {'left': self.map_rooms[0], 'bottom': self.map_rooms[3]}
        self.map_rooms[2].adj_rooms |= {'top': self.map_rooms[0], 'right': self.map_rooms[3]}
        self.map_rooms[3].adj_rooms |= {'left': self.map_rooms[2], 'top': self.map_rooms[1]}
        
        for room in self.map_rooms:
            room.update_connections()

    def __init__(self):
        self.generate_map()
        self.set_room(self.map_rooms[0])

    def set_room(self, room):
        self.room = room
        self.tiles = room.tiles
        self.room_px_size = room.room_px_size
        self.real_offset = room.center.copy()
        self.collision_tiles = room.collision_tiles
        self.grid = room.grid
        self.room_size = room.room_size
        self.edges = self.room.edges

    def update_offset(self, player):
        # TODO: Optimize by not calculating target if edge
        target = 0.5*pygame.Vector2(config.CANVAS_SIZE) - player.pos
        # self.offset = target
        self.real_offset += (target-self.real_offset) * 0.05
        for i in range(2):
            if abs(self.edges[i][0] - self.edges[i][1]) < self.room_px_size[i] + 2*GameMap.EDGE_PAN:
                
                self.real_offset[i] = self.room.center[i]
                continue

            for direction, edge in enumerate(self.edges[i]):
                adjusting = False
                if direction == 0:  # left
                    if self.real_offset[i] > edge:
                        # print(f'{i} {self.real_offset[i]} < {edge}')
                        adjusting = True
                elif direction == 1:  # right
                    if self.real_offset[i] < edge:
                        # print(f'{i} {self.real_offset[i]} > {edge}')
                        adjusting = True

                if adjusting:
                    self.real_offset[i] = edge
                    # self.real_offset[i] += (-self.real_offset[i] + edge) * 1
                    # self.real_offset[i] = 0.1*(self.real_offset[i] - edge)**2
                    # from random import uniform
                    # print(f'too big {uniform(0, 1)}')

        # self.real_offset = self.center
        self.offset = pygame.Vector2(int(self.real_offset[0]), int(self.real_offset[1]))

    def change_room(self, direction):
        self.set_room(self.room.adj_rooms[direction])

    def render(self, surf):
        for tile in self.tiles:
            tile.render(surf, offset=self.offset)



Room.load_all_rooms()
