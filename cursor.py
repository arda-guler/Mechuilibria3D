class cursor:
    def __init__(self, pos, color, visible=True):
        self.pos = pos
        self.color = color
        self.visible = visible

    def move(self, movement):
        self.pos = self.pos + movement

    def set_pos(self, newpos):
        self.pos = newpos
