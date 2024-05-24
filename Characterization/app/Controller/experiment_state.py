



class Experiment:
    def __init__(self):
        self.audio_sample_list = list
        self.channel_list = list

        self.current_index = 0
        self.current_stim_number = ''
        self.current_speaker_projecting = ''
        self.current_speaker_selected = ''

        self.output_file = object
        self.experiment_in_progress = bool
        self.reaction_time = int
        self.max_index = int


    def get_current_stim_number(self):
        return self.current_stim_number

    def update_current_stim_number(self, number):
        self.current_stim_number = str(number + 1)

    def set_audio_channel_list(self, audio_samples_list, channel_list):
        self.audio_sample_list = audio_samples_list
        self.channel_list = channel_list







