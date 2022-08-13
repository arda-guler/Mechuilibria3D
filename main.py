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

def import_save(filename):
    global points, links, forces

    filepath = "structures/" + filename + ".m3s"
    
    points = []
    links = []
    forces = []
    
    f = open(filepath, "r")
    lines = f.readlines()

    for line in lines:
        line = line.split("|")
        if line[0] == "P":
            new_point = point_mass(line[1],
                                   vec3(float(line[2][1:-1].split(",")[0]),
                                        float(line[2][1:-1].split(",")[1]),
                                        float(line[2][1:-1].split(",")[2])),
                                   vec3(float(line[3][1:-1].split(",")[0]),
                                        float(line[3][1:-1].split(",")[1]),
                                        float(line[3][1:-1].split(",")[2])),
                                   [float(line[4][1:-1].split(",")[0]),
                                    float(line[4][1:-1].split(",")[1]),
                                    float(line[4][1:-1].split(",")[2])],
                                    float(line[5]),
                                    bool(line[6][0:4]=="True"))
            points.append(new_point)

        elif line[0] == "L":
            new_link = link(line[1],
                            get_point_by_ident(line[2]),
                            get_point_by_ident(line[3]),
                            [float(line[4][1:-1].split(",")[0]),
                             float(line[4][1:-1].split(",")[1]),
                             float(line[4][1:-1].split(",")[2])],
                            float(line[5]))

            links.append(new_link)

        elif line[0] == "F":
            new_const_force = const_force(line[1],
                                          get_point_by_ident(line[2]),
                                          vec3(float(line[3][1:-1].split(",")[0]),
                                               float(line[3][1:-1].split(",")[1]),
                                               float(line[3][1:-1].split(",")[2]))
                                          )
            forces.append(new_const_force)

    return points, links, forces

def export_structure():
    global points, links, forces

    filename = input("Export filename:")
    filepath = "structures/" + filename + ".m3s"

    with open(filepath, "w") as expfile:
        for p in points:
            point_string = "P|" + p.ident + "|[" + str(p.pos.x) + "," + str(p.pos.y) + "," + str(p.pos.z) + "]|[" + str(p.vel.x) + "," + str(p.vel.y) + "," + str(p.vel.z) + "]|" + str(p.color) + "|" + str(p.mass) + "|" + str(p.static) + "\n"
            expfile.write(point_string)

        for l in links:
            link_string = "L|" + l.ident + "|" + l.p1.ident + "|" + l.p2.ident + "|" + str(l.color) + "|" + str(l.k) + "\n"
            expfile.write(link_string)

        for f in forces:
            force_string = "F|" + f.ident + "|" + f.point.ident + "|[" + str(f.force.x) + "," + str(f.force.y) + "," + str(f.force.z) + "]|\n"
            expfile.write(force_string)

    print("Structure export complete!")
    input("Press Enter to continue...")
            
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

    import_yesno = input("Import structure? (y/N):")
    if not import_yesno or import_yesno.lower() == "n":
        points = []
        links = []
        forces = []

    else:
        filename = input("Structure filename:")
        points, links, forces = import_save(filename)

    ## GROUND
    floor = ground(0, [0.7,0.7,0.7], 0.5, 0.25)

    ## 3D CURSORS
    cursor_A = cursor(vec3(1,0,0), [1,0,0], False)
    cursor_B = cursor(vec3(-1,0,0), [0,0,1], False)
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

    #export_structure()
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

            elif command[0] == "export_structure":
                export_structure()

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

        if applied_force_ratios:
            max_link_force = max(applied_force_ratios)
        else:
            max_link_force = 1

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
