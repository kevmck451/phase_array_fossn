# Project File Structure and Dependencies

## Core Files
- **constants.py**
  - No imports (Defines global constants used throughout the project).

## Bus Interfaces and Protocols
- **axi3.py**
  - No imports (Defines AXI3 interfaces, signatures, and enums).

- **bus.py**
  - No imports (Likely defines other bus interfaces or general bus utilities).

## AXI Components
- **axi3_csr.py**
  - Imports from `axi3.py` (Uses AXI3 interface definitions for CSR handling).

- **cyclone_v_hps.py**
  - Imports from `axi3.py` (Integrates AXI3 interface for Cyclone V HPS configurations).

## Signal and Stream Handling
- **stream.py**
  - Imports from:
    - `bus.py`
    - `constants.py` (Handles streams of data, potentially integrating with bus interfaces).

- **misc.py**
  - No imports detailed, but possibly includes utilities like synchronizers or delays.

## Audio Processing
- **convolve.py**
  - Imports from:
    - `constants.py`
    - `stream.py` (Handles convolution operations for audio processing).

- **mic.py**
  - Imports from:
    - `constants.py`
    - `stream.py` (Handles microphone data capture and processing).

## System Top-Level Configuration
- **top.py**
  - Imports from:
    - `bus.py`
    - `constants.py`
    - `mic.py`
    - `convolve.py`
    - `stream.py` (Coordinates top-level system integration and module interactions).

## FPGA and System Configuration
- **fpga_top.py**
  - Imports from:
    - `top.py`
    - `constants.py`
    - `mic.py`
    - `convolve.py`
    - `cyclone_v_pll.py`
    - `axi3_csr.py`
    - `cyclone_v_hps.py`
    - `bus.py`
    - `axi3.py` (Defines FPGA-specific configurations and top-level FPGA integration).

- **cyclone_v_pll.py**
  - No imports detailed (likely manages PLL configurations specific to Cyclone V).

## Simulation
- **sim_top.py**
  - Imports from:
    - `top.py`
    - `constants.py`
    - `mic.py`
    - `convolve.py`
    - `bus.py` (Sets up simulation environments, integrating components for test scenarios).

## Miscellaneous
- **misc.py** could contain miscellaneous utilities like delays, synchronizers, or other small components shared across various parts of the project.
