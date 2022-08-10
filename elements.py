from math_utils import *
from vector3 import *

gravity = -9.81

class point_mass:
    def __init__(self, ident, pos, vel, color, mass, static=False):
        self.ident = ident
        self.pos = pos
        self.vel = vel
        self.color = color
        self.mass = mass
        self.static = static
        self.accel = vec3()

    def get_dist_to(self, thing):
        return (self.pos - thing.pos).mag()

    def direction_to(self, thing):
        return (thing.pos - self.pos).normalized()

    def clear_accel(self):
        self.accel = vec3()

    def apply_force(self, force):
        self.accel += force/self.mass

    def apply_gravity(self):
        self.apply_force(vec3(0, self.mass * gravity, 0))

    def update_vel(self, dt):
        if not self.static:
            self.vel += self.accel * dt

    def update_pos(self, dt):
        if not self.static:
            self.pos += self.vel * dt

class link:
    def __init__(self, ident, p1, p2, color, k=5000):
        self.ident = ident
        self.p1 = p1
        self.p2 = p2
        self.color = color
        self.k = k
        self.neutral_length = p1.get_dist_to(p2)
        self.pos = (p1.pos + p2.pos)/2

    def apply_force(self):
        p1 = self.p1
        p2 = self.p2
        dist = p1.get_dist_to(p2)
        if not dist == self.neutral_length:
            p1.apply_force(p1.direction_to(p2) * self.k * (dist - self.neutral_length))
            p2.apply_force(p2.direction_to(p1) * self.k * (dist - self.neutral_length))

    def calc_force(self):
        p1 = self.p1
        p2 = self.p2
        dist = p1.get_dist_to(p2)
        if not dist == self.neutral_length:
            return self.k * (dist - self.neutral_length)
        else:
            return 0

class ground:
    def __init__(self, height, color, elasticity, k):
        self.height = height
        self.color = color
        self.elasticity = elasticity
        self.k = k

    def apply_force(self, points, dt):
        for p in points:
            # normal force
            if p.pos.y < self.height:
                p.apply_force(vec3(0, p.mass * p.vel.y * -1 * (self.elasticity+1)/dt, 0))
                p.apply_force(vec3(0, p.mass * -gravity, 0))

            # friction
            if p.pos.y <= self.height:
                p.apply_force(vec3(p.vel.x, 0, p.vel.z) * p.mass * gravity * self.k)
            
class const_force:
    def __init__(self, ident, point, force):
        self.ident = ident
        self.point = point
        self.force = force

    def apply(self):
        self.point.apply_force(self.force)
