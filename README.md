# Conveyor Belt Monitoring & Control System

An educational MPLAB X / XC8 project for the PIC16F877A. It demonstrates a
digital object sensor, CCP1 PWM motor-speed control, Timer1-based jam timing,
LCD status, and fault outputs.

## Start here

- [`newmain.c`](newmain.c) - complete commented firmware source.
- [`output/pdf/Conveyor_Belt_Monitoring_Control_Handbook.pdf`](output/pdf/Conveyor_Belt_Monitoring_Control_Handbook.pdf) - colorful beginner handbook with the system diagram, pin map, register guide, timing calculations, program walkthrough, and review notes.
- `nbproject/` and `Makefile` - MPLAB X project files.

Open this folder in MPLAB X, select the PIC16F877A and XC8, then build. The
project is configured for a 20 MHz crystal. Confirm the physical wiring and
sensor polarity before powering the motor driver.

## Pin map

| PIC pin | Function |
| --- | --- |
| RB0 | Digital object sensor input, active LOW by default |
| RB1 | Fault LED output, use a current-limiting resistor |
| RB2 | Buzzer-driver output |
| RB3 | Active-LOW stop / jam-acknowledge button with external pull-up |
| RC2/CCP1 | PWM output to motor-driver enable input |
| RD2, RD3 | H-bridge direction inputs IN1 and IN2 |
| RD0, RD1 | LCD RS and E |
| RD4-RD7 | LCD D4-D7 in 4-bit mode |
| LCD R/W | Tie to GND |

The 16x2 LCD uses PORTD and the H-bridge direction control uses RD2/RD3.
Timer1 runs from Fosc/4 with a 1:8 prescaler and provides an approximate
millisecond timebase. The jam threshold defaults to 5 seconds and PWM speed to
60 percent; both can be changed near the top of `newmain.c`.

## Safety and educational scope

The PIC cannot drive a motor or buzzer directly. Use a suitable motor driver,
separate motor supply as required, a common logic ground, proper decoupling,
and a protected driver module. Test first in simulation or with a low-voltage
setup. A real conveyor requires guarded machinery and independent emergency
stop and safety controls; this example is not a certified safety controller.

The handbook describes the source as written. Build and verify it with your
installed MPLAB X / XC8 version and target hardware before relying on it.
