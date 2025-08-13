from .entity import Entity
import pygame

class Health:

    def __init__(self, max_hp=5, hp=5):
        self.pos = (5, 5)
        self.max_hp = max_hp
        self.hp = hp

        self.hearts = []
        for i in range(self.max_hp):
            self.hearts.append(Entity(self.pos + pygame.Vector2(14*i, 0), 'heart', 'idle'))



    def update(self):
        for heart in self.hearts:
            heart.update()

    def render(self, surf):
        for heart in self.hearts:
            heart.render(surf)
