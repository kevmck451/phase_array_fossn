
from Controller.AudioReceiver import AudioReceiver



import time










def main():
    chan_count = 48
    audio_receiver = AudioReceiver(chan_count)


    print("Press 's' to stop recording and save to a WAV file.")

    while True:
        data = audio_receiver.get_audio_data()
        if data is not None:
            print(f'Type: {type(data)}')
            print(f'Shape: {data.shape}')

        time.sleep(0.1)


if __name__ == "__main__":
    main()



