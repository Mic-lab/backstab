from . import sfx
from .timer import Timer
from .animation import Animation

class DashOrb:

    MAX_ORB = 3

    def __init__(self, dash):
        self.dash = dash
        self.update(self.dash)

    # TODO: Remove dash cause already stored in self
    def update(self, dash):
        if self.dash.ready:
            pass
        self.ratio = int((dash.charge_timer.ratio * DashOrb.MAX_ORB))
        print(f'{self.ratio}')
        self.img = Animation.img_db[f'orb_{self.ratio}']

    def render(self, pos, surf):
        surf.blit(self.img, pos)

    @property
    def colors(self):
        DashOrb.PRESETS[self.preset]

class Dash:

    DEFAULT_CHARGE_TIME = 60

    def __init__(self, duration=DEFAULT_CHARGE_TIME,
                 colors=((200, 200, 200), (240, 240, 240))):
        self.duration = duration
        self.charge_timer = Timer(self.duration)
        self.colors = colors
        self.dash_orb = DashOrb(self)

    def render(self, pos, surf):
        self.dash_orb.render(pos, surf)
                   
    def update(self, player):
        self.charge_timer.update()
        if self.ready:
            sfx.sounds['dash_load.wav'].play()
        self.dash_orb.update(self)

    
    def execute(self, player, mouse_pos):
        self.charge_timer.reset()
        if self.ready: raise ValueError('watahel bpi')
        player.dash(mouse_pos)
        self.special_execute(player, mouse_pos)
        sfx.sounds['dash.wav'].play()

    def special_execute(self, player, mouse_pos):
        pass

    @property
    def ready(self):
        return self.charge_timer.done

    def __repr__(self) -> str:
        return f'Dash({self.ready=} {self.charge_timer})'

class AttackDash(Dash):
    
    def special_execute(self, player, mouse_pos):
        print(f'Special execute')
        player.stab = True
        # player.stab_timer = self.timer
        sfx.sounds['kill_dash.wav'].play()

