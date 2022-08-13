import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import os
import keyboard
import glfw
import time

from camera import *
from math_utils import *
from ui import *
from elements import *
from graphics import *
from cursor import *

points = []
links = []
cursors = []
forces = []

def get_os_type():
    return os.name

def clear_cmd_terminal(os_name):
    if os_name == "nt":
        os.system("cls")
    else:
        os.system("clear")

vp_size_changed = False
def resize_cb(window, w, h):
    global vp_size_changed
    vp_size_changed = True

def create_point(ident, pos, vel, color, mass, static=False):
    global points
    
    new_point = point_mass(ident, pos, vel, color, mass, static)
    points.append(new_point)

def remove_point(ident):
    global points, links

    for p in points:
        if p.ident == ident:
            
            for l in links:
                if l.p1 == p or l.p2 == p:
                    links.remove(l)
                    del l

            points.remove(p)
            del p

def get_point_by_ident(ident):
    global points

    result = None

    for p in points:
        if p.ident == ident:
            result = p
            break

    return result

def create_link(ident, p1, p2, color, k):
    global links
    
    new_link = link(ident, p1, p2, color, k)
    links.append(new_link)

def remove_link(ident):
    global links
    for l in links:
        if l.ident == ident:
            links.remove(l)
            del l

def get_link_by_ident(ident):
    global links

    result = None

    for l in links:
        if l.ident == ident:
            result = l
            break

    return result

def create_const_force(ident, point, force):
    global forces
    new_force = const_force(ident, point, force)
    forces.append(new_force)

def remove_force(ident):
    global forces
    for f in forces:
        if f.ident == ident:
            forces.remove(f)
            del f

# clear all keyboard buffer
# e.g. don't keep camera movement keys
# in buffer as we try to enter a command
def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def init():
    global points, links, forces
    main_cam = camera("main_cam", vec3(), [[1,0,0],[0,1,0],[0,0,1]], True)
    dt = 0.005

    ## POINTS (ident, pos, vel, volor, mass, static)
    p0 = point_mass("p0", vec3(0,0,0), vec3(), [1,0,0], 1, True)
    p1 = point_mass("p1", vec3(2,0,0), vec3(), [1,0,0], 1, True)
    p2 = point_mass("p2", vec3(2,0,-2), vec3(), [1,0,0], 1, True)
    p3 = point_mass("p3", vec3(0,0,-2), vec3(), [1,0,0], 1, True)

    p4 = point_mass("p4", vec3(0,5,0), vec3(), [1,0,0], 1)
    p5 = point_mass("p5", vec3(2,5,0), vec3(), [1,0,0], 1)
    p6 = point_mass("p6", vec3(2,5,-2), vec3(), [1,0,0], 1)
    p7 = point_mass("p7", vec3(0,5,-2), vec3(), [1,0,0], 1)

    p8 = point_mass("p8", vec3(0,10,0), vec3(), [1,0,0], 1)
    p9 = point_mass("p9", vec3(2,10,0), vec3(), [1,0,0], 1)
    p10 = point_mass("p10", vec3(2,10,-2), vec3(), [1,0,0], 1)
    p11 = point_mass("p11", vec3(0,10,-2), vec3(), [1,0,0], 1)

    p12 = point_mass("p12", vec3(0,15,0), vec3(), [1,0,0], 1)
    p13 = point_mass("p13", vec3(2,15,0), vec3(), [1,0,0], 1)
    p14 = point_mass("p14", vec3(2,15,-2), vec3(), [1,0,0], 1)
    p15 = point_mass("p15", vec3(0,15,-2), vec3(), [1,0,0], 1)

    p16 = point_mass("p16", vec3(-12,15,0), vec3(), [1,0,0], 1)
    p17 = point_mass("p17", vec3(-12,10,0), vec3(), [1,0,0], 1)
    p18 = point_mass("p18", vec3(-12,10,-2), vec3(), [1,0,0], 1)
    p19 = point_mass("p19", vec3(-12,15,-2), vec3(), [1,0,0], 1)

    p20 = point_mass("p20", vec3(20,15,0), vec3(), [1,0,0], 1)
    p21 = point_mass("p21", vec3(20,12,0), vec3(), [1,0,0], 1)
    p22 = point_mass("p22", vec3(20,12,-2), vec3(), [1,0,0], 1)
    p23 = point_mass("p23", vec3(20,15,-2), vec3(), [1,0,0], 1)

    p24 = point_mass("p24", vec3(25,15,-1), vec3(), [1,0,0], 1)
    
    points = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9,
              p10, p11, p12, p13, p14, p15, p16, p17, p18, p19,
              p20, p21, p22, p23, p24]

    ## LINKS
    l1 = link("l1", p0, p1, [0,1,1])
    l2 = link("l2", p1, p2, [0,1,1])
    l3 = link("l3", p2, p3, [0,1,1])
    l4 = link("l4", p3, p0, [0,1,1])

    l5 = link("l5", p4, p5, [0,1,1])
    l6 = link("l6", p5, p6, [0,1,1])
    l7 = link("l7", p6, p7, [0,1,1])
    l8 = link("l8", p7, p4, [0,1,1])

    l9 = link("l9", p8, p9, [0,1,1], 15000)
    l10 = link("l10", p9, p10, [0,1,1], 15000)
    l11 = link("l11", p10, p11, [0,1,1], 15000)
    l12 = link("l12", p11, p8, [0,1,1], 15000)

    l13 = link("l13", p12, p13, [0,1,1])
    l14 = link("l14", p13, p14, [0,1,1])
    l15 = link("l15", p14, p15, [0,1,1])
    l16 = link("l16", p15, p12, [0,1,1])

    l17 = link("l17", p0, p4, [0,1,1], 15000)
    l18 = link("l18", p1, p5, [0,1,1], 15000)
    l19 = link("l19", p2, p6, [0,1,1], 15000)
    l20 = link("l20", p3, p7, [0,1,1], 15000)

    l21 = link("l21", p4, p8, [0,1,1], 15000)
    l22 = link("l22", p5, p9, [0,1,1], 15000)
    l23 = link("l23", p6, p10, [0,1,1], 15000)
    l24 = link("l24", p7, p11, [0,1,1], 15000)

    l25 = link("l25", p8, p12, [0,1,1], 15000)
    l26 = link("l26", p9, p13, [0,1,1], 15000)
    l27 = link("l27", p10, p14, [0,1,1], 15000)
    l28 = link("l28", p11, p15, [0,1,1], 15000)

    l29 = link("l29", p12, p16, [0,1,1])
    l30 = link("l30", p8, p17, [0,1,1])
    l31 = link("l31", p11, p18, [0,1,1])
    l32 = link("l32", p15, p19, [0,1,1])

    l29 = link("l29", p12, p16, [0,1,1])
    l30 = link("l30", p8, p17, [0,1,1])
    l31 = link("l31", p11, p18, [0,1,1])
    l32 = link("l32", p15, p19, [0,1,1])

    l33 = link("l33", p16, p17, [0,1,1])
    l34 = link("l34", p17, p18, [0,1,1])
    l35 = link("l35", p18, p19, [0,1,1])
    l36 = link("l36", p19, p16, [0,1,1])

    l37 = link("l37", p13, p20, [0,1,1])
    l38 = link("l38", p9, p21, [0,1,1])
    l39 = link("l39", p10, p22, [0,1,1])
    l40 = link("l40", p14, p23, [0,1,1])

    l41 = link("l41", p20, p21, [0,1,1])
    l42 = link("l42", p21, p22, [0,1,1])
    l43 = link("l43", p22, p23, [0,1,1])
    l44 = link("l44", p23, p20, [0,1,1])

    l45 = link("l45", p20, p24, [0,1,1])
    l46 = link("l46", p21, p24, [0,1,1])
    l47 = link("l47", p22, p24, [0,1,1])
    l48 = link("l48", p23, p24, [0,1,1])

    s1 = link("s1", p0, p5, [1,0,1])
    s2 = link("s1", p1, p6, [1,0,1])
    s3 = link("s3", p2, p7, [1,0,1])
    s4 = link("s4", p3, p4, [1,0,1])

    s5 = link("s5", p4, p9, [1,0,1])
    s6 = link("s6", p5, p10, [1,0,1])
    s7 = link("s7", p6, p11, [1,0,1])
    s8 = link("s8", p7, p8, [1,0,1])

    s9 = link("s9", p8, p13, [1,0,1])
    s10 = link("s10", p9, p14, [1,0,1])
    s11 = link("s11", p10, p15, [1,0,1])
    s12 = link("s12", p11, p12, [1,0,1])

    s13 = link("s13", p16, p15, [1,0,1])
    s14 = link("s14", p17, p12, [1,0,1])
    s15 = link("s15", p18, p8, [1,0,1])
    s16 = link("s16", p19, p11, [1,0,1])

    s17 = link("s17", p16, p18, [1,0,1])

    s18 = link("s18", p9, p20, [1,0,1])
    s19 = link("s19", p10, p21, [1,0,1])
    s20 = link("s20", p14, p22, [1,0,1])
    s21 = link("s21", p13, p23, [1,0,1])

    s22 = link("s22", p20, p22, [1,0,1])

    s23 = link("s23", p4, p6, [1,0,1])
    s24 = link("s24", p8, p10, [1,0,1], 15000)
    s25 = link("s25", p12, p14, [1,0,1])
    
    links = [l1, l2, l3, l4, l5, l6, l7, l8, l9,
             l10, l11, l12, l13, l14, l15, l16, l17, l18, l19,
             l20, l21, l22, l23, l24, l25, l26, l27, l28, l29,
             l30, l31, l32, l33, l34, l35, l36, l37, l38, l39,
             l40, l41, l42, l43, l44, l45, l46, l47, l48,
             s1, s2, s3, s4, s5, s6, s7, s8, s9,
             s10, s11, s12, s13, s14, s15, s16, s17, s18, s19,
             s20, s21, s22, s23, s24, s25]

    ## GROUND
    floor = ground(0, [0.7,0.7,0.7], 0.5, 0.25)

    ## FORCES
    f1 = const_force("force1", p20, vec3(0, 50, 0))
    forces = [f1]

    ## 3D CURSORS
    cursor_A = cursor(vec3(1,0,0), [1,0,0])
    cursor_B = cursor(vec3(-1,0,0), [0,0,1])
    cursors = [cursor_A, cursor_B]
    
    return main_cam, dt, points, links, floor, forces, cursors

def main():
    global vp_size_changed
    main_cam, dt, points, links, floor, forces, cursors = init()
    glfw.init()

    window = glfw.create_window(1000,600,"Mechuilibria3D", None, None)
    glfw.set_window_pos(window,100,100)
    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, resize_cb)
    
    gluPerspective(70, 1000/600, 0.005, 10000)
    glEnable(GL_CULL_FACE)
    glClearColor(0.3, 0.3, 0.3, 1)
    glPointSize(3)
    main_cam.move(vec3(-5,-5,-30))

    cam_rotate_speed = 0.5
    cam_strafe_speed = 0.1

    cam_pitch_up = "W"
    cam_pitch_down = "S"
    cam_yaw_left = "A"
    cam_yaw_right = "D"
    cam_roll_ccw = "Q"
    cam_roll_cw = "E"

    cam_strafe_left = "J"
    cam_strafe_right = "L"
    cam_strafe_up = "U"
    cam_strafe_down = "O"
    cam_strafe_forward = "I"
    cam_strafe_backward = "K"

    os_name = str(get_os_type())

    sim_time = 0
    cycle = 0
    frame_command = False
    while not glfw.window_should_close(window):
        sim_time += dt
        frame_command = False
        glfw.poll_events()

        if vp_size_changed:
            vp_size_changed = False
            w, h = glfw.get_framebuffer_size(window)
            glViewport(0, 0, w, h)

        main_cam.rotate(vec3((keyboard.is_pressed(cam_pitch_up) - keyboard.is_pressed(cam_pitch_down)) * cam_rotate_speed,
                             (keyboard.is_pressed(cam_yaw_left) - keyboard.is_pressed(cam_yaw_right)) * cam_rotate_speed,
                             (keyboard.is_pressed(cam_roll_ccw) - keyboard.is_pressed(cam_roll_cw)) * cam_rotate_speed))

        main_cam.move(vec3((keyboard.is_pressed(cam_strafe_left) - keyboard.is_pressed(cam_strafe_right)) * cam_strafe_speed,
                           (keyboard.is_pressed(cam_strafe_down) - keyboard.is_pressed(cam_strafe_up)) * cam_strafe_speed,
                           (keyboard.is_pressed(cam_strafe_forward) - keyboard.is_pressed(cam_strafe_backward)) * cam_strafe_speed))

        if keyboard.is_pressed("c"):
            frame_command = True

        if frame_command:
            flush_input()
            command = input("\n > ")
            command = command.split(" ")
            command[0] = command[0].lower()

            # --- COMMAND INTERPRETER ---
            if command[0] == "create_point":
                create_point(command[1], # ident
                             vec3(float(command[2][1:-1].split(",")[0]),
                                  float(command[2][1:-1].split(",")[1]),
                                  float(command[2][1:-1].split(",")[2])), # position

                             vec3(float(command[3][1:-1].split(",")[0]),
                                  float(command[3][1:-1].split(",")[1]),
                                  float(command[3][1:-1].split(",")[2])), # velocity
                             
                             [float(command[4][1:-1].split(",")[0]),
                              float(command[4][1:-1].split(",")[1]),
                              float(command[4][1:-1].split(",")[2])], # color

                             float(command[5]), # mass

                             int(command[6])) # static

            elif command[0] == "remove_point":
                remove_point(command[1])

            elif command[0] == "create_link":
                create_link(command[1], get_point_by_ident(command[2]), get_point_by_ident(command[3]),
                            [float(command[4][1:-1].split(",")[0]),
                             float(command[4][1:-1].split(",")[1]),
                             float(command[4][1:-1].split(",")[2])],
                            float(command[5]))

            elif command[0] == "remove_link":
                remove_link(command[1])

            elif command[0] == "create_const_force":
                create_const_force(command[1],
                                   get_point_by_ident(command[2]),
                                   vec3(float(command[3][1:-1].split(",")[0]),
                                        float(command[3][1:-1].split(",")[1]),
                                        float(command[3][1:-1].split(",")[2]))
                                   )

            elif command[0] == "remove_force":
                remove_force(command[1])

            elif command[0] == "clear_forces":
                forces = []

            elif command[0] == "clear_scene":
                forces = []
                links = []
                points = []  

            elif command[0] == "dt":
                dt = float(command[1])

            elif command == "":
                pass

            else:
                print("Unrecognized command!")
                input("Press Enter to continue...")

        # PHYSICS HAPPENS BELOW
        if not dt == 0:
            floor.apply_force(points, dt)

        for f in forces:
            f.apply()

        applied_force_ratios = []
        for l in links:
            if not dt == 0:
                l.apply_force()
                applied_force_ratios.append(abs(l.calc_force()/l.k))

        max_link_force = max(applied_force_ratios)

        for p in points:
            if not dt == 0:
                p.apply_gravity()
                p.update_vel(dt)
                p.update_pos(dt)

            p.clear_accel()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        drawScene(points, links, forces, cursors, main_cam, floor, max_link_force)
        glfw.swap_buffers(window)

        if cycle % 100 <= 1:
            clear_cmd_terminal(os_name)
            print("Mechuilibria 3D Command Interpreter")
            print("T:", round(sim_time, 3))

        #time.sleep(dt)
        cycle += 1

main()
