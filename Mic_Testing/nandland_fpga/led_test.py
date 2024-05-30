from amaranth import *
from amaranth.build import *
from amaranth_boards.nandland_go import NandlandGoPlatform

class LEDTest(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        led1 = platform.request("led", 0)
        led2 = platform.request("led", 1)

        counter = Signal(24)

        # Blink LED1
        m.d.sync += counter.eq(counter + 1)
        m.d.comb += [
            led1.o.eq(counter[-1]),  # Toggle LED1 based on the counter
            led2.o.eq(~counter[-1]),  # Toggle LED2 in the opposite phase
        ]

        return m

if __name__ == "__main__":
    platform = NandlandGoPlatform()
    platform.build(LEDTest(), do_program=True)
