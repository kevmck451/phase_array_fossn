from amaranth import *
from amaranth.sim import Simulator

class I2SController(Elaboratable):
    def __init__(self, bit_depth=24, sample_rate=48000, clock_freq=12_288_000):
        self.bit_depth = bit_depth
        self.sample_rate = sample_rate
        self.clock_freq = clock_freq

        # I2S signals
        self.sck = Signal()  # Serial Clock
        self.ws = Signal()   # Word Select (Left/Right)
        self.sd = Signal()   # Serial Data

        # Input signals for left and right channel data
        self.left_data = Signal(bit_depth)
        self.right_data = Signal(bit_depth)

    def elaborate(self, platform):
        m = Module()

        bit_clock_div = self.clock_freq // (self.sample_rate * self.bit_depth * 2)
        ws_clock_div = self.clock_freq // (self.sample_rate * 2)

        bit_counter = Signal(range(bit_clock_div))
        ws_counter = Signal(range(ws_clock_div))
        bit_index = Signal(range(self.bit_depth), reset_less=True)

        left_data_reg = Signal(self.bit_depth)
        right_data_reg = Signal(self.bit_depth)

        m.d.sync += [
            bit_counter.eq(bit_counter + 1),
            ws_counter.eq(ws_counter + 1)
        ]

        with m.FSM():
            with m.State("IDLE"):
                m.d.sync += [
                    bit_counter.eq(0),
                    ws_counter.eq(0),
                    bit_index.eq(0),
                    self.sck.eq(0),
                    self.ws.eq(0),
                    self.sd.eq(0)
                ]
                m.d.sync += [
                    left_data_reg.eq(self.left_data),
                    right_data_reg.eq(self.right_data)
                ]
                m.next = "LEFT_CHANNEL"

            with m.State("LEFT_CHANNEL"):
                m.d.sync += self.ws.eq(0)
                with m.If(bit_counter == bit_clock_div - 1):
                    m.d.sync += [
                        bit_counter.eq(0),
                        self.sck.eq(~self.sck)
                    ]
                    with m.If(self.sck == 0):
                        m.d.sync += [
                            bit_index.eq(bit_index + 1),
                            self.sd.eq(left_data_reg.bit_select(self.bit_depth - 1 - bit_index, 1).as_unsigned())
                        ]
                        with m.If(bit_index == self.bit_depth - 1):
                            m.d.sync += bit_index.eq(0)
                            m.next = "RIGHT_CHANNEL"
                with m.Else():
                    m.d.sync += bit_counter.eq(bit_counter + 1)

            with m.State("RIGHT_CHANNEL"):
                m.d.sync += self.ws.eq(1)
                with m.If(bit_counter == bit_clock_div - 1):
                    m.d.sync += [
                        bit_counter.eq(0),
                        self.sck.eq(~self.sck)
                    ]
                    with m.If(self.sck == 0):
                        m.d.sync += [
                            bit_index.eq(bit_index + 1),
                            self.sd.eq(right_data_reg.bit_select(self.bit_depth - 1 - bit_index, 1).as_unsigned())
                        ]
                        with m.If(bit_index == self.bit_depth - 1):
                            m.d.sync += bit_index.eq(0)
                            m.next = "LEFT_CHANNEL"
                with m.Else():
                    m.d.sync += bit_counter.eq(bit_counter + 1)

        return m

# Testbench
if __name__ == "__main__":
    dut = I2SController()

    def process():
        yield dut.left_data.eq(0xFFFFFF)
        yield dut.right_data.eq(0x000000)

        for _ in range(500):
            yield

            clock = (yield dut.sck)
            word_select = (yield dut.ws)
            data = (yield dut.sd)

            print(f"sck: {clock}\t|\tws: {word_select}\t|\tsd: {data}")

    sim = Simulator(dut)
    sim.add_clock(1e-6)  # 1 MHz clock
    sim.add_sync_process(process)
    with sim.write_vcd("i2s_test.vcd", "i2s_test.gtkw"):
        sim.run()
