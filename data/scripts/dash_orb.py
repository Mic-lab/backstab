class Dash:

    DEFAULT_CHARGE_TIME = 20

    def __init__(self, duration=DEFAULT_CHARGE_TIME):
        self.duration = duration
        self.charge_timer = Timer(self.duration)
        self.colors = (200, 200, 200), (240, 240, 240)

    def update(self):
        self.charge_timer.update()
    
    def execute(self):
        self.charge_timer.reset()
        if self.ready: raise ValueError('watahel bpi')

    @property
    def ready(self):
        return self.charge_timer.done

    def __repr__(self) -> str:
        return f'Dash({self.ready=} {self.charge_timer})'


class DashOrb:

    def __init__(self, dash):
        self.dash = dash

    def update(self):
        self.ratio = self.ready_dash_i

    def render(self):
        pass


    @property
    def colors(self):
        DashOrb.PRESETS[self.preset]
