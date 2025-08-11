from .state import State
from ..mgl import shader_handler
from ..import utils
from ..button import Button
from ..font import FONTS
from ..import animation
from ..entity import Entity, PhysicsEntity
from ..creatures import Enemy, Player
from ..timer import Timer
from ..particle import Particle, ParticleGenerator
from .. import sfx
from .. import screen, config
import pygame
import pygame.gfxdraw

class Game(State):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.player = Player(pos=(150, 30), name='side', action='idle')
        self.e_speed = 1.5

        self.enemies = []

        self.enemies.append(
            Enemy(pos=(200, 200), name='civilian', action='idle')
        )
        
        self.gens = []

    def sub_update(self):

        self.handler.canvas.fill((20, 20, 20))

        for enemy in self.enemies:
            enemy.update(self.player, [])
            enemy.render(self.handler.canvas)

            dist = self.player.pos - enemy.pos
            angle = dist.angle_to(pygame.Vector2(1, 0))
            angle = pygame.Vector2(1, 0).angle_to(dist)
            if angle < 0:
                angle = 360 - abs(angle)
            # angle = dist.angle_to(pygame.Vector2(1, 0))
            # print(f'{angle=}')
            pygame.gfxdraw.pie(self.handler.canvas, *enemy.rect.center, 50,
                               int(angle),

                               int(angle)+1,
                               (0, 200, 200))

        update_data = self.player.update(self.handler.inputs, [])
        if update_data.get('stab'):
            self.gens.append(
                ParticleGenerator.from_template(self.player.rect.midbottom, 'stab')
            )

        self.player.render(self.handler.canvas)

        self.gens = ParticleGenerator.update_generators(self.gens)
        for particle_gen in self.gens:
            particle_gen.render(self.handler.canvas)

        text = [f'{round(self.handler.clock.get_fps())} fps',
                f'vel = {self.player.vel}',
                # pprint.pformat(Particle.cache)
                ]
        self.handler.canvas.blit(FONTS['basic'].get_surf('\n'.join(text)), (0, 0))
