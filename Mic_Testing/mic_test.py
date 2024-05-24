
from amaranth import *
from amaranth.lib.wiring import Component
from amaranth.lib.wiring import Out, In


from .mic import MicClockGenerator
from .mic import MicDataReceiver

MIC_DATA_BITS = 24 # each word is a signed 24 bit number
MIC_FRAME_BITS = 64 # 64 data bits per data frame from the microphone


class MicTest(Component):
    mic_sck: Out(1)
    mic_ws: Out(1)
    mic_data_raw: In(1)

    sample_l: Out(signed(MIC_DATA_BITS))
    sample_r: Out(signed(MIC_DATA_BITS))
    sample_new: Out(1)

    def elaborate(self, platform):
        m = Module()

        m.submodules.mic_clk = mic_clk = MicClockGenerator()
        m.submodules.mic_rcv = mic_rcv = MicDataReceiver()

        # wire clock to data receiver
        m.d.comb += [
            mic_rcv.mic_sck.eq(mic_clk.mic_sck),
            mic_rcv.mic_data_sof_sync.eq(mic_clk.mic_data_sof_sync),
        ]

        # wire actual microphone input
        m.d.comb += [
            self.mic_sck.eq(mic_clk.mic_sck),
            self.mic_ws.eq(mic_clk.mic_ws),
            mic_rcv.mic_data_raw.eq(self.mic_data_raw),
        ]

        # wire test outputs
        m.d.comb += [
            self.sample_l.eq(mic_rcv.sample_l),
            self.sample_r.eq(mic_rcv.sample_r),
            self.sample_new.eq(mic_rcv.sample_new),
        ]

        return m

def test():
    from amaranth.sim import Simulator

    top = MicTest()
    sim = Simulator(top)
    sim.add_clock(1e-6, domain="sync")  # Adjust clock period as needed

    def process():
        for _ in range(1000):  # Adjust the number of cycles as needed
            yield

    sim.add_sync_process(process)
    with sim.write_vcd("mic_test.vcd", "mic_test.gtkw", traces=[
        top.mic_sck, top.mic_ws, top.mic_data_raw,
        top.sample_l, top.sample_r, top.sample_new]):
        sim.run()

if __name__ == "__main__":
    test()













