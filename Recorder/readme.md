# Controller


## Audio Receiver
- The `AudioReceiver` class is designed to collect RAW audio data from an FPGA server
- It connects to the server over a socket, receives audio data in chunks, and stores it in a queue for processing
- This implementation is intended to handle multi-channel audio data in real-time
- Connects to an FPGA server using a socket
- Receives audio data in real-time
- Supports multi-channel audio data
- Stores received audio data in a thread-safe queue
- Provides a method to retrieve audio data for processing




```zsh
journalctl -fu start-mic-server
```







