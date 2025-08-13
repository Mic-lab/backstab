import pygame
import pygame.gfxdraw
import random
from .animation import Animation
from .entity import PhysicsEntity, Entity
from math import pi, cos, sin
from .timer import Timer
from .particle import ParticleGenerator

class Stab(Entity):
    # cache = {}
    # angle_skip = 5
    # for i in range(360/angle_skip):
    #     angle = i*angle_skip
    #     cache[angle] = pygame.transform.rotate(Animation.img_db)

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
    DASH_DURATION = 12
    DASH_SPEED = 7

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stab = None
        self.speed = 2
        self.dash_cooldown_timer = Timer(Player.DASH_COOLDOWN)
        self.dash_cooldown_timer.frame = Player.DASH_COOLDOWN
        self.dash_timer = Timer(Player.DASH_DURATION)
        self.dash_timer.frame = Player.DASH_DURATION
        self.dash_timer.done = True
        self.stab_radius = 50

    def render(self, surf, *args, **kwargs):
        # if self.stab: self.stab.render(surf)
        s = pygame.Surface((self.stab_radius*2, self.stab_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 200, 255), (self.stab_radius, self.stab_radius), self.stab_radius-8)  # just to feel fair for player cause it uses enemy rect (FIXME)
        s.set_alpha(50)
        surf.blit(s, self.rect.center - pygame.Vector2(self.stab_radius, self.stab_radius))
        super().render(surf, *args, **kwargs)

    def update(self, inputs, *args, **kwargs):
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
            self.dash_timer = Timer(Player.DASH_DURATION)
            self.dash_cooldown_timer = Timer(Player.DASH_DURATION + Player.DASH_COOLDOWN)

        if any(self.vel):
            self.animation.set_action('run')
        else:
            self.animation.set_action('idle')

        self.dash_cooldown_timer.update()
        self.dash_timer.update()

        super().update(*args, **kwargs)
        
        # if self.stab:
        #     self.update_stab_pos()
        #     done = self.stab.update()
        #     if done: self.stab = None
        # else:
        #     if inputs['pressed'].get('mouse1'):
        #         mouse_angle = (-pygame.Vector2(self.rect.center) + inputs['mouse pos']).angle_to(pygame.Vector2(0, 1))
        #         self.stab = Stab(angle=mouse_angle, pos=(0,0), name='stab', action='idle')
        #         self.update_stab_pos()
        #         output['stab'] = True
        self.stab = inputs['pressed'].get('mouse1')

        return output

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
            },
        },
    }
    
    def __init__(self, starting_view=0, view_width=10, *args, **kwargs):
        kwargs = Enemy.STATS[kwargs['name']]['entity'] | kwargs
        super().__init__(*args, **kwargs)

        self.view_angle = starting_view
        self.view_width = 0.15
        self.desire = 'idle'
        self.mode_timer = Timer(60)
        self.stats = Enemy.STATS[kwargs['name']]['enemy']

    @property
    def angle_1(self):
        return self.view_angle - 0.5*self.view_width*360

    @property
    def angle_2(self):
        return self.view_angle + 0.5*self.view_width*360

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
            
        self.run_angle = player_angle

        # if self.mode_timer.done:
        #     self.mode_timer = Timer(random.randint(40, 41))
        #     if self.desire == 'run':
        #         self.desire = 'idle'
        #     elif self.desire == 'idle':
        #         self.desire = 'run'
        #         # self.run_angle = random.uniform(player_angle-0.1, player_angle+0.1)
        #         print(f'{self.run_angle=}')
        # self.mode_timer.update()
        # if self.desire == 'run':
        #     self.animation.set_action('run')
        #     self.vel += 0.5*pygame.Vector2(cos(self.run_angle/180*pi),
        #                                    sin(self.run_angle/180*pi))
        #     # self.vel -= 0.1*pygame.Vector2(cos(self.run_angle), sin(self.run_angle))
        # else:
        #     self.animation.set_action('idle')
        #     self.vel *= 0.9

        self.animation.set_action('run')
        self.vel += 0.05*pygame.Vector2(cos(self.run_angle/180*pi),
                                       sin(self.run_angle/180*pi))

        for e in enemies:
            if e is self:
                continue
            d = pygame.Vector2(self.rect.center) - e.rect.center
            if d.length() < 20:
                self.vel += d*0.05


        # self.view_angle += 1

        # print(f'{self.view_angle=} {player_angle=}')

        # if abs(self.view_angle - player_angle) <= 2:
        #     self.view_angle = player_angle
        # else:


        
        if abs(self.view_angle - player_angle) < self.stats['turn_speed']:
            self.view_angle = player_angle
        else:
            big_angle = max(self.view_angle, player_angle)
            small_angle = next(iter({self.view_angle, player_angle} - {big_angle,}))
            if big_angle - small_angle > 180:
                direction = -1
            else:
                direction = 1
                
            if big_angle == self.view_angle:
                direction *= -1
            self.view_angle += direction*self.stats['turn_speed']



        self.view_angle = self.view_angle % 360

        # optional: check dist
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
        color = (255, 0, 50) if self.see_player else (200, 200, 200)

        # if not self.see_player or 1:
            # if self.player_dist.length() < self.player.stab_radius:
                # color = (0, 0, 255)
                # for i in range(1, 50):
                #     pygame.gfxdraw.pie(surf, *self.rect.center, i,
                #                        int(self.angle_1),
                #                        int(self.angle_2),
                #                        color)

        pygame.gfxdraw.pie(surf, *self.rect.center, 50,
                           int(self.angle_1),
                           int(self.angle_2),
                           color)

