

from Application.engine.filters.noise_reduction_array import noise_reduction_filter
from Application.engine.filters.high_pass_array import high_pass_filter
from Application.engine.filters.low_pass_array import low_pass_filter
from Application.engine.filters.normalize import normalize
from Application.engine.filters.down_sample import downsample
from Application.engine.filters.scale import scale



from queue import Queue
import numpy as np




class Processing:
    def __init__(self):

        '''
        Noise Reduction: { 'nr' : std_threshold }
        High Pass: { 'hp' : bottom_cutoff }
        Normalization: { 'nm' : percentage }
        Down Sampling: { 'ds' : sample_rate }

        processing_chain = {'nr' : 0.5,
                            'hp' : 1000,
                            'nm' : 100,
                            'ds' : 6000 }
        '''

        # self.processing_chain = {'hp': 1144, 'nm': 100, 'ds': 6288}
        # self.processing_chain = {'hp': 1144, 'ds': 6288, 'scale': 100}
        self.processing_chain = {'hp': 1144, 'ds': 6288}
        self.nr_std_threshold = None
        self.bottom_cutoff_frequency = None
        self.norm_percent = None
        self.new_sample_rate = None

        self.queue = Queue()

        self.send_to_external_audio_stream = False
        self.external_audio_queue = Queue()

    def process_data(self, data):

        # print(f'Raw Max: {np.max(data)}')
        # print(f'Raw min: {np.min(data)}')

        new_data = data

        for process in self.processing_chain:
            if process == 'nr':
                # print(f'Noise Reduction ({process})\t|\tSTD: {self.processing_chain[process]}')
                new_data = noise_reduction_filter(new_data, self.processing_chain[process])

            elif process == 'lp':
                # print(f'High Pass ({process})      \t|\tBC: {self.processing_chain[process]} Hz')
                new_data = low_pass_filter(new_data, self.processing_chain[process])
                # new_data = low_pass_filter(new_data, self.processing_chain[process], order=8)

            elif process == 'hp':
                new_data = high_pass_filter(new_data, self.processing_chain[process])
                # new_data = high_pass_filter(new_data, self.processing_chain[process], order=8)

                # print(f'HP Max: {np.max(new_data)}')
                # print(f'HP min: {np.min(new_data)}')

            elif process == 'nm':
                # print(f'Normalization ({process})  \t|\t%: {self.processing_chain[process]} %')
                new_data = normalize(new_data, self.processing_chain[process])

                # print(f'NM Max: {np.max(new_data)}')
                # print(f'NM min: {np.min(new_data)}')

            elif process == 'ds':
                # print(f'Down Sampling ({process})  \t|\tSR: {self.processing_chain[process]} Hz')
                new_data = downsample(new_data, self.processing_chain[process])

                # print(f'DS Max: {np.max(new_data)}')
                # print(f'DS min: {np.min(new_data)}')

            elif process == 'scale':
                # print(f'Scaling ({process})  \t|\Factor: {self.processing_chain[process]}')
                new_data = scale(new_data, self.processing_chain[process])

                # print(f'S Max: {np.max(new_data)}')
                # print(f'S min: {np.min(new_data)}')

            else:
                print('processing input not recognized')



        self.queue.put(new_data)

        if self.send_to_external_audio_stream:
            self.external_audio_queue.put(new_data)














if __name__ == '__main__':
    process = Processing()
    # process.processing_chain = { 'nr' : 0.5,
    #                              'hp' : 1000,
    #                              'nm' : 100,
    #                              'ds' : 6000 }

    process.processing_chain = {'hp': 1000,
                                'nm': 100,
                                'ds': 6000}


    process.process_data(data = None)





