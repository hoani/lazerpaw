from controller.vision import ThresholdProcessor, draw_crosshair
from controller.pantilt import PanTilt, ServoControl
import cv2 as cv
import numpy as np
import server.server as server
from hardware.camera import Camera
from hardware.servo import YawServo, PitchServo, Factory
from hardware.lazer import Lazer
from hardware.button import Button
from hardware.led import Status
import time
import subprocess
import controller.commands as cmds


def do_shutdown():
    start = time.time()
    remaining = 5
    while remaining > 0:
        data = {"state": "Shutting down", "remaining": remaining}
        server.update_data(data)
        remaining = 5 - (time.time() - start)
        led.update_shutdown(remaining / 5)
        time.sleep(0.05)

    data = {"state": "Shutting down", "remaining": 0}
    server.update_data(data)
    led.update_shutdown(0)
    time.sleep(0.05)
    subprocess.run(["sudo", "shutdown", "-h", "now"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Lazerpaw cat lazer chase game")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    serverThread = server.start()

    factory = Factory()
    panCtl = ServoControl(YawServo(factory))
    tiltCtl = ServoControl(PitchServo(factory))
    pantilt = PanTilt(panCtl, tiltCtl)

    camera = Camera()
    lazer = Lazer()
    button = Button()
    led = Status()

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

    manual = cmds.ManualMode(camera.hfov * 180 / np.pi, camera.vfov * 180 / np.pi)
    server.set_manual_enabled_cb(manual.set_enabled)
    server.set_manual_command_cb(manual.set_cmd)

    special = cmds.SpecialMode()
    server.set_special_cb(special.toggle_enable)

    dt = 0

    last_s = time.time()
    i = 0
    state = "Idle"
    for frame in camera.frame():
        if shutdown.get():
            do_shutdown()
            break

        if dt == 0:
            dt = 1 / 30  # Handle first update.
        else:
            now_s = time.time()
            dt = now_s - last_s
            last_s = now_s

        masked, cropped = threshold.process_frame(
            frame, pantilt.get_pan(), pantilt.get_tilt()
        )
        if lazerTester.get():
            draw_crosshair(frame)

        server.update_video(frame)
        server.update_proc(masked)

        ctl = c.update(cropped, dt)
        if ctl is not None:
            state = "Running"
            lazer.set(ctl.lazer())
        else:
            if special.get_enabled():
                state = "Special"
                dx, dy = special.get_deltas(pantilt.get_pan(), pantilt.get_tilt())
                pantilt.increment_pan(dx / 2)  # div 2 because pan bounds are half.
                pantilt.increment_tilt(dy)
                lazer.set(special.get_lazer())
            else:
                if manual.get_enabled():
                    state = "Manual"
                    pantilt.increment_pan(manual.get_delta_yaw())
                    pantilt.increment_tilt(manual.get_delta_pitch())
                else:
                    state = "Idle"
                lazer.set(lazerTester.get())

        if state != "Idle":
            pantilt.update(dt)
        else:
            pantilt.disable()

        data = {
            "time": time.strftime("%H:%M:%S"),
            "state": state,
        }
        remaining = c.get_remaining()
        if remaining > 0:
            data["remaining"] = remaining

        server.update_data(data)

        if state == "Running":
            led.update_running(remaining / cmds.ControlRoutine.ExecutionPeriod)
        elif state == "Manual":
            led.update_manual()
        else:
            led.update_idle()

        cmd = button.update()
        if cmd == Button.CommandShutdown:
            shutdown.set()
        elif cmd == Button.CommandRun:
            if c.get_running() == False:
                if manual.get_enabled():
                    manual.set_enabled(False)
                c.start()
            else:
                c.stop()

        if args.debug is True:
            print(
                "LazerPaw - dt: {:.1f}ms, fps: {:.1f}\n".format(dt * 1000.0, 1 / dt)
                + "Pos - pan: {:.1f}, tilt: {:.1f} ".format(
                    pantilt.get_pan(), pantilt.get_tilt()
                )
                + "Target - pan: {:.1f}, tilt: {:.1f} ".format(
                    pantilt._pan.target, pantilt._tilt.target
                )
            )

    camera.release()
    exit(0)
