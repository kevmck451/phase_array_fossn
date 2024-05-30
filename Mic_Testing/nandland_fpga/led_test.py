from amaranth import *
from amaranth_boards.nandland_go import NandlandGoPlatform

class LEDTest(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        led1 = platform.request("led", 0)
        led2 = platform.request("led", 1)
        led3 = platform.request("led", 2)
        led4 = platform.request("led", 3)

        button1 = platform.request("button", 3)

        counter = Signal(28)

        # Blink LED1
        m.d.sync += [counter.eq(counter + 1)]

        m.d.comb += [
            led1.o.eq(counter[-1]),
            led2.o.eq(counter[-2]),
            led3.o.eq(counter[-3]),
            led4.o.eq(counter[-4]),
        ]

        # m.d.comb += led4.o.eq(button1.i)

        return m

if __name__ == "__main__":
    platform = NandlandGoPlatform()
    platform.build(LEDTest(), do_program=True)
