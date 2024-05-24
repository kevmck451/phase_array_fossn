# FPGA-Based Audio Processing System Outline

## Top-Level Module
- **Top**
  - Description: Coordinates all sub-modules and manages data flow throughout the system.
  - Dependencies:
    - Blinker
    - MicCapture
    - Convolver
    - SampleStreamFIFO
    - SampleWriter
    - SystemRegs
    - CSR Decoder

## Sub-Modules
### Input and Synchronization
- **Blinker**
  - Description: Manages an LED based on the input from a button, incorporating a debouncing mechanism.
  - Dependencies: None

- **MicCapture** and **MicCaptureRegs**
  - Description: Captures audio data from microphones and provides configurable settings through CSR registers.
  - Dependencies: 
    - FFSynchronizer (for button synchronization in Blinker)
    - SampleStream (for FIFO data handling)

### Data Handling and FIFO Management
- **SampleStreamFIFO**
  - Description: Manages asynchronous FIFOs to transfer data across different clock domains.
  - Dependencies:
    - SampleStream (defines the data signature for streams)

### Processing
- **Convolver**
  - Description: Processes audio data using convolution with pre-loaded coefficients.
  - Dependencies:
    - numpy (for loading and processing coefficient data)

### Configuration and Control
- **SystemRegs**
  - Description: Provides system-wide configuration settings accessible via CSR.
  - Dependencies:
    - csr (from amaranth_soc for CSR register handling)

### CSR Interface and Decoding
- **CSR Decoder**
  - Description: Decodes CSR addresses and routes data to appropriate registers within subsystems.
  - Dependencies:
    - csr (from amaranth_soc for CSR infrastructure)

### Output and Storage
- **SampleWriter**
  - Description: Writes processed or raw audio data to external memory interfaces.
  - Dependencies:
    - AudioRAMBus (for memory interface)
    - SampleStream (for data flow management)

## System Configuration
- **Constants and Settings**
  - Description: Defines system-wide constants such as MIC_FREQ_HZ, NUM_TAPS, NUM_MICS, and NUM_CHANS.
  - Dependencies: None

## External Dependencies
- **numpy**
  - Description: Used for loading and manipulating coefficient data for the Convolver.
- **pathlib**
  - Description: Manages file paths for loading coefficient data.

## Utility and Helper Classes
- **FFSynchronizer**
  - Description: Used within Blinker and potentially other modules to synchronize signals across clock domains.
- **AudioRAMBus**
  - Description: Defines the bus interface for audio data output to external memory.
- **SampleStream**
  - Description: Defines the signature for audio sample data streams used across FIFOs and processing modules.
