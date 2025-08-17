import pygame
import pygame.gfxdraw
import random
from .animation import Animation
from .entity import PhysicsEntity, Entity
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

    DASH_COOLDOWN = 15
    DASH_DURATION = 12
    DASH_SPEED = 7

    LOWEST_HIT_ALPHA = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stab = None
        self.speed = 2
        self.dash_cooldown_timer = Timer(Player.DASH_DURATION + Player.DASH_COOLDOWN, start=False)
        self.dash_timer = Timer(Player.DASH_DURATION, start=False)
        self.dash_timer.done = True
        self.stab_radius = 50
        self.invincible = False
        self.dmg_timer = Timer(60, start=False)

    @property
    def img(self):
        base_img = super().img.copy()
        if not self.dmg_timer.done:
            base_img.set_alpha(Player.LOWEST_HIT_ALPHA + 0.5*(255 -
                Player.LOWEST_HIT_ALPHA) + (255 -
                    Player.LOWEST_HIT_ALPHA)*sin(self.dmg_timer.ratio*50))
        return base_img

    def render(self, surf, *args, **kwargs):
        # if self.stab: self.stab.render(surf)
        s = pygame.Surface((self.stab_radius*2, self.stab_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 200, 255), (self.stab_radius, self.stab_radius), self.stab_radius-12, width=2)  # removing from stab radius just to feel fair for player cause it uses enemy rect (FIXME)
        s.set_alpha(50)
        surf.blit(s, self.rect.center - pygame.Vector2(self.stab_radius, self.stab_radius))
        super().render(surf, *args, **kwargs)

    def update(self, inputs, dangers, *args, **kwargs):
        output = {}

        if not self.dash_timer.done:
            if self.dash_timer.frame % 2 == 0:
                trail_surf = self.img.copy()
                trail_surf.set_alpha(150)
                trail = {
                    'surf': trail_surf,
                    'pos': self.pos.copy(),
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

        # print(self.dash_cooldown_timer, self.dash_cooldown_timer.done)
        # print(f'{self.vel=} {type(self.vel)}')
        if inputs['pressed'].get('space') and self.dash_cooldown_timer.done and self.vel != (0, 0):
            self.max_vel = Player.DASH_SPEED
            self.vel = pygame.Vector2(self.vel)
            self.vel.scale_to_length(Player.DASH_SPEED)
            self.dash_timer.reset()
            self.dash_cooldown_timer.reset()

        if any(self.vel):
            self.animation.set_action('run')
        else:
            self.animation.set_action('idle')


        self.stab = inputs['pressed'].get('mouse1')

        if self.dmg_timer.done:
            self.invincible = False
        for danger in dangers:
            if self.rect.colliderect(danger):
                successful_hit = self.take_dmg()
                if successful_hit:
                    output = output | {'hit': True}
                break

        # TODO: Make dict for this
        self.dash_cooldown_timer.update()
        self.dash_timer.update()
        self.dmg_timer.update()

        super().update(*args, **kwargs)
        return output

    def take_dmg(self):
        if self.invincible:
            return
        self.invincible = True
        self.dmg_timer.reset()
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

    def update(self, player, enemies, *args, **kwargs):
        output = {}

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

        self.update_behavior()
        self.distance_from_enemies(enemies)

        # optional: check dist
        if self.view_width == 1:
            self.see_player = True
        elif self.angle_1 > self.angle_2:
            self.see_player = self.angle_1 < player_angle or self.angle_2 > player_angle
        else:
            self.see_player = self.angle_1 < player_angle < self.angle_2

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

    def render(self, surf, *args, **kwargs):
        super().render(surf, *args, **kwargs)

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

    def update_behavior(self):
        self.animation.set_action('run')
        self.goto_player()
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
        print(f'{self.angle_1=} {self.angle_2=} {self.view_angle=}')

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

        self.goto_player()
