# Amaranth Implementation of Beamforming with Microphones

## Updaing I/O Ports for FOSSN
- this is located in fpga_top.py
- DE1-Nano user manual page 28 of 118
- we are using DE10-nano shield A
- which is GPIO 0


## Mic Order / Data lines
- from back

2L / 1L
2R / 1R
4L / 3L
4R / 3R


d1 | d2
d3 | d4


### GPIO Pins
| Ant 1             | Ant 2             | Ant 3             | Ant 4             | Ant 5             | Ant 6               |
|-------------------|-------------------|-------------------|-------------------|-------------------|---------------------|
| 00 : 15 / 01 : 13 | 02 : 01 / 03 : 02 | 04 : 14 / 05 : 16 | 06 : 26 / 07 : 28 | 08 : 40 / 09 : 39 | 010 : 27 / 011 : 25 |
| 10 : 15 / 11 : 13 | 12 : 01 / 13 : 02 | 14 : 14 / 15 : 16 | 16 : 26 / 17 : 28 | 18 : 40 / 19 : 39 | 110 : 27 / 111 : 25 |
| 20 : 19 / 21 : 07 | 22 : 05 / 23 : 06 | 24 : 08 / 25 : 20 | 26 : 22 / 27 : 34 | 28 : 36 / 29 : 35 | 210 : 33 / 211 : 21 |
| 30 : 19 / 31 : 07 | 32 : 05 / 33 : 06 | 34 : 08 / 35 : 20 | 36 : 22 / 37 : 34 | 38 : 36 / 39 : 35 | 310 : 33 / 311 : 21 |

### GPIO Pins
A1
d1: 13
d2: 15
d3: 7
d4: 19

A2
d1: 2
d2: 1
d3: 6
d4: 5


### Clk Pins & Index
| Ant | pins |
|-----|------|
| 1   | 17   |
| 2   | 03   |
| 3   | 10   |
| 4   | 24   |
| 5   | 38   |
| 6   | 31   |

# WS Pins & Index
| Ant | pins |
|-----|------|
| 1   | 09   |
| 2   | 04   |
| 3   | 18   |
| 4   | 32   |
| 5   | 37   |
| 6   | 23   |


### GPIO Pin List
01 - A2 d2
02 - A2 d1
03 - A2 clk
04 - A2 ws
05 - A2 d4
06 - A2 d3
07 - A1 d3
08 - A3 d4
09 - A1 ws
10 - A3 clk

13 - A1 d1
14 - A3 d2
15 - A1 d2
16 - A3 d1
17 - A1 clk
18 - A3 ws
19 - A1 d4
20 - A3 d3
21 - A6 d3
22 - A4 d4
23 - A6 ws
24 - A4 clk
25 - A6 d1
26 - A4 d2
27 - A6 d2
28 - A4 d1

31 - A6 clk
32 - A4 ws
33 - A6 d4
34 - A4 d3
35 - A5 d3
36 - A5 d4
37 - A5 ws
38 - A5 clk
39 - A5 d1
40 - A5 d2



