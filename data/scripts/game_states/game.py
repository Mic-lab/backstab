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
from ..game_map import GameMap
import pygame
import pygame.gfxdraw

class Game(State):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.player = Player(pos=(150, 40), name='side', action='idle')
        self.e_speed = 1.5

        self.enemies = []

        self.enemies.extend([
            Enemy(pos=(200, 200), name='civilian', action='idle'),
            Enemy(pos=(250, 200), name='civilian', action='idle'),
            Enemy(pos=(250, 100), name='civilian', action='idle'),
            Enemy(pos=(200, 100), name='civilian', action='idle'),
        ])
        
        self.gens = []
        self.game_map = GameMap()

    def sub_update(self):

        self.handler.canvas.fill((80, 80, 80))
        self.handler.canvas.fill((40, 30, 50))
        self.handler.canvas.fill((50, 50, 60))

        self.game_map.render(self.handler.canvas)

        collisions = [tile.rect for tile in self.game_map.tiles]

        # for c in collisions:
        #     pygame.draw.rect(self.handler.canvas, (200, 200, 0), c)

        new_enemies = []
        for enemy in self.enemies:
            update_data = enemy.update(self.player, self.enemies, collisions)
            if update_data.get('dead'):
                continue

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

            new_enemies.append(enemy)
        self.enemies = new_enemies

        update_data = self.player.update(self.handler.inputs, collisions)

        self.player.render(self.handler.canvas)

        self.gens = ParticleGenerator.update_generators(self.gens)
        for particle_gen in self.gens:
            # particle_name = particle_gen.base_particle.animation.action
            # if particle_name == 'stab':
            #     for particle in particle_gen.particles:
            #         particle.real_pos = self.player.rect.midbottom
            particle_gen.render(self.handler.canvas)

        text = [f'{round(self.handler.clock.get_fps())} fps',
                f'vel = {self.player.vel}',
                # pprint.pformat(Particle.cache)
                ]
        self.handler.canvas.blit(FONTS['basic'].get_surf('\n'.join(text)), (0, 0))
