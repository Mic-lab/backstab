from .state import State
from ..mgl import shader_handler
from ..import utils
from ..button import Button
from ..font import FONTS
from ..import animation
from ..entity import Entity, PhysicsEntity
from ..timer import Timer
from ..particle import Particle, ParticleGenerator
from .. import sfx
from .. import screen, config
import pygame

class Menu(State):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        rects = [pygame.Rect(30, 30+i*30, 110, 20) for i in range(6)]
        self.buttons = {
            'game': Button(rects[0], 'harloo', 'basic'),
            'scale': Button(rects[1], f'Window Scale ({config.SCALE}x)', 'basic'),
        }

    def sub_update(self):

        self.handler.canvas.fill((20, 20, 20))

        # Update Buttons
        for key, btn in self.buttons.items():
            btn.update(self.handler.inputs)
            btn.render(self.handler.canvas)

            if btn.clicked:
                if key == 'game':
                    self.handler.transition_to(self.handler.states.Game)
                elif key == 'scale':
                    config.SCALE = (config.SCALE + 1) % 5
                    if config.SCALE == 0: config.SCALE = 1
                    config.SCREEN_SIZE = config.SCALE*config.CANVAS_SIZE[0], config.SCALE*config.CANVAS_SIZE[1]
                    screen.screen = screen.create_screen()
                    shader_handler.ctx.viewport = (0, 0, config.SCREEN_SIZE[0], config.SCREEN_SIZE[1])
                    btn.text = f'Window Scale ({config.SCALE}x)'
