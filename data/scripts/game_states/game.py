from .state import State
from ..mgl import shader_handler
from ..import utils
from ..button import Button
from ..font import FONTS
from ..import animation
from ..entity import Entity, PhysicsEntity
from ..creatures import Enemy, Player, BasicEnemy, Eye
from ..timer import Timer
from ..particle import Particle, ParticleGenerator
from .. import sfx
from .. import screen, config
from ..game_map import GameMap
from ..health import Health
import pygame
import pygame.gfxdraw

class Game(State):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.player = Player(pos=(150, 40), name='side', action='idle')
        self.e_speed = 1.5
        self.health = Health()

        self.game_map = GameMap()

        self.enemies = []
        self.enemies.extend([
            BasicEnemy(pos=(200, 200), name='civilian', action='idle'),
            BasicEnemy(pos=(250, 200), name='civilian', action='idle'),
            BasicEnemy(pos=(250, 100), name='civilian', action='idle'),
            Eye(pos=(250, 100), name='eye', action='opened'),
        ])

        self.timers = {
            'hit': Timer(30, start=False)
        }
        self.dead_enemies = []
        self.gens = []
        self.trails = []

    def sub_update(self):
        shader_handler.vars['los'] = []
        shader_handler.vars['losType'] = []

        # self.handler.canvas.fill((80, 80, 80))
        # self.handler.canvas.fill((40, 30, 50))
        # self.handler.canvas.fill((50, 50, 60))
        # self.handler.canvas.fill(config.COLORS['ground'])
        self.handler.canvas.fill((0, 0, 0))

        self.game_map.render(self.handler.canvas)

        self.dangers = []
        collisions = self.game_map.collision_tiles  # NOTE: same reference

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
            shader_handler.vars['los'].append((
                enemy.rect.centerx / config.CANVAS_SIZE[0],
                enemy.rect.centery / config.CANVAS_SIZE[1],
                enemy.angle_1, enemy.angle_2))
            shader_handler.vars['losType'].append(0 if enemy.see_player else 1)

            # if enemy.angle_1 == -1:
            #     print(shader_handler.vars['los'][-1])
            #     print(shader_handler.vars['losType'][-1])

            dist = self.player.pos - enemy.pos
            angle = dist.angle_to(pygame.Vector2(1, 0))
            angle = pygame.Vector2(1, 0).angle_to(dist)
            if angle < 0:
                angle = 360 - abs(angle)
            # pygame.gfxdraw.pie(self.handler.canvas, *enemy.rect.center, 50,
            #                    int(angle),
            #
            #                    int(angle)+1,
            #                    (0, 200, 200))
            
            self.dangers.append(enemy.rect)

            new_enemies.append(enemy)

        self.enemies = new_enemies

        update_data = self.player.update(self.handler.inputs, self.dangers, collisions)

        if update_data.get('trail'):
            self.trails.append(update_data['trail'])
        if update_data.get('hit'):
            self.timers['hit'].reset()
            self.health.change_hp(-1, self.gens)

        self.player.render(self.handler.canvas)

        self.health.update()
        self.health.render(self.handler.canvas)

        self.gens = ParticleGenerator.update_generators(self.gens)
        for particle_gen in self.gens:
            # particle_name = particle_gen.base_particle.animation.action
            # if particle_name == 'stab':
            #     for particle in particle_gen.particles:
            #         particle.real_pos = self.player.rect.midbottom
            particle_gen.render(self.handler.canvas)

        shader_handler.vars['hitTimer'] = -1 if self.timers['hit'].done else self.timers['hit'].ratio

        for timer_name, timer_obj in self.timers.items():
            timer_obj.update()

        text = [f'{round(self.handler.clock.get_fps())} fps',
                f'vel = {self.player.vel}',
                # pprint.pformat(Particle.cache)
                ]
        self.handler.canvas.blit(FONTS['basic'].get_surf('\n'.join(text)), (400, 0))


