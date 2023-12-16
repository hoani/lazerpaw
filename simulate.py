from simulator.simulator import (
    Room,
    Camera,
    Cat,
    Simulation,
    Servo,
    PanBounds,
    TiltBounds,
)
from controller.vision import ThresholdProcessor, draw_crosshair
from controller.pantilt import PanTilt, ServoControl
import controller.commands as cmds
import cv2 as cv
import numpy as np
from random import randint
import server.server as server
import time


if __name__ == "__main__":
    serverThread = server.start()

    panCtl = ServoControl(Servo(0, PanBounds[0], PanBounds[1]))
    tiltCtl = ServoControl(
        Servo((TiltBounds[0] + TiltBounds[1]) / 2, TiltBounds[0], TiltBounds[1])
    )
    pantilt = PanTilt(panCtl, tiltCtl)

    room = Room()
    camera = Camera(pantilt)
    sim = Simulation(room=room, camera=camera)
    sim.add_cat(Cat(randint(0, room.size[0]), randint(0, room.size[1])))

    c = cmds.ControlRoutine(pantilt)
    server.set_start_cb(c.start)
    server.set_stop_cb(c.stop)

    lazerTester = cmds.LazerTester()
    server.set_lazer_tester_cb(lazerTester.set)

    shutdown = cmds.Shutdown()
    server.set_shutdown_cb(shutdown.set)

    threshold = ThresholdProcessor(
        pantilt.get_pan_boundary(), pantilt.get_tilt_boundary()
    )
    server.set_threshold_cb(threshold.set_threshold)

    manual = cmds.ManualMode(camera.hfov, camera.vfov)
    server.set_manual_enabled_cb(manual.set_enabled)
    server.set_manual_command_cb(manual.set_cmd)

    special = cmds.SpecialMode()
    server.set_special_cb(special.toggle_enable)

    dt = 0.05

    while shutdown.get() is False:
        frame = sim.update()
        frame = cv.resize(frame, (640, 480))

        draw_crosshair(frame)

        server.update_video(frame)

        masked, cropped = threshold.process_frame(
            frame, pantilt.get_pan(), pantilt.get_tilt()
        )

        server.update_proc(masked)

        ctl = c.update(cropped, dt)
        state = "Idle"
        if ctl is not None:
            state = "Running"
            sim.lazerOn = ctl.lazer()
        else:
            if special.get_enabled():
                dx, dy = special.get_deltas(pantilt.get_pan(), pantilt.get_tilt())
                pantilt.increment_pan(dx / 2)  # div 2 because pan bounds are half.
                pantilt.increment_tilt(dy)
                sim.lazerOn = special.get_lazer()
            else:
                if manual.get_enabled():
                    pantilt.increment_pan(manual.get_delta_yaw())
                    pantilt.increment_tilt(manual.get_delta_pitch())
                    state = "Manual"
                sim.lazerOn = lazerTester.get()

        pantilt.update(dt)

        data = {
            "time": time.strftime("%H:%M:%S"),
            "state": state,
        }
        remaining = c.get_remaining()
        if remaining > 0:
            data["remaining"] = remaining

        server.update_data(data)

        if cv.waitKey(int(100 * dt)) != -1:
            break

    exit(0)
