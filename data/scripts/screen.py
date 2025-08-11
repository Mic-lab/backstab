import pygame
from . import config

def create_screen():
    return pygame.display.set_mode(config.SCREEN_SIZE,  pygame.OPENGL | pygame.DOUBLEBUF)

screen = create_screen()


