# lazerpaw
Cat lazer chase project.



# Running

`lazerpaw` is designed to run on a Raspberry Pi Zero W2.

It can run on a Rapsberry Pi Zero W, but will require a reduced frame rate to deal with the image processing load; which leads to jumpier control.

## Raspberry Pi

Se below for instructions on installing dependencies.

Run with:
```
python3 -m lazerpaw
```

### Running as a service

You can set `lazerpaw` as a service so that it runs automatically. To configure `lazerpaw` as a service:
```
./service/addService.sh
```

And then run it as a `user` service:
```
systemctl --user start lazerpaw
```

To run on boot:
```
systemctl --user enable lazerpaw
```

To inspect logs:
```
journalctl --user -u lazerpaw --since "10 minutes ago"
```

## Running the Simulator

The simulator should work on any operating system. I run it on a macbook.

Install the following dependencies:

```
python3 -m pip install flask opencv-python numpy
```

To run the simulator:

```
python3 -m simulate
```


# Machine setup

## Rapsberry Pi Zero W2

Run the following to install dependencies:

```
sudo apt update
sudo apt install pigpio python3-pigpio python3-opencv python3-numpy python3-flask
```

Run the PiGPIO daemon (for good servo control)

```
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

### Enable the serial port

* Call `sudo raspi-config`
* Navigate to the `Interface Options`
* Select `Serial Port`
* Select `<NO>` for making a login shell accessible over serial
* Select `<YES>` for enabling the serial port hardware







