from amaranth import *
from amaranth.sim import Simulator, Settle

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

        # Calculate the number of clock cycles per bit and word select toggle
        bit_clock_div = self.clock_freq // (self.sample_rate * self.bit_depth * 2)
        ws_clock_div = self.clock_freq // (self.sample_rate * 2)

        bit_counter = Signal(range(bit_clock_div))
        ws_counter = Signal(range(ws_clock_div))
        bit_index = Signal(range(self.bit_depth))

        left_data_reg = Signal(self.bit_depth)
        right_data_reg = Signal(self.bit_depth)

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
                m.next = "LEFT_CHANNEL"

            with m.State("LEFT_CHANNEL"):
                m.d.sync += self.ws.eq(0)
                with m.If(ws_counter == ws_clock_div - 1):
                    m.d.sync += ws_counter.eq(0)
                with m.Else():
                    m.d.sync += ws_counter.eq(ws_counter + 1)

                with m.If(bit_counter == bit_clock_div - 1):
                    m.d.sync += bit_counter.eq(0)
                    m.d.sync += self.sck.eq(~self.sck)
                    with m.If(self.sck == 0):
                        m.d.sync += [
                            bit_index.eq(bit_index + 1),
                            self.sd.eq(self.left_data.bit_select(bit_index, 1))
                        ]
                        with m.If(bit_index == self.bit_depth - 1):
                            m.next = "RIGHT_CHANNEL"
                            m.d.sync += bit_index.eq(0)
                with m.Else():
                    m.d.sync += bit_counter.eq(bit_counter + 1)

            with m.State("RIGHT_CHANNEL"):
                m.d.sync += self.ws.eq(1)
                with m.If(ws_counter == ws_clock_div - 1):
                    m.d.sync += ws_counter.eq(0)
                with m.Else():
                    m.d.sync += ws_counter.eq(ws_counter + 1)

                with m.If(bit_counter == bit_clock_div - 1):
                    m.d.sync += bit_counter.eq(0)
                    m.d.sync += self.sck.eq(~self.sck)
                    with m.If(self.sck == 0):
                        m.d.sync += [
                            bit_index.eq(bit_index + 1),
                            self.sd.eq(self.right_data.bit_select(bit_index, 1))
                        ]
                        with m.If(bit_index == self.bit_depth - 1):
                            m.next = "LEFT_CHANNEL"
                            m.d.sync += bit_index.eq(0)
                with m.Else():
                    m.d.sync += bit_counter.eq(bit_counter + 1)

        return m

# Testbench
if __name__ == "__main__":
    dut = I2SController()



    def process():
        # Simulate input data for left and right channels
        yield dut.left_data.eq(0x000001)
        yield dut.right_data.eq(0x000000)

        bit_index = 1
        for _ in range(100):
            yield

            clock = (yield dut.sck)
            word_select = (yield dut.ws)
            data = (yield dut.sd)

            if word_select == 0:
                print(f"LEFT\t|\tBIT: {bit_index}\t|\tsck: {clock}\t|\tws: {word_select}\t|\tsd: {data}")
            else:
                print(f"RIGHT\t|\tBIT: {bit_index}\t|\tsck: {clock}\t|\tws: {word_select}\t|\tsd: {data}")

            if bit_index == 24: bit_index = 1
            else: bit_index += 1

    sim = Simulator(dut)
    sim.add_clock(1e-6)  # 1 MHz clock
    sim.add_sync_process(process)
    with sim.write_vcd("i2s_test.vcd", "i2s_test.gtkw"):
        sim.run()
