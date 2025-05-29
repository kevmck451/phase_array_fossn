from Application.engine.beamform.beamform import Beamform
from Application.engine.filters.processor import Processing
from Application.engine.detectors.pca_calculator import PCA_Calculator
from Application.engine.detectors.detector import Detector

import queue
import numpy as np
import threading

class Calibration_All:
    def __init__(self, audio_streamer, temp, array_config, save_path):
        self.audio_streamer       = audio_streamer
        self.temp                 = temp
        self.array_config         = array_config
        self.save_path            = save_path

        thetas_1 = list(range(-90, 91, 2))
        thetas_2 = list(range(-90, 91, 5))
        self.thetas = sorted(set(thetas_1 + thetas_2))
        print(self.thetas)
        self.phis   = [0]

        print(self.array_config.title)

        if self.array_config.title == 'Rectangular Array':
            self.beam_mix_list = [self.array_config.beam_mix_1,
                                  self.array_config.beam_mix_2,]
        else:
            self.beam_mix_list = [
                self.array_config.beam_mix_1,
                self.array_config.beam_mix_2,
                self.array_config.beam_mix_3,
                self.array_config.beam_mix_4,
            ]

        # instantiate one object per mix
        self.beamformer_list     = [
            Beamform(self.thetas, self.phis, self.temp, self.array_config, m)
            for m in self.beam_mix_list
        ]
        self.processor_list      = []
        for m in self.beam_mix_list:
            p = Processing()
            p.processing_chain = m.processing_chain
            self.processor_list.append(p)
        self.pca_calculator_list = [PCA_Calculator() for _ in self.beam_mix_list]
        self.detector_list       = [Detector()     for _ in self.beam_mix_list]

        self.run_calibration     = True
        self.calibration_finished = False
        self.shared_audio_queue  = queue.Queue(maxsize=100)

        self._start_everything()

    def _start_everything(self):
        self.threads = []

        def start(fn, name):
            t = threading.Thread(target=fn, daemon=True, name=name)
            t.start()
            self.threads.append(t)

        start(self._audio_stream, "AudioStream")

        for idx, bf in enumerate(self.beamformer_list):
            start(lambda bf=bf: self._beamform_worker(bf), f"Beamform-{idx}")

        for idx, (proc, bf) in enumerate(zip(self.processor_list, self.beamformer_list)):
            start(lambda proc=proc, bf=bf: self._process_worker(proc, bf), f"Process-{idx}")

        for idx, (calc, proc) in enumerate(zip(self.pca_calculator_list, self.processor_list)):
            start(lambda calc=calc, proc=proc: self._pca_worker(calc, proc), f"PCA-{idx}")

        for idx, (det, calc) in enumerate(zip(self.detector_list, self.pca_calculator_list)):
            start(lambda det=det, calc=calc: self._baseline_worker(det, calc), f"Baseline-{idx}")

    def stop_everything(self):
        # 1) tell threads to exit
        self.run_calibration = False

        # 2) drain shared_audio_queue into each beamformer
        while True:
            try:
                data = self.shared_audio_queue.get_nowait()
            except queue.Empty:
                break
            for bf in self.beamformer_list:
                bf.beamform_data(np.copy(data))

        # 3) drain each beamformer.queue into its processor
        for proc, bf in zip(self.processor_list, self.beamformer_list):
            while True:
                try:
                    data = bf.queue.get_nowait()
                except queue.Empty:
                    break
                proc.process_data(data)

        # 4) drain each processor.queue into its PCA calculator
        for calc, proc in zip(self.pca_calculator_list, self.processor_list):
            while True:
                try:
                    data = proc.queue.get_nowait()
                except queue.Empty:
                    break
                calc.process_chunk(data)

        # 5) drain each calculator.queue into its detector
        for det, calc in zip(self.detector_list, self.pca_calculator_list):
            while True:
                try:
                    data = calc.queue.get_nowait()
                except queue.Empty:
                    break
                det.calculate_baseline(data)

        # 6) wait for all threads to finish cleanly
        for t in self.threads:
            t.join(timeout=2)

        # 7) save and mark complete
        self._save_calibration()
        self.calibration_finished = True

    def _audio_stream(self):
        while self.run_calibration:
            try:
                data = self.audio_streamer.queue.get(timeout=0.1)
                self.shared_audio_queue.put(data, timeout=0.1)
            except (queue.Empty, queue.Full):
                pass

    def _beamform_worker(self, beamformer):
        while self.run_calibration:
            try:
                data = self.shared_audio_queue.get(timeout=0.1)
                beamformer.beamform_data(np.copy(data))
            except queue.Empty:
                continue

    def _process_worker(self, processor, beamformer):
        while self.run_calibration:
            try:
                chunk = beamformer.queue.get(timeout=0.1)
                processor.process_data(chunk)
            except queue.Empty:
                continue

    def _pca_worker(self, calculator, processor):
        while self.run_calibration:
            try:
                chunk = processor.queue.get(timeout=0.1)
                calculator.process_chunk(chunk)
            except queue.Empty:
                continue

    def _baseline_worker(self, detector, calculator):
        while self.run_calibration:
            try:
                chunk = calculator.queue.get(timeout=0.1)
                detector.calculate_baseline(chunk)
            except queue.Empty:
                continue

    def _save_calibration(self):
        for detector, mix in zip(self.detector_list, self.beam_mix_list):
            np.save(f'{self.save_path}/{mix.name}_baseline_means.npy',
                    detector.baseline_means)
            np.save(f'{self.save_path}/{mix.name}_baseline_stds.npy',
                    detector.baseline_stds)
            print(f'Baseline stats saved in folder: {self.save_path}')
