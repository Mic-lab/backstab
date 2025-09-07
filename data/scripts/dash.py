from data.scripts.timer import Timer

class DashOrb:

    MAX_ORB = 3

    def __init__(self, dash):
        self.dash = dash

    def update(self, dash):
        if self.dash.ready:
            pass
        self.ratio = dash.charge_timer.ratio


    def render(self, canvas):
        pass

    @property
    def colors(self):
        DashOrb.PRESETS[self.preset]

class Dash:

    DEFAULT_CHARGE_TIME = 20

    def __init__(self, duration=DEFAULT_CHARGE_TIME,
                 colors=((200, 200, 200), (240, 240, 240))):
        self.duration = duration
        self.charge_timer = Timer(self.duration)
        self.colors = colors
        self.dash_orb = DashOrb(self)

    def update(self, player):
        self.charge_timer.update()
        self.dash_orb.update(self)
    
    def execute(self, player, mouse_pos):
        self.charge_timer.reset()
        if self.ready: raise ValueError('watahel bpi')
        player.dash(mouse_pos)

    @property
    def ready(self):
        return self.charge_timer.done

    def __repr__(self) -> str:
        return f'Dash({self.ready=} {self.charge_timer})'

