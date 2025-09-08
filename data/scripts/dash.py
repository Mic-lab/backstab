from . import sfx
from .timer import Timer
from .animation import Animation
from .utils import swap_colors
from .config import COLORS

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
        print(f'{self.ratio} {self.dash.colors=}')

        img_key = f'orb_{self.ratio}{self.dash.colors}'
        if img_key not in Animation.img_db:
            img = swap_colors(Animation.img_db[f'orb_{self.ratio}'], (100, 100, 100), self.dash.colors[0])
            img = swap_colors(img, (255, 255, 255), self.dash.colors[1])
            Animation.add_img(img, img_key)
        self.img = Animation.img_db[img_key]

    def render(self, pos, surf):
        surf.blit(self.img, pos)

class Dash:

    DEFAULT_CHARGE_TIME = 60

    def __init__(self, duration=DEFAULT_CHARGE_TIME,
                 colors=(COLORS['dark gray'], COLORS['white'])):
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

    def __init__(self, *args, **kwargs):
        kwargs['colors'] = (COLORS['dark green'], COLORS['green'])
        super().__init__(*args, **kwargs)
    
    def special_execute(self, player, mouse_pos):
        print(f'Special execute')
        player.stab = True
        # player.stab_timer = self.timer
        sfx.sounds['kill_dash.wav'].play()

