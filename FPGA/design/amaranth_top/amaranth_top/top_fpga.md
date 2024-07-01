# FGPA Top File
1. AudioAdapter Class
2. FPGATop Class
3. gen_build function

---
## Audio Adapter
- Transforms a 16-bit audio RAM bus into a 32-bit AXI3 bus
- handles AXI3 signaling for address writes and data writes, 
  - including burst mode and alignment of addresses
- includes a mechanism to split 16-bit audio data across 32-bit AXI bus words, 
  - also manages byte strobes 

---
## FPGA Top
- Establishes the top-level module for the FPGA setting up:
  - clocks and PLLs
  - GPIO resources, 
  - connections to the HPS (Hard Processor System) of the Cyclone V SoC
- Includes defining clock domains for microphone capture and convolution, 
  - wiring GPIOs for microphone data, and connecting audio RAM bus to the AXI3 interface. 
- It also integrates other necessary submodules such as the Convolver, PLLs, 
  - and CSR (Control and Status Register) bridge.
  
### Updating I/O Ports for FOSSN
- DE1-Nano user manual page 28 of 118
- we are using DE10-nano shield A from Circuit Boards
- which goes on GPIO 0 pins

### Antenna Mic Order / Data lines
perspective from front of mic antenna

|     |     |
|-----|-----|
| d1  | d2  |
| d3  | d4  |

|          |          |
|----------|----------|
| 1L (ch2) | 2L (ch4) |
| 1R (ch1) | 2R (ch3) |
| 3L (ch6) | 4L (ch8) |
| 3R (ch5) | 4R (ch7) |

### GPIO Pins
| Ant 1  | Ant 2  | Ant 3  | Ant 4  | Ant 5  | Ant 6  |
|--------|--------|--------|--------|--------|--------|
| d1: 13 | d1: 02 | d1: 16 | d1: 28 | d1: 39 | d1: 25 |
| d2: 15 | d2: 01 | d2: 14 | d2: 26 | d2: 40 | d2: 27 |
| d3: 07 | d3: 06 | d3: 20 | d3: 34 | d3: 35 | d3: 21 |
| d4: 19 | d4: 05 | d4: 08 | d4: 22 | d4: 36 | d4: 33 |

### Clk Pins & Index
| Ant | pins |
|-----|------|
| 1   | 17   |
| 2   | 03   |
| 3   | 10   |
| 4   | 24   |
| 5   | 38   |
| 6   | 31   |

### WS Pins & Index
| Ant | pins |
|-----|------|
| 1   | 09   |
| 2   | 04   |
| 3   | 18   |
| 4   | 32   |
| 5   | 37   |
| 6   | 23   |


### GPIO Pin List
|     |        |     |        |
|-----|--------|-----|--------|
| 01  | A2 d2  | 02  | A2 d1  |
| 03  | A2 clk | 04  | A2 ws  |
| 05  | A2 d4  | 06  | A2 d3  |
| 07  | A1 d3  | 08  | A3 d4  |
| 09  | A1 ws  | 10  | A3 clk |
| 13  | A1 d1  | 14  | A3 d2  |
| 15  | A1 d2  | 16  | A3 d1  |
| 17  | A1 clk | 18  | A3 ws  |
| 19  | A1 d4  | 20  | A3 d3  |
| 21  | A6 d3  | 22  | A4 d4  |
| 23  | A6 ws  | 24  | A4 clk |
| 25  | A6 d1  | 26  | A4 d2  |
| 27  | A6 d2  | 28  | A4 d1  |
| 31  | A6 clk | 32  | A4 ws  |
| 33  | A6 d4  | 34  | A4 d3  |
| 35  | A5 d3  | 36  | A5 d4  |
| 37  | A5 ws  | 38  | A5 clk |
| 39  | A5 d1  | 40  | A5 d2  |



---
## Generator Build Files
The gen_build function prepares build constraints and settings for the FPGA compilation process 
using the DE10-Nano platform, generating the required files for FPGA synthesis and implementation.
