import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import math

from math_utils import *
from ui import *
from vector3 import *

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

def drawLinks(links, max_link_force):
    
    for l in links:
        # change color to label color
        # glColor(l.color[0], l.color[1], l.color[2])

        # change color to force level color
        # calculate how red it should be, clamped between 0 and 1
        if not max_link_force == 0:
            red_level = max(min((l.calc_force()/l.k)/max_link_force, 1), 0)
            blue_level = max(min((-l.calc_force()/l.k)/max_link_force, 1), 0)
            green_level = (1 - red_level**2 - blue_level**2)**0.5
        else:
            red_level = 0
            blue_level = 0
            green_level = 1
            
        glColor(red_level, green_level, blue_level)

        glBegin(GL_LINES)
        glVertex3f(l.p1.pos.x, l.p1.pos.y, l.p1.pos.z)
        glVertex3f(l.p2.pos.x, l.p2.pos.y, l.p2.pos.z)
        glEnd()

def drawPoint2D(x, y, color, camera):
    glPushMatrix()

    glTranslate(-camera.pos.x,
                -camera.pos.y,
                -camera.pos.z)
    
    glColor(color[0], color[1], color[2])

    glBegin(GL_POINTS)

    x1 = x * 100
    y1 = y * 100

    glVertex3f((x1) * camera.get_orient()[0][0] + (y1) * camera.get_orient()[1][0] + (-1000) * camera.get_orient()[2][0],
               (x1) * camera.get_orient()[0][1] + (y1) * camera.get_orient()[1][1] + (-1000) * camera.get_orient()[2][1],
               (x1) * camera.get_orient()[0][2] + (y1) * camera.get_orient()[1][2] + (-1000) * camera.get_orient()[2][2])

    glEnd()
    
    glPopMatrix()

def drawLine2D(x1, y1, x2, y2, color, camera):
    glPushMatrix()
    glTranslate(-camera.pos.x,
                -camera.pos.y,
                -camera.pos.z)
    
    glColor(color[0], color[1], color[2])
    
    glBegin(GL_LINES)

    x1 = x1 * 100
    y1 = y1 * 100
    x2 = x2 * 100
    y2 = y2 * 100
    glVertex3f((x1) * camera.get_orient()[0][0] + (y1) * camera.get_orient()[1][0] + (-1000) * camera.get_orient()[2][0],
               (x1) * camera.get_orient()[0][1] + (y1) * camera.get_orient()[1][1] + (-1000) * camera.get_orient()[2][1],
               (x1) * camera.get_orient()[0][2] + (y1) * camera.get_orient()[1][2] + (-1000) * camera.get_orient()[2][2])
    
    glVertex3f((x2) * camera.get_orient()[0][0] + (y2) * camera.get_orient()[1][0] + (-1000) * camera.get_orient()[2][0],
               (x2) * camera.get_orient()[0][1] + (y2) * camera.get_orient()[1][1] + (-1000) * camera.get_orient()[2][1],
               (x2) * camera.get_orient()[0][2] + (y2) * camera.get_orient()[1][2] + (-1000) * camera.get_orient()[2][2])
    glEnd()
    glPopMatrix()

def drawRectangle2D(x1, y1, x2, y2, color, camera):
    drawLine2D(x1, y1, x2, y1, color, camera)
    drawLine2D(x1, y1, x1, y2, color, camera)
    drawLine2D(x2, y1, x2, y2, color, camera)
    drawLine2D(x1, y2, x2, y2, color, camera)

def drawColorScale(x1, y1, x2, y2, camera, max_val, colorUp, colorDown, colorMid=None, text_size=0.075):
    drawRectangle2D(x1, y1, x2, y2, [1,1,1], camera)
    drawLine2D(x1, y1, x2, y1, colorUp, camera)
    drawLine2D(x1, y2, x2, y2, colorDown, camera)
    if colorMid:
        drawLine2D(x1, (y1+y2)/2, x2, (y1+y2)/2, colorMid, camera)

    #render_AN("RAPID COMPUTE ACTIVE", (1,0,0), [-5, 0.5], cam, size)
    render_AN("TENSION " + str(round(max_val,5)), colorUp, [x2 + text_size, y1], camera, text_size)
    render_AN("COMPRESSION " + str(round(max_val,5)), colorDown, [x2 + text_size, y2], camera, text_size)

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

def drawForces(forces):
    
    for f in forces:
        glPushMatrix()

        scaler = 0.2
        start_position = f.point.pos
        end_position = f.point.pos + f.force
        f_vector = f.force * scaler
        
        f_dir = f_vector.normalized()
        arrowhead_start = f.force * scaler * 0.8

        if not f_dir.cross(vec3(1,0,0)) == vec3(0,0,0):
            arrowhead_vector1 = f_dir.cross(vec3(1,0,0))
        else:
            arrowhead_vector1 = f_dir.cross(vec3(0,1,0))

        arrowhead_vector2 = arrowhead_vector1.cross(f_dir)

        arrowhead_vector1 = arrowhead_vector1 * f.force.mag() * scaler * 0.1
        arrowhead_vector2 = arrowhead_vector2 * f.force.mag() * scaler * 0.1
            
        arrowhead_pt1 = arrowhead_start + arrowhead_vector1
        arrowhead_pt2 = arrowhead_start - arrowhead_vector1

        arrowhead_pt3 = arrowhead_start + arrowhead_vector2
        arrowhead_pt4 = arrowhead_start - arrowhead_vector2
        
        glTranslate(start_position.x, start_position.y, start_position.z)
        glColor(1,0,1)

        glBegin(GL_LINES)

        glVertex3f(0,0,0)
        glVertex3f(f_vector.x, f_vector.y, f_vector.z)

        glVertex3f(arrowhead_pt1.x, arrowhead_pt1.y, arrowhead_pt1.z)
        glVertex3f(arrowhead_pt3.x, arrowhead_pt3.y, arrowhead_pt3.z)

        glVertex3f(arrowhead_pt2.x, arrowhead_pt2.y, arrowhead_pt2.z)
        glVertex3f(arrowhead_pt4.x, arrowhead_pt4.y, arrowhead_pt4.z)

        glVertex3f(arrowhead_pt2.x, arrowhead_pt2.y, arrowhead_pt2.z)
        glVertex3f(arrowhead_pt3.x, arrowhead_pt3.y, arrowhead_pt3.z)

        glVertex3f(arrowhead_pt1.x, arrowhead_pt1.y, arrowhead_pt1.z)
        glVertex3f(arrowhead_pt4.x, arrowhead_pt4.y, arrowhead_pt4.z)

        glVertex3f(arrowhead_pt1.x, arrowhead_pt1.y, arrowhead_pt1.z)
        glVertex3f(f_vector.x, f_vector.y, f_vector.z)

        glVertex3f(arrowhead_pt2.x, arrowhead_pt2.y, arrowhead_pt2.z)
        glVertex3f(f_vector.x, f_vector.y, f_vector.z)

        glVertex3f(arrowhead_pt3.x, arrowhead_pt3.y, arrowhead_pt3.z)
        glVertex3f(f_vector.x, f_vector.y, f_vector.z)

        glVertex3f(arrowhead_pt4.x, arrowhead_pt4.y, arrowhead_pt4.z)
        glVertex3f(f_vector.x, f_vector.y, f_vector.z)

        glEnd()

        glPopMatrix()

def drawCursors(cursors, camera):

    for cursor in cursors:
        if cursor.visible:
            glPushMatrix()

            glTranslate(cursor.pos.x,
                        cursor.pos.y,
                        cursor.pos.z)
            
            glColor(cursor.color[0], cursor.color[1], cursor.color[2])

            glBegin(GL_LINES)

            glVertex3f(2,0,0)
            glVertex3f(-2,0,0)

            glVertex3f(0,2,0)
            glVertex3f(0,-2,0)

            glVertex3f(0,0,2)
            glVertex3f(0,0,-2)

            glEnd()
            
            glPopMatrix()

def drawScene(points, links, forces, cursors, active_cam, floor, max_link_force):
    points.sort(key=lambda x: mag([-x.pos.x - active_cam.pos.x, -x.pos.y - active_cam.pos.y, -x.pos.z - active_cam.pos.z]), reverse=True)
    links.sort(key=lambda x: mag([-x.pos.x - active_cam.pos.x, -x.pos.y - active_cam.pos.y, -x.pos.z - active_cam.pos.z]), reverse=True)

    drawGround(floor)
    drawLinks(links, max_link_force)
    drawForces(forces)
    drawPoints(points)
    drawCursors(cursors, active_cam)
    drawColorScale(-10, 6, -9.5, 3, active_cam, max_link_force, [1,0,0], [0,0,1], [0,1,0])
    #drawOrigin()

