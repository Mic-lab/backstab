import json
import pygame
from pygame import Vector2
import sys
from copy import deepcopy
from data.scripts import config
from copy import deepcopy
from data.scripts.sfx import sounds
from data.scripts import utils
from data.scripts.game_map import Tile
from data.scripts.font import FONTS

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

    print(f'{rooms=}')
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
    print(f'{rooms=}')
    print()
    json_rooms = deepcopy(rooms)
    for category, rooms in rooms['all'].items():
        for i, room in enumerate(rooms):
            print(f'{room=}')
            for j, tile in enumerate(room):
                print(f'{tile=}')
                json_rooms['all'][category][i][j] = tile.get_serialized()
    with open(path, 'w') as f:
        json.dump(json_rooms, f)



BORDER_W = 24*4
TILE_SIZE = 24
BASE_PAN = (2, 16)
PAN = 2

config.scale = 3
config.screen_size = Vector2(config.CANVAS_SIZE) * config.scale
screen = pygame.display.set_mode(config.screen_size)
canvas = pygame.Surface(config.CANVAS_SIZE + Vector2(0, BORDER_W))
clock = pygame.time.Clock()

tiles_str = [
    ('tl_wall', 'top_wall', 'tr_wall'),
    ('left_wall', 'ground', 'right_wall'),
    ('bl_wall', 'bottom_wall', 'br_wall'),
    ('rock',),
]

rooms = load_rooms()
tiles = get_base_tiles()
room_id = ('normal', 0)

selected_tile = None
scroll = [0, 0]
# scroll = [100, 30]

mx, my = 0, 0

mouse_down_left = False
mouse_down_right = False
wheel_down = False
shift_down = False

running = True
while running:

    old_mx = mx
    old_my = my
    mx, my = pygame.mouse.get_pos()
    mx = mx // config.scale
    my = my // config.scale
    
    left_click = False
    right_click = False
    s_pressed = False

    # screen_coord = Vector2(mx, my) // TILE_SIZE * TILE_SIZE
    # coord = (Vector2(mx, my) - scroll) // TILE_SIZE * TILE_SIZE
    # screen_coord = coord
    coord = (Vector2(mx, my) - scroll) // TILE_SIZE * TILE_SIZE
    screen_coord = Vector2(mx, my) // TILE_SIZE * TILE_SIZE + Vector2(scroll[0]%TILE_SIZE, scroll[1]%TILE_SIZE)  # struggling to figure this out

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                left_click = True
                mouse_down_left = True
                if mx <= BORDER_W:
                    for tile in tiles:
                        if tile.rect.collidepoint(mx, my):
                            selected_tile = tile
                            break
            if event.button == 3:
                right_click = True
                mouse_down_right = True

            if event.button == 2:
                wheel_down = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_down_left = False
            elif event.button == 3:
                mouse_down_right = False
            elif event.button == 2:
                wheel_down = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                shift_down = True
            if event.key == pygame.K_s:
                s_pressed = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                shift_down = False

    if room_id[1] == len(rooms['all'][room_id[0]]):
        rooms['all'][room_id[0]].append([])
    map_tiles = rooms['all'][room_id[0]][room_id[1]]

    if wheel_down:
        delta = Vector2(mx, my) - Vector2(old_mx, old_my)
        scroll += delta

    if mx > BORDER_W:
        if mouse_down_left:
            if selected_tile:

                if shift_down:
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

        elif mouse_down_right:
            if shift_down:
                if right_click:
                    for i, tile in enumerate(map_tiles):
                        if tile.pos == coord:
                            sounds['delete.wav'].play()
                            if len(tile.name) > 1:
                                tile.name.pop(-1)
                                map_tiles[i] = Tile(pos=tile.pos, name=tile.name)
                            else:
                                map_tiles.pop(i)
                            break
            else:
                for i, tile in enumerate(map_tiles):
                    if tile.pos == coord:
                        sounds['delete.wav'].play()
                        map_tiles.pop(i)
                        break

    canvas.fill((80, 80, 80))

    for tile in map_tiles:
        tile.render(canvas, scroll)
        
    if mx > BORDER_W and 0:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill((100, 255, 255))
        s.set_alpha(50)
        canvas.blit(s, screen_coord)

    pygame.draw.aaline(canvas, (30, 30, 30), (0, +scroll[1]), (config.CANVAS_SIZE[0], +scroll[1]))
    pygame.draw.aaline(canvas, (30, 30, 30), (scroll[0], 0), (scroll[0], config.CANVAS_SIZE[1]))


    pygame.draw.rect(canvas, (50, 50, 50), pygame.Rect(0, 0, BORDER_W, config.CANVAS_SIZE[1]))
    for tile in tiles:
        pygame.draw.rect(canvas, (30, 30, 30), tile.rect, 1)
        tile.render(canvas)
    if selected_tile:
        r = selected_tile.rect.inflate(4, 4)
        pygame.draw.rect(canvas, (0, 255, 100), r, width=2)

    if s_pressed:
        save_rooms(rooms)

    canvas.blit(FONTS['basic'].get_surf(f'Room ID: {'/'.join(str(e) for e in room_id)}'), (2, 2))

    screen.blit(pygame.transform.scale_by(canvas, config.scale), (0, 0))


    pygame.display.update()
    clock.tick(config.fps)

