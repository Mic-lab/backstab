import pygame
import pygame.gfxdraw
import random
from data.scripts import config
from data.scripts.pathfinding import PathFinder
from .animation import Animation
from .entity import PhysicsEntity, Entity
from .dash import Dash
from math import pi, cos, sin
from .timer import Timer
from .particle import ParticleGenerator
from abc import abstractmethod

class Stab(Entity):

    def __init__(self, angle, *args, **kwargs):
        self.angle = angle
        super().__init__(*args, **kwargs)

    @property
    def rect(self):
        self._rect = pygame.Rect(*self.pos, 32, 32)
        return self._rect

    @property
    def img(self):
        base_img = super().img
        return pygame.transform.rotate(base_img, self.angle)

class Player(PhysicsEntity):

    DASH_COOLDOWN = 20
    DASH_DURATION = 10
    DASH_SPEED = 9
    DASH_DURATION = 10
    DASH_SPEED = 8

    LOWEST_HIT_ALPHA = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timers = {}

        self.stab = None
        self.speed = 2
        self.stab_radius = 50
        self.invincible = False
        self.timers['dmg'] = Timer(60, start=False)

        self.dashes = []
        for _ in range(2): self.add_dash(Dash())

        self.ready_dash_i = 0
        self.timers['dash'] = Timer(Player.DASH_DURATION, start=False)

    def add_dash(self, dash):
        self.dashes.append(dash)

    @property
    def img(self):
        base_img = super().img.copy()
        if not self.timers['dmg'].done:
            base_img.set_alpha(Player.LOWEST_HIT_ALPHA + 0.5*(255 -
                Player.LOWEST_HIT_ALPHA) + (255 -
                    Player.LOWEST_HIT_ALPHA)*sin(self.timers['dmg'].ratio*50))
        return base_img

    def render(self, surf, *args, **kwargs):
        # if self.stab: self.stab.render(surf)
        s = pygame.Surface((self.stab_radius*2, self.stab_radius*2), pygame.SRCALPHA)
        offset = pygame.Vector2(args[0])  # Is this bad practice?
        # pygame.draw.circle(s, (200, 200, 255), (self.stab_radius, self.stab_radius), self.stab_radius-12, width=2)  # removing from stab radius just to feel fair for player cause it uses enemy rect (FIXME)
        s.set_alpha(50)
        surf.blit(s, self.rect.center+offset - pygame.Vector2(self.stab_radius, self.stab_radius))
        super().render(surf, *args, **kwargs)

    def update(self, offset, inputs, dangers, *args, **kwargs):
        output = {}

        if not self.timers['dash'].done:
            if self.timers['dash'].frame % 1 == 0:
                trail_surf = self.img.copy()
                trail_surf.set_alpha(150)
                trail = {
                    'surf': trail_surf,
                    'pos': self.pos,
                    'change': 20,
                }
                output['trail'] = trail
        else:
            self.max_vel = self.speed
            self.vel = pygame.Vector2()
            if inputs['held'].get('a'):
                self.vel[0] -= self.speed
                self.animation.flip[0] = True
            elif inputs['held'].get('d'):
                self.vel[0] += self.speed
                self.animation.flip[0] = False
            if inputs['held'].get('w'):
                self.vel[1] -= self.speed
            elif inputs['held'].get('s'):
                self.vel[1] += self.speed

        if inputs['pressed'].get('mouse1') and self.current_dash:
            self.current_dash.execute(self, inputs['mouse pos'] - pygame.Vector2(offset))

        if any(self.vel):
            self.animation.set_action('run')
        else:
            self.animation.set_action('idle')


        self.stab = inputs['pressed'].get('mouse1')

        if self.timers['dmg'].done:
            self.invincible = False
        for danger in dangers:
            if self.rect.colliderect(danger):
                successful_hit = self.take_dmg()
                if successful_hit:
                    output = output | {'hit': True}
                break

        if self.ready_dash_i < len(self.dashes) - 1:
            next_dash = self.dashes[self.ready_dash_i + 1]
            next_dash.update(self)
            if next_dash.ready:
                if self.ready_dash_i != len(self.dashes):
                    print(f'{self.ready_dash_i} is ready')
                    self.ready_dash_i += 1 

        for timer in self.timers.values():
            timer.update()

        super().update(*args, **kwargs)
        return output

    def dash(self, mouse_pos):
        print('dashing')
        print(f'reseting dash {self.ready_dash_i}')
        self.ready_dash_i -= 1
        self.max_vel = Player.DASH_SPEED
        self.vel = pygame.Vector2(self.vel)
        vel = mouse_pos - pygame.Vector2(self.rect.center)
        self.vel = vel
        self.vel.scale_to_length(Player.DASH_SPEED)
        self.timers['dash'].reset()

    @property
    def current_dash(self):
        if self.ready_dash_i < 0: return None

        return self.dashes[self.ready_dash_i if self.ready_dash_i < len(self.dashes) else len(self.dashes) - 1]

    def take_dmg(self):
        if self.invincible:
            return
        self.invincible = True
        self.timers['dmg'].reset()
        return True

    def get_angle_pos(self, angle, radius=20):
        return self.rect.center + radius*pygame.Vector2(sin(angle/180*pi),
                                                        cos(angle/180*pi))
    def update_stab_pos(self):
        # r = self.stab.rect.copy()
        r = pygame.Rect(0,0, *self.stab.img.get_size())
        r.center = self.get_angle_pos(self.stab.angle)
        self.stab.real_pos = r.topleft
        # self.stab.real_pos = self.get_angle_pos(self.stab.angle)



class Enemy(PhysicsEntity):

    STATS = {
        'civilian': {
            'entity':{
                'max_vel': 0.7,
            },
            'enemy':{
                'turn_speed': 2,
                'acceleration': 0.5,
            },
        },
        'eye': {
            'entity':{
                'max_vel': 0.5,
            },
            'enemy':{
                'acceleration': 0.2,
            },
        },
    }
    
    def __init__(self, starting_view=0, view_width=0.1, *args, **kwargs):
        kwargs = Enemy.STATS[kwargs['name']]['entity'] | kwargs
        super().__init__(*args, **kwargs)

        self.view_angle = starting_view
        self.view_width = view_width
        self.desire = 'idle'
        self.mode_timer = Timer(60)
        self.stats = Enemy.STATS[kwargs['name']]['enemy']

        self.target = None
        self.update_path_timer = Timer(20, start=False)
        self.path_finder = None

    # NOTE: A bit redundant
    @property
    def angle_1(self):
        if self.view_width == 1:  # -1 Hard coded to be considered as 360 degrees. Usually it would do 0 degrees.
            return -1
        angle_1 = self.view_angle - 0.5*self.view_width*360
        angle_1 = angle_1 % 360
        if angle_1 < 0: angle_1 = 360 - abs(angle_1)
        return angle_1

    @property
    def angle_2(self):
        if self.view_width == 1:
            return -1
        angle_2 = self.view_angle + 0.5*self.view_width*360
        angle_2 = angle_2 % 360
        if angle_2 < 0: angle_2 = 360 - abs(angle_2)
        return angle_2

    def find_path(self, game_map):
        if self.path_finder:
            my_tile_pos = int(self.rect.center[0] // config.TILE_SIZE[0]), int(self.rect.center[1] // config.TILE_SIZE[1])
            player_tile_pos = int(self.player.rect.center[0] // config.TILE_SIZE[0]), int(self.player.rect.center[1] // config.TILE_SIZE[1])
            if my_tile_pos == player_tile_pos:
                self.path = []
            else:
                self.path = self.path_finder.get_path(game_map, my_tile_pos, player_tile_pos)
                self.path.reverse()
        else:
            self.path = None

    def follow_path(self):
        if self.path:

            if self.target:
                if (self.target - self.rect.center).length() < 15:
                    self.path.pop(0)

            if len(self.path) >= 2:
                target = self.path[1].x*config.TILE_SIZE[0], self.path[1].y*config.TILE_SIZE[1]
                target += 0.5*pygame.Vector2(config.TILE_SIZE)
                vel_change = -pygame.Vector2(self.rect.center) + target

                if vel_change.length() == 0:
                    vel_change = pygame.Vector2(0, 1)
                else:
                    vel_change.scale_to_length(1)

#             print(f'''
# My center: {self.rect.center}
# Target's center: {target} ({self.path[0].x, self.path[0].y})
# {vel_change=}
#             ''')

                self.target = target
                self.vel += self.stats['acceleration']*vel_change
            else:
                self.target = pygame.Vector2(self.player.rect.center)
        else:
            self.goto_player()


    @abstractmethod
    def update_behavior(self):
        pass

    def distance_from_enemies(self, enemies):
        for e in enemies:
            if e is self:
                continue
            d = pygame.Vector2(self.rect.center) - e.rect.center
            if d.length() < 20:
                self.vel += d*0.05

    def update(self, game_map, player, enemies, *args, **kwargs):
        output = {}

        self.player = player
        self.player_dist = player.rect.center - pygame.Vector2(self.rect.center)
        if self.player_dist == 0:
            player_angle = 0
        else:
            player_angle = pygame.Vector2(1, 0).angle_to(self.player_dist)
            player_angle = self.player_dist.angle_to(pygame.Vector2(1, 0))
            player_angle = pygame.Vector2(1, 0).angle_to(self.player_dist)
        if player_angle < 0:
            player_angle = 360 - abs(player_angle)
        self.player_angle = player_angle

        if self.update_path_timer.done:
            self.update_path_timer.reset()
            self.find_path(game_map)
        self.follow_path()
        self.update_behavior()
        self.distance_from_enemies(enemies)

        # optional: check dist
        if self.view_width == 1:
            self.see_player = True
        elif self.angle_1 > self.angle_2:
            self.see_player = self.angle_1 < player_angle or self.angle_2 > player_angle
        else:
            self.see_player = self.angle_1 < player_angle < self.angle_2

        self.update_path_timer.update()

        hit_output = self.process_hits(player)
        output = output | hit_output
                
        super().update(*args, **kwargs)
        return output

    def process_hits(self, player):
        output = {}
        if player.stab:

            # if self.rect.colliderect(player.stab.rect):
            if not self.see_player:
                if self.player_dist.length() < player.stab_radius:
                        output['dead'] = True

        return output

    def render(self, surf, offset, *args, **kwargs):
        super().render(surf, offset, *args, **kwargs)

        # Path finding displya

        if self.path:
            s = pygame.Surface(surf.get_size())
            s.set_colorkey((0, 0, 0))
            for i, tile in enumerate(self.path):
                if i == len(self.path) - 1:
                    pygame.draw.rect(s, (0, 255, 0), ((tile.x)*24+offset[0], offset[1]+tile.y*24, 24, 24))
                else:
                    pygame.draw.rect(s, (200, 200-i*10, 200), ((tile.x)*24+offset[0], offset[1]+tile.y*24, 24, 24))
            s.set_alpha(20)
            surf.blit(s, (0,0))
            surf.set_at((self.target[0]+offset[0], self.target[1]+offset[1]), (0, 255, 255))
            surf.set_at(pygame.Vector2(self.rect.center) + offset, (255, 0, 255))

        # bye bye!
        # color = (255, 0, 50) if self.see_player else (200, 200, 200)

        # if not self.see_player or 1:
        #     if self.player_dist.length() < self.player.stab_radius:
        #         color = (0, 0, 255)
        #         for i in range(1, 50):
        #             pygame.gfxdraw.pie(surf, *self.rect.center, i,
        #                                int(self.angle_1),
        #                                int(self.angle_2),
        #                                color)

        # pygame.gfxdraw.pie(surf, *self.rect.center, 50,
        #                    int(self.angle_1),
        #                    int(self.angle_2),
        #                    color)

    # Methods that can be used for update behavior --------------------------- #
    # NOTE: May require certain keys to be in STATS

    def goto_player(self):
        self.vel += self.stats['acceleration']*pygame.Vector2(cos(self.player_angle/180*pi), sin(self.player_angle/180*pi))


class BasicEnemy(Enemy):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_finder = PathFinder()

    def update_behavior(self):
        self.animation.set_action('run')
        # self.goto_player()
        if abs(self.view_angle - self.player_angle) < self.stats['turn_speed']:
            self.view_angle = self.player_angle
        else:
            big_angle = max(self.view_angle, self.player_angle)
            small_angle = next(iter({self.view_angle, self.player_angle} - {big_angle,}))
            if big_angle - small_angle > 180:
                direction = -1
            else:
                direction = 1
            if big_angle == self.view_angle:
                direction *= -1
            self.view_angle += direction*self.stats['turn_speed']
            self.view_angle = self.view_angle % 360

class Eye(Enemy):

    def __init__(self, *args, **kwargs):
        super().__init__(view_width=1, *args, **kwargs)
        self.open_timer = Timer(100)
        self.path_finder = PathFinder()

    def update_behavior(self):
        if self.open_timer.done:
            if self.animation.action == 'opened':
                self.animation.set_action('closed')
                self.view_width = 0
            elif self.animation.action == 'closed':
                self.animation.set_action('opened')
                self.view_width = 1
            self.open_timer.reset()
        self.open_timer.update()
