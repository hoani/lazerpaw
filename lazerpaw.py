from controller.vision import ThresholdProcessor
import cv2 as cv
import numpy as np
import server.server as server
from hardware.camera import Camera
from hardware.servo import PanTilt
from hardware.lazer import Lazer
from hardware.button import Button
import time
import subprocess
import controller.commands as cmds

def do_shutdown():
    start = time.time()
    remaining = 5
    while remaining > 0:
        data = {
            "state": "Shutting down",
            "remaining": remaining
        }
        server.update_data(data)
        remaining = 5 - (time.time() - start)
        time.sleep(0.05)

    data = {
        "state": "Shutting down",
        "remaining": 0
    }
    server.update_data(data)
    time.sleep(0.05)
    subprocess.run(["sudo", "shutdown", "-h", "now"]) 


if __name__ == "__main__":
    serverThread = server.start()

    pantilt = PanTilt()
    camera = Camera()
    lazer = Lazer()
    button = Button()
    
    c = cmds.ControlRoutine(pantilt.get_pan(), pantilt.get_tilt(), pantilt.get_pan_boundary(), pantilt.get_tilt_boundary())
    server.set_start_cb(c.start)
    server.set_stop_cb(c.stop)

    lazerTester = cmds.LazerTester()
    server.set_lazer_tester_cb(lazerTester.set)

    shutdown = cmds.Shutdown()
    server.set_shutdown_cb(shutdown.set)

    threshold = ThresholdProcessor()
    server.set_threshold_cb(threshold.set_threshold)

    manual = cmds.ManualMode(camera.hfov*180/np.pi, camera.vfov*180/np.pi)
    server.set_manual_enabled_cb(manual.set_enabled)
    server.set_manual_command_cb(manual.set_cmd)

    dt = 0

    last_s = time.time()
    i = 0
    state = "Idle"
    for capture in camera.frame():
        if shutdown.get():
            do_shutdown()
            break

        if dt == 0:
            dt = 1/30 # Handle first update.
        else:
            now_s = time.time()
            dt = now_s - last_s
            last_s = now_s

        masked, cropped = threshold.process_frame(capture)
        server.update_video(capture)
        server.update_proc(masked)
        

        
        # blank = np.zeros(masked.shape[:2], dtype='uint8')
        # cmasked = blank.copy()
        
        # ## Crop image to radius.
        # srcw, srch = masked.shape[1], masked.shape[0]
        # dstw, dsth = cropped.shape[1], cropped.shape[0]

        # x0, y0 = int((srcw-dstw)/2), int((srch-dsth)/2)
        # x1, y1 = int(x0 + dstw), int(y0 +dsth)
        # cmasked[ y0:y1, x0:x1] = cropped
        # merged = cv.merge([blank, cmasked, masked])

        # server.update_proc(merged)

        ctl = c.update(cropped, dt)
        if ctl is not None:
            state = 'Running'
            lazer.set(ctl.lazer())

            pantilt.pan(ctl.yaw())
            pantilt.tilt(ctl.pitch())
        else:
            if manual.get_enabled():
                state = 'Manual'
                pantilt.increment_pan(manual.get_delta_yaw())
                pantilt.increment_tilt(manual.get_delta_pitch())
            else:
                state = 'Idle'
            lazer.set(lazerTester.get())

        pantilt.update(dt)

        data = {
            "time": time.strftime("%H:%M:%S"), 
            "state": state,
        }
        remaining = c.get_remaining()
        if remaining > 0:
            data["remaining"] = remaining

        server.update_data(data)

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
                
        print(
            'LazerPaw - dt: {:.1f}ms, fps: {:.1f}\n'.format(dt*1000.0, 1/dt) +
            'Pos - pan: {:.1f}, tilt: {:.1f} '.format(pantilt.get_pan(), pantilt.get_tilt()) +
            'Target - pan: {:.1f}, tilt: {:.1f} '.format(pantilt.yaw.target, pantilt.pitch.target)
        )
    
    camera.release()
    exit(0)