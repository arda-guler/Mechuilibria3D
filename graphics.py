import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import math

from math_utils import *
from ui import *

def drawOrigin():
    glBegin(GL_LINES)
    glColor(1,0,0)
    glVertex3f(0,0,0)
    glVertex3f(100,0,0)
    glColor(0,1,0)
    glVertex3f(0,0,0)
    glVertex3f(0,100,0)
    glColor(0,0,1)
    glVertex3f(0,0,0)
    glVertex3f(0,0,100)
    glEnd()

def drawPoints(points):

    for p in points:
        glColor(p.color[0], p.color[1], p.color[2])
        
        glPushMatrix()
        glTranslatef(p.pos.x, p.pos.y, p.pos.z)

        glBegin(GL_POINTS)
        glVertex3f(0, 0, 0)
        glEnd()

        glPopMatrix()

def drawLinks(links):
    
    for l in links:
        glColor(l.color[0], l.color[1], l.color[2])

        glBegin(GL_LINES)
        glVertex3f(l.p1.pos.x, l.p1.pos.y, l.p1.pos.z)
        glVertex3f(l.p2.pos.x, l.p2.pos.y, l.p2.pos.z)
        glEnd()

def drawGround(floor, size=100, divisions=20):

    y_floor = floor.height
    glColor(floor.color[0], floor.color[1], floor.color[2])

    glBegin(GL_LINES)
    
    for xi in range(divisions + 1):
        glVertex3f(2* xi * (size/divisions) - size, y_floor, -size)
        glVertex3f(2* xi * (size/divisions) - size, y_floor, +size)

    for zi in range(divisions + 1):
        glVertex3f(-size, y_floor, 2* zi * (size/divisions) - size)
        glVertex3f(+size, y_floor, 2* zi * (size/divisions) - size)

    glEnd()

def drawScene(points, links, forces, active_cam, floor):

    points.sort(key=lambda x: mag([-x.pos.x - active_cam.pos.x, -x.pos.y - active_cam.pos.y, -x.pos.z - active_cam.pos.z]), reverse=True)
    links.sort(key=lambda x: mag([-x.pos.x - active_cam.pos.x, -x.pos.y - active_cam.pos.y, -x.pos.z - active_cam.pos.z]), reverse=True)

    drawGround(floor)
    drawLinks(links)
    drawPoints(points)
    #drawOrigin()

