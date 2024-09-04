

from Mic_Array.Processing.noise_reduction_array import noise_reduction_filter
from Mic_Array.Processing.high_pass_array import high_pass_filter
from Mic_Array.Processing.normalize import normalize
from Mic_Array.Processing.down_sample import downsample



from queue import Queue



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

        self.processing_chain = {'hp': 1000, 'nm': 100, 'ds': 6000}
        self.nr_std_threshold = None
        self.bottom_cutoff_frequency = None
        self.norm_percent = None
        self.new_sample_rate = None

        self.queue = Queue()


    def process_data(self, data):

        new_data = data

        for process in self.processing_chain:
            if process == 'nr':
                # print(f'Noise Reduction ({process})\t|\tSTD: {self.processing_chain[process]}')
                new_data = noise_reduction_filter(new_data, self.processing_chain[process])


            elif process == 'hp':
                # print(f'High Pass ({process})      \t|\tBC: {self.processing_chain[process]} Hz')
                new_data = high_pass_filter(new_data, self.processing_chain[process])


            elif process == 'nm':
                # print(f'Normalization ({process})  \t|\t%: {self.processing_chain[process]} %')
                new_data = normalize(new_data, self.processing_chain[process])


            elif process == 'ds':
                # print(f'Down Sampling ({process})  \t|\tSR: {self.processing_chain[process]} Hz')
                new_data = downsample(new_data, self.processing_chain[process])


            else:
                print('processing input not recognized')


        self.queue.put(new_data)















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





