from simulator.simulator import Room, Camera, Cat, Simulation
from controller.vision import ThresholdProcessor
import cv2 as cv
import numpy as np
from random import randint
import server.server as server
import controller.commands as cmds




if __name__ == "__main__":
    serverThread = server.start()

    room = Room()
    camera = Camera()
    sim = Simulation(room=room, camera=camera)
    sim.add_cat(Cat(randint(0, room.size[0]),randint(0, room.size[1])))
    
    c = cmds.ControlRoutine(camera.pan, camera.tilt, Camera.PanBounds, Camera.TiltBounds)
    server.set_start_cb(c.start)
    server.set_stop_cb(c.stop)

    lazerTester = cmds.LazerTester()
    server.set_lazer_tester_cb(lazerTester.set)

    shutdown = cmds.Shutdown()
    server.set_shutdown_cb(shutdown.set)

    threshold = ThresholdProcessor()
    server.set_threshold_cb(threshold.set_threshold)

    manual = cmds.ManualMode(camera.hfov, camera.vfov)
    server.set_manual_enabled_cb(manual.set_enabled)
    server.set_manual_command_cb(manual.set_cmd)

    dt = 0.05

    while shutdown.get() is False:
        frame = sim.update()
        frame = cv.resize(frame, (640,480))

        server.update_video(frame)

        masked, cropped = threshold.process_frame(frame)

        server.update_proc(masked)


        ctl = c.update(cropped, dt)
        if ctl is not None:
            sim.lazerOn = ctl.lazer()

            camera.commandPan(ctl.yaw() *np.pi/180)
            camera.commandTilt(ctl.pitch()*np.pi/180)
        else:
            if manual.get_enabled():
                camera.increment_pan(manual.get_delta_pitch())
                camera.increment_tilt(manual.get_delta_yaw())
            sim.lazerOn = lazerTester.get()

        if cv.waitKey(int(100*dt)) != -1:
            break

    exit(0)