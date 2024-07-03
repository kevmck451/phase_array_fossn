# Microphone Testing

- to test microphones, module sockets were soldered to an extra mic antenna (sockets in part list in docs)
- this mic antenna was also labeled as to not mix up the order of channels when testing

|          |          |
|----------|----------|
| 1L (ch2) | 2L (ch4) |
| 1R (ch1) | 2R (ch3) |
| 3L (ch6) | 4L (ch8) |
| 3R (ch5) | 4R (ch7) |

- testing the sensitivity of each mic ensures that all mics that are "hard wired" to the antennas are all in the same range
- a [REED R8090 Sound Level Calibrator](https://www.amazon.com/Instruments-R8090-Calibrator-Diameter-Microphones/dp/B008S0OVR2/) was used for our testing

## Testing Process
- start FPGA server running in raw mode at gain level 10
```zsh
sudo server -r -g 10 
```
- all mics were tested and results recorded in the MasterMicTest.csv in a quiet room
- using this data, the rms range variable in ```TestMics.py``` was selected for pass / fail thresholds
- it would be recommended to do this process yourself if your conditions are significantly different

### Testing
- run the ```TestMics.py``` script
- slide the calibrator to 94dB setting
- place calibrator on top of mic so that mic is securely in the opening
  - the fit should be almost exact so make sure calibrator is not angled and perfect level/centered on mic
  - small variation in calibrator placement could change the results so try to be consistent
- once you feel the calibrator is correctly positioned, press enter where ever the script is being run
- the script will collect 2 seconds worth of data and calculate the RMS value
- mics that are within the desired range will receive a PASS and other a fail
- once you have the number of mics needed for your array at the desired sensitivity, testing is complete
- the other mics are still good obviously so maybe save them for another project





















