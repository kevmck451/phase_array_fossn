# Forward Operations Security Sensor Network (FOSSN)

## Project Overview

What they want from us:
	- easily deployable networked sensor system is needed to provide automated security monitoring
	- develop concepts for a Forward Operations Sensor Network

The sensor system should 
	- detect encroaching personnel and vehicles (ground and aerial)
	- presence of chemical, biological, radiological, and nuclear (CBRN) materials
	- system of unattended sensors will communicate via a network
	- Autonomous algorithms will consolidate sensor inputs and provide summary notifications of activity within the area monitored to personnel in the FO unit

Results of this study:
	- a demonstration of several key technologies necessary for building an effective FOSSN 
	- a detailed plan for the full development of the FOSSN

Complementary sensors of acoustic

Unattended Ground Sensors (UGS)
Memphis has developed the means for implementing acoustic, magnetic, and hyperspectral sensors for UAS that can be translated to UGS sensing

The FOSSN team will translate these wide area coverage sensors into an UGS configuration and will demonstrate a VIS and LWIR capability for wide area coverage to include the detection and recognition of humans and vehicles.  The FOSSN team will also perform field experimentation to determine the performance of these systems in the range at which these systems effectively engage humans and military vehicles, including threat UAS.

The FOSSN team will also leverage existing phased array acoustic sensing to a UGS configuration

All sensors will be tied together leveraging Named Data Networking (NDN) and multi-hop ad hoc communications developed for the ARL program

Based on prior experience and input from task 3.1, research areas needed for the development of a complete and operationally effective system will be developed. For each area, recommendations regarding technical approaches will be made and a report produced. 

3.4.2 Phased Array Acoustic Sensor Research
	- The FOSSN team will develop a wide area coverage acoustic with at least a 180 degree FOV with resolution sufficient to localize a target direction when combined with other sensing modalities. This sensor will leverage technologies developed for the UAS based acoustic interrogator mission.
	- The FOSSN team will demonstrate the acoustic UGS systems in the field.  The system will be demonstrated in the field with a ground sensor coupled to a tabletop computer that can show the performance of the system.
	- The FOSSN team will determine the performance of the wide area acoustic system.  A theoretical performance will be provided as well as a field experiment/demonstration that provides the range at which aerial and ground vehicles can be detected and recognized.

The FOSSN team will develop an overall plan for developing a system that meets the needs of field artillery security. This plan will detail any needed technology development and the necessary resources to execute the plan. 

Test and Evaluation (T&E) Plan – Based on the results of laboratory and field evaluations and demonstrations, an overall T&E plan will be developed for a complete field artillery security system. 

# Repo Contents

## I. Beamform

## II. Circuit Boards

### 1. DE10_Shield

### 2. Mic_Antenna

## III. Documents

## IV. FPGA SoC Setup

1. Creating a NixOS for an FPGA SoC
2. Initial Build for SD Card Image
3. Initial Installation on DE10
4. Developing Application and Maintenance


### 1. FPGA Folder

- The Altera DE10 Nano uses Quartus to synthesize/place & route the HDL code to the FPGA 
- Quartus is only able to do this using an intel processor
- Nix is linux
- so in order to develop software on this device with Nix, a computer with intel processor and linux is needed

### 2. Nix
- Development Environment
- Package Management
- FPGA Interaction Tool Chain

### 3. Design

### 4. Docs





