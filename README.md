# lazerpaw
Cat lazer chase project

# Machine setup

## MacOS

This project can be run with the simulator on macos.

```
python3 -m pip install flask opencv-python numpy
```

## Rapsberry Pi Zero W

This project is written to be run on a Raspberry Pi Zero W. 

Run the following to install dependencies:

```
sudo apt update
sudo apt install pigpio python3-pigpio python3-opencv python3-numpypyth python3-flask
```

Run the PiGPIO daemon (for good servo control)

```
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```






