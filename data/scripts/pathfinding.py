# https://www.youtube.com/watch?v=-L-WgKMFuhE
from copy import deepcopy
from time import perf_counter

class Tile:

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.g = None  # distance from starting tile
        self.h = None  # distance from end node
        self.f = None  # g + h
        self.parent = None

    def update(self, potential_parent, start, end):
        if self.h is None:
            self.calc_h(end)

        # if self.x == potential_parent.x or self.y == potential_parent.y:
        #     parent_dist = 10
        # else:
        #     parent_dist = 14
        if abs(self.x - potential_parent.x) == 1 and abs(self.y - potential_parent.y) == 1:
            parent_dist = 14  # diagonal
        else:
            parent_dist = 10  # straight

        if potential_parent is start:
            potential_g = parent_dist
        else:
            potential_g = potential_parent.g + parent_dist

        if self.g is None or potential_g < self.g:
            self.parent = potential_parent
            self.g = potential_g
            self.f = self.g + self.h

    def calc_h(self, end):
        end_dist = (abs(self.x - end.x), abs(self.y - end.y))
        if end_dist[0] > end_dist[1]:
            big = end_dist[0]
            small = end_dist[1]
        else:
            big = end_dist[1]
            small = end_dist[0]
        diagonals = small
        horizontals = big - small
        self.h = (diagonals * 14 + horizontals * 10) *1.001
        # self.h = abs(self.x - end.x) * 10 + abs(self.y - end.y) * 10
        # self.h = (abs(self.x - end.x)**2 + abs(self.y - end.y)**2) ** 0.5

    def __repr__(self):
        return f'({self.x}, {self.y})'

def get_grid(grid_inp, start_coord, end_coord):
    grid_inp[start_coord[1]][start_coord[0]] = 2
    grid_inp[end_coord[1]][end_coord[0]] = 3

    # from pprint import pprint
    # pprint(grid_inp)

    grid = []
    for y, row in enumerate(grid_inp):
        grid.append([])
        for x, tile_num in enumerate(row):
            if tile_num == 1:
                tile = False
            else:
                tile = Tile(x, y)
                if tile_num == 2:
                    start = tile
                elif tile_num == 3:
                    end = tile
            grid[y].append(tile)
    return grid, start, end

class PathFinder:

    neighbor_offset = set()
    for x in range(-1, 2):
        for y in range(-1, 2):
            coord = (x, y)
            if coord == (0, 0):
                continue
            neighbor_offset.add(coord)

    # neighbor_offset = {(-1, 0), (1, 0), (0, -1), (0, 1)}

    def __init__(self):
        pass

    def get_path(self, game_map, start, end):
        grid, grid_size = deepcopy(game_map.grid), game_map.map_size
        # start = grid[int(start[1])][int(start[0])]
        # end = grid[int(end[1])][int(end[0])]
        # print(f'{grid=}')
        # print(f'{start=}')
        grid, start, end = get_grid(grid, start, end)
        self.calc_path(grid, start, end, grid_size)

        path = [end]
        current = end
        while True:
            path.append(current.parent)
            current = current.parent
            if current is start:
                path.append(current)
                return path

    @classmethod
    def calc_path(cls, grid, start, end, grid_size):
        t0 = perf_counter()

        open_tiles = {start}
        close_tiles = set()

        while True:
            # current = min(open_tiles, key=lambda e: e.f)
            current = next(iter(open_tiles))
            for tile in open_tiles:
                if tile.f is None: continue
                if tile.f == current.f:
                    if tile.g < current.f:
                        current = tile
                elif tile.f < current.f:
                    current = tile
            
            open_tiles.remove(current) # can be optimized with pop
            close_tiles.add(current)

            if current is end:
                t1 = perf_counter()
                time_taken = round(t1 - t0, 4)
                if time_taken >= 0.0002:
                    print(f'close_tiles explored {len(close_tiles)} ({time_taken} s)')
                return

            for offset in cls.neighbor_offset:
                x, y = current.x - offset[0], current.y - offset[1]

                if x < 0 or y < 0 or x == grid_size[0] or y == grid_size[1]:
                    continue

                neighbor_tile = grid[y][x]
                if not neighbor_tile or neighbor_tile in close_tiles:
                    continue
                neighbor_tile.update(current, start, end)
                open_tiles.add(neighbor_tile)
