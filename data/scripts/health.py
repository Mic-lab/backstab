from .particle import ParticleGenerator
from .entity import Entity
import pygame

class Health:

    def __init__(self, max_hp=5, hp=5):
        self.pos = (5, 5)
        self.max_hp = max_hp
        self.hp = hp
        self.change_hp(0)

    def change_hp(self, change, gens=None):
        if change == -1:
            pos = list(self.hearts[self.hp-1].rect.center)
            pos[0] += 1  # idk prolly some odd/even pixel thing
            gens.append(ParticleGenerator.from_template(pos, 'heart_break'))

        self.hp += change
        if self.hp > self.max_hp: self.hp = self.max_hp
        elif self.hp < 0: self.hp = 0

        self.hearts = []
        for i in range(self.max_hp):
            if i >= self.hp:
                name = 'empty'
            else:
                name = 'full'
            self.hearts.append(Entity(self.pos + pygame.Vector2(14*i, 0), 'heart', name))


    def update(self):
        for heart in self.hearts:
            heart.update()

    def render(self, surf):
        for heart in self.hearts:
            heart.render(surf)
