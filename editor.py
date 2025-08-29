import json
import pygame
from pygame import Vector2 as Vec2
import sys
from copy import deepcopy
from data.scripts import config
from copy import deepcopy
from data.scripts.sfx import sounds
from data.scripts import utils
from data.scripts.game_map import Tile
from data.scripts.font import FONTS
from data.scripts.button import Button

def get_base_tiles():
    tiles = []

    for i, row in enumerate(tiles_str):
        for j, name in enumerate(row):
            pos = (BASE_PAN[0] + j * TILE_SIZE + (j * PAN),
                   BASE_PAN[1] + i * TILE_SIZE + (i * PAN))
            tiles.append(Tile(pos=pos, name=name, collision=True))
    return tiles

def load_rooms(path='rooms.json'):
    print('Loading')
    try:
        rooms = utils.read_json(path)
    except FileNotFoundError:
        rooms = {'all': {
            'normal': []
        }}
        save_rooms(rooms)
        return rooms

    serialized_rooms = rooms
    rooms_out = deepcopy(serialized_rooms)


    for category, rooms in serialized_rooms['all'].items():
        for i, room in enumerate(rooms):
            print(f'{room=}')
            for j, tile in enumerate(room):
                print(f'{tile=}')
                rooms_out['all'][category][i][j] = Tile.get_deserialized(**tile)
    return rooms_out

def save_rooms(rooms, path='rooms.json'):
    print('Saving')
    # print(f'{rooms=}')
    # print()
    json_rooms = deepcopy(rooms)
    for category, rooms in rooms['all'].items():
        for i, room in enumerate(rooms):
            print(f'{room=}')
            for j, tile in enumerate(room):
                print(f'{tile=}')
                json_rooms['all'][category][i][j] = tile.get_serialized()
    with open(path, 'w') as f:
        json.dump(json_rooms, f)

def handle_input(inputs):
    for key in inputs['pressed']:
        inputs['pressed'][key] = inputs['released'][key] = False

    mx, my = pygame.mouse.get_pos()
    inputs['mouse pos'] = (mx // config.SCALE, my // config.SCALE)
    inputs['unscaled mouse pos'] = mx, my

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            inputs['quit'] = True

        if event.type == pygame.MOUSEBUTTONDOWN:
            inputs['pressed'][f'mouse{event.button}'] = True
            inputs['held'][f'mouse{event.button}'] = True

        if event.type == pygame.MOUSEBUTTONUP:
            inputs['released'][f'mouse{event.button}'] = True
            inputs['held'][f'mouse{event.button}'] = False

        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            inputs['pressed'][key_name] = True
            inputs['held'][key_name] = True

        if event.type == pygame.KEYUP:
            key_name = pygame.key.name(event.key)
            inputs['released'][key_name] = True
            inputs['held'][key_name] = False

BORDER_W = 24*4
TILE_SIZE = 24
BASE_PAN = (2, 50)
PAN = 2

config.scale = 3
config.screen_size = Vec2(config.CANVAS_SIZE) * config.scale
screen = pygame.display.set_mode(config.screen_size)
canvas = pygame.Surface(config.CANVAS_SIZE + Vec2(0, BORDER_W))
clock = pygame.time.Clock()

BG = (16, 14, 18)
BG = (80, 80, 80),

room_num_btn_pos = Vec2(BASE_PAN[0], 20)
buttons = {
    'decrease_room': Button(pygame.Rect(*room_num_btn_pos, 20, 20), '[-]', 'editor'),
    'increase_room': Button(pygame.Rect(*(room_num_btn_pos + (25, 0)), 20, 20), '[+]', 'editor'),
}

tiles_str = [
    ('tl_wall', 'top_wall', 'tr_wall'),
    ('left_wall', 'ground', 'right_wall'),
    ('bl_wall', 'bottom_wall', 'br_wall'),
    ('rock',),
    ('top_door', 'bottom_door', 'right_door'),
    ('left_door',),
]

rooms = load_rooms()
tiles = get_base_tiles()
room_id = ['normal', 0]

selected_tile = None
scroll = [0, 0]
# scroll = [100, 30]

mx, my = 0, 0

inputs = {'pressed': {}, 'released': {}, 'held': {}, 'mouse pos': (0, 0)}

running = True
while running:

    old_mx, old_my = inputs['mouse pos']
    handle_input(inputs)
    mx, my = inputs['mouse pos']

    coord = (Vec2(mx, my) - scroll) // TILE_SIZE * TILE_SIZE
    screen_coord = Vec2(mx, my) // TILE_SIZE * TILE_SIZE + Vec2(scroll[0]%TILE_SIZE, scroll[1]%TILE_SIZE)  # struggling to figure this out

    running = not inputs.get('quit')

    if room_id[1] == len(rooms['all'][room_id[0]]):
        rooms['all'][room_id[0]].append([])
    map_tiles = rooms['all'][room_id[0]][room_id[1]]

    if inputs['held'].get('mouse2'):
        delta = Vec2(mx, my) - Vec2(old_mx, old_my)
        scroll += delta

    if inputs['pressed'].get('mouse1'):
        if mx <= BORDER_W:
            for tile in tiles:
                if tile.rect.collidepoint(mx, my):
                    selected_tile = tile
                    break

    elif mx > BORDER_W:

        if selected_tile and inputs['held'].get('mouse1'):

            if inputs['held'].get('shift'):
                pass

            valid_spot = True
            for tile in map_tiles:
                if tile.pos == coord:
                    # print('already placed')
                    valid_spot = False
                    break

            if valid_spot:
                sounds['place.wav'].play()

                placed_tile = deepcopy(selected_tile)
                placed_tile.real_pos = coord
                map_tiles.append(
                    placed_tile
                )

        elif inputs['held'].get('mouse3'):
            for i, tile in enumerate(map_tiles):
                if tile.pos == coord:
                    sounds['delete.wav'].play()
                    map_tiles.pop(i)
                    break

    canvas.fill(BG)

    for tile in map_tiles:
        tile.render(canvas, scroll)
        
    if mx > BORDER_W and 0:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill((100, 255, 255))
        s.set_alpha(50)
        canvas.blit(s, screen_coord)

    pygame.draw.aaline(canvas, (0, 0, 80), (0, +scroll[1]), (config.CANVAS_SIZE[0], +scroll[1]))
    pygame.draw.aaline(canvas, (0, 0, 80), (scroll[0], 0), (scroll[0], config.CANVAS_SIZE[1]))


    pygame.draw.rect(canvas, BG, pygame.Rect(0, 0, BORDER_W, config.CANVAS_SIZE[1]))
    pygame.draw.rect(canvas, (20, 20, 20), pygame.Rect(0, 0, BORDER_W, config.CANVAS_SIZE[1]), width=1)
    for tile in tiles:
        pygame.draw.rect(canvas, (30, 30, 30), tile.rect, 1)
        tile.render(canvas)
    if selected_tile:
        r = selected_tile.rect.inflate(4, 4)
        pygame.draw.rect(canvas, (0, 255, 100), r, width=2)

    if inputs['pressed'].get('s'):
        save_rooms(rooms)

    for name, button in buttons.items():
        button.update(inputs)
        if button.clicked:
            if name == 'decrease_room':
                if room_id[-1] > 0:
                    room_id[-1] -= 1
            elif name == 'increase_room':
                room_id[-1] += 1
        button.render(canvas)

    canvas.blit(FONTS['basic'].get_surf(f'Room ID: {'/'.join(str(e) for e in room_id)}'), (2, 2))
    screen.blit(pygame.transform.scale_by(canvas, config.scale), (0, 0))


    pygame.display.update()
    clock.tick(config.fps)

