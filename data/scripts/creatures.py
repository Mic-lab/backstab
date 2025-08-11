import pygame
import pygame.gfxdraw
import random
from .entity import PhysicsEntity
from math import pi, cos, sin
from .timer import Timer
from .particle import ParticleGenerator

class Player(PhysicsEntity):
    speed = 1.5

    def update(self, inputs, *args, **kwargs):
        output = {}

        self.vel = [0, 0]
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

        if inputs['pressed'].get('space'):
            output['stab'] = True

        if any(self.vel):
            self.animation.set_action('run')
        else:
            self.animation.set_action('idle')
        super().update([])

        return output



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
        if self.mode_timer.done:
            self.mode_timer = Timer(random.randint(30, 60))
            if self.desire == 'run':
                self.desire = 'idle'
            elif self.desire == 'idle':
                self.desire = 'run'
                self.run_angle = random.uniform(0, 2*pi)
        self.mode_timer.update()

        if self.desire == 'run':
            self.animation.set_action('run')
            self.vel += 0.00*pygame.Vector2(cos(self.run_angle), sin(self.run_angle))
            # self.vel -= 0.1*pygame.Vector2(cos(self.run_angle), sin(self.run_angle))
        else:
            self.animation.set_action('idle')
            self.vel *= 0.9

        dist = player.pos - self.pos
        player_angle = pygame.Vector2(1, 0).angle_to(dist)
        player_angle = dist.angle_to(pygame.Vector2(1, 0))
        player_angle = pygame.Vector2(1, 0).angle_to(dist)
        if player_angle < 0:
            player_angle = 360 - abs(player_angle)
            
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
