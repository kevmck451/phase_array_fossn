from amaranth import *
from amaranth.lib.wiring import connect
from amaranth.sim.core import Simulator

from .top import Top
from .audio_constants import MIC_FREQ_HZ
from .audio_mic import MicCapture
from .audio_convolve import Convolver
from .hps_bus import FakeAudioRAMBusWriteReceiver

class SimTop(Elaboratable):
    def __init__(self):
        self.top = Top()

    def elaborate(self, platform):
        m = Module()

        m.submodules.top = top = self.top
        m.submodules.fake_rx = fake_rx = FakeAudioRAMBusWriteReceiver()

        connect(m, top.audio_ram, fake_rx.audio_ram)

        return m

def run_sim():
    sim_top = SimTop()
    top = sim_top.top
    sim = Simulator(sim_top)
    sim.add_clock(1/50e6, domain="sync")
    sim.add_clock(1/(MIC_FREQ_HZ*MicCapture.REL_FREQ), domain="mic_capture")
    sim.add_clock(1/(MIC_FREQ_HZ*Convolver.REL_FREQ), domain="convolver")

    # feed some data to the mic after a bit
    def mic_proc():
        for _ in range(64):
            yield
        yield top.mic_data_raw.eq(1)
        yield

    def reg_proc():
        def write(addr, data):
            yield top.csr_bus.addr.eq(addr)
            yield top.csr_bus.w_data.eq(data)
            yield top.csr_bus.w_stb.eq(1)
            yield
            yield top.csr_bus.w_stb.eq(0)
            yield

        for _ in range(512):
            yield

        # request switch to fake mics
        yield from write(5, 1)

        for _ in range(3300-512): # delay until a nice time to switch
            yield

        # request a buffer switch
        yield from write(2, 1)

        for _ in range(50):
            yield

        # request an increase in gain
        yield from write(4, 1)

        for _ in range(2048):
            yield

        # request to write raw mic data
        yield from write(4, 0) # and turn gain back down to see that accurately
        yield from write(10, 1)

    sim.add_sync_process(mic_proc, domain="sync")
    sim.add_sync_process(reg_proc, domain="sync")

    mod_traces = []
    for name in top.signature.members.keys():
        t = getattr(top, name)
        if isinstance(t, Signal): mod_traces.append(t)

    clk_hack = sim._design.fragment.domains["sync"].clk
    with sim.write_vcd("sim_top.vcd", "sim_top.gtkw",
            traces=[clk_hack, *mod_traces]):
        sim.run_until((1/MIC_FREQ_HZ)*16, run_passive=True)

if __name__ == "__main__":
    run_sim()
