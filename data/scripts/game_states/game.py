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
            Enemy(pos=(250, 100), name='civilian', action='idle'),
        ])

        self.dead_enemies = []
        
        self.gens = []
        self.game_map = GameMap()
        self.trails = []
        self.los = []

    def sub_update(self):

        # self.handler.canvas.fill((80, 80, 80))
        # self.handler.canvas.fill((40, 30, 50))
        # self.handler.canvas.fill((50, 50, 60))
        self.handler.canvas.fill(config.COLORS['ground'])

        self.game_map.render(self.handler.canvas)

        collisions = []
        for tile in self.game_map.tiles:
            if tile.collision:
                collisions.append(tile.rect)

        # for c in collisions:
        #     pygame.draw.rect(self.handler.canvas, (200, 200, 0), c)

        new_trails = []
        for trail in self.trails:
            img = trail['surf']
            self.handler.canvas.blit(img, trail['pos'])
            new_alpha = img.get_alpha() - trail['change']
            if new_alpha > 0:
                img.set_alpha(new_alpha)
                new_trails.append(trail)
        self.trails = new_trails

        new_dead_enemies = []
        for enemy in self.dead_enemies:
            enemy.animation.set_action('idle')
            enemy.render(self.handler.canvas)
            done = enemy.stab.update()
            if not done:
                new_dead_enemies.append(enemy)
                enemy.stab.render(self.handler.canvas)
        self.dead_enemies = new_dead_enemies

        new_enemies = []
        for enemy in self.enemies:
            update_data = enemy.update(self.player, self.enemies, collisions)
            if update_data.get('dead'):
                self.dead_enemies.append(enemy)
                stab_w = animation.Animation.animation_db['stab']['rect'].w
                enemy.stab = Entity(enemy.rect.center- pygame.Vector2(stab_w, 0), 'stab', 'idle')
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

        if update_data.get('trail'):
            self.trails.append(update_data['trail'])

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

        shader_handler.vars['los'] = self.los
