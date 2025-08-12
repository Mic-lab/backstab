import pygame
import pygame.gfxdraw
import random
from .entity import PhysicsEntity, Entity
from math import pi, cos, sin
from .timer import Timer
from .particle import ParticleGenerator

class Player(PhysicsEntity):

    DASH_COOLDOWN = 20
    DASH_DURATION = 12
    DASH_SPEED = 6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stab = None
        self.speed = 2
        self.dash_cooldown_timer = Timer(Player.DASH_COOLDOWN)
        self.dash_cooldown_timer.frame = Player.DASH_COOLDOWN
        self.dash_timer = Timer(Player.DASH_DURATION)
        self.dash_timer.frame = Player.DASH_DURATION

    def render(self, surf, *args, **kwargs):
        if self.stab: self.stab.render(surf)
        super().render(surf, *args, **kwargs)

    def update(self, inputs, *args, **kwargs):
        output = {}

        if not self.dash_timer.done:
            print('dashing')
            pass
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
        
        if self.stab:
            self.stab.real_pos = self.stab_pos
            done = self.stab.update()
            if done: self.stab = None
        else:
            if inputs['pressed'].get('mouse1'):
                self.stab = Entity(pos=(0,0), name='stab', action='idle')
                self.stab = Entity(pos=self.stab_pos, name='stab', action='idle')
                output['stab'] = True

        return output

    @property
    def stab_pos(self):
        return self.rect.midbottom - pygame.Vector2(self.stab.img.get_width()*0.5, 0)



class Enemy(PhysicsEntity):

    STATS = {
        'civilian': {
            'entity':{
                'max_vel': 1,
            },
            'enemy':{
                'turn_speed': 1,
            },
        },
    }
    
    def __init__(self, starting_view=0, view_width=10, *args, **kwargs):
        kwargs = Enemy.STATS[kwargs['name']]['entity'] | kwargs
        super().__init__(*args, **kwargs)

        self.view_angle = starting_view
        self.view_width = 0.1
        self.desire = 'idle'
        self.mode_timer = Timer(60)
        self.stats = Enemy.STATS[kwargs['name']]['enemy']

    @property
    def angle_1(self):
        return self.view_angle - 0.5*self.view_width*360

    @property
    def angle_2(self):
        return self.view_angle + 0.5*self.view_width*360

    def update(self, player, *args, **kwargs):
        dist = player.pos - self.pos
        if dist == 0:
            player_angle = 0
        else:
            player_angle = pygame.Vector2(1, 0).angle_to(dist)
            player_angle = dist.angle_to(pygame.Vector2(1, 0))
            player_angle = pygame.Vector2(1, 0).angle_to(dist)
        if player_angle < 0:
            player_angle = 360 - abs(player_angle)
            

        if self.mode_timer.done:
            self.mode_timer = Timer(random.randint(40, 41))
            if self.desire == 'run':
                self.desire = 'idle'
            elif self.desire == 'idle':
                self.desire = 'run'
                # self.run_angle = random.uniform(player_angle-0.1, player_angle+0.1)
                self.run_angle = player_angle
                print(f'{self.run_angle=}')
        self.mode_timer.update()

        if self.desire == 'run':
            self.animation.set_action('run')
            self.vel += 0.5*pygame.Vector2(cos(self.run_angle/180*pi),
                                           sin(self.run_angle/180*pi))
            # self.vel -= 0.1*pygame.Vector2(cos(self.run_angle), sin(self.run_angle))
        else:
            self.animation.set_action('idle')
            self.vel *= 0.9

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



        super().update(*args, **kwargs)

    def render(self, surf, *args, **kwargs):
        super().render(surf, *args, **kwargs)
        color = (255, 0, 50) if self.see_player else (200, 200, 200)
        pygame.gfxdraw.pie(surf, *self.rect.center, 50,
                           int(self.angle_1),
                           int(self.angle_2),
                           color)
