

import Mic_Array.array_config as array_config


from Filters.noise_reduction import noise_reduction_filter
from Filters.high_pass import high_pass_filter
from Filters.down_sample import downsample
from Filters.normalize import normalize




from queue import Queue



class ProcessBeamformedData:
    def __init__(self):
        self.processing_chain = None
        self.nr_std_threshold = None
        self.bottom_cutoff_frequency = None
        self.top_cutoff_frequency = None
        self.new_sample_rate = None

        self.queue = Queue()





















if __name__ == '__main__':
    print()




