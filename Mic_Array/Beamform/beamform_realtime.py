


from Mic_Array.AudioStreamSimulator import AudioStreamSimulator
from Filters.audio import Audio




from queue import Queue
import time















if __name__ == '__main__':




    # initial set up
    # 1. Set up Mic Coordinates / Map Ch's to Positions (WILL ONLY HAPPEN ONCE)
    # 2. generate a set of coeffs for a particular set of angles based on a temp (WILL HAPPEN PERIODICALLY)
        # save those values because they will be used until temp goes outside some range
    # 3. Beamform (HAPPENING WHEN DATA IS AVAILABLE TO BEAMFORM)
        # will beamforming small chunks and then appending the end affect it?

    thetas = [-70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70]
    phis = [0]  # azimuth angle: neg is below and pos is above
    temp_F = 86  # temperature in Fahrenheit

    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    filename = 'cars_drive_by_150m_BF_(-70, 70)-(0)'
    filepath = f'{base_path}/Tests/18_beamformed/{filename}.wav'
    audio = Audio(filepath=filepath, num_channels=len(thetas))
    chunk_size_seconds = 0.5





    stream = AudioStreamSimulator(audio, chunk_size_seconds)
    stream.start_stream()


    while stream.running:
        if not stream.queue.empty():
            print('BEAMFORMING----------')






        time.sleep(0.25)