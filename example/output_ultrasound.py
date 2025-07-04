from matplotlib import pyplot as plt
from pyautd3 import AUTD3, Intensity, Phase, Silencer, Static, Uniform
from pyautd3.utils import Duration

from pyautd3_emulator import Emulator, Recorder

if __name__ == "__main__":
    with Emulator([AUTD3(pos=[0.0, 0.0, 0.0], rot=[1.0, 0.0, 0.0, 0.0])]) as emulator:
        # output voltage
        def f(autd: Recorder) -> None:
            autd.send(Silencer.disable())
            autd.send((Static(intensity=0xFF), Uniform(phase=Phase(0x40), intensity=Intensity(0xFF))))
            autd.tick(Duration.from_millis(1))

        record = emulator.record(f)

        df = record.output_voltage()
        t = [float(c.replace("voltage[V]@", "").replace("[25us/512]", "")) * 0.025 / 512.0 for c in df.columns]
        v = df.row(0)
        plt.plot(t, v)
        plt.xlim(0, 1)
        plt.ylim(-15, 15)
        plt.xlabel("time [ms]")
        plt.ylabel("Voltage [V]")
        plt.title("output voltage")
        plt.show()

        df = record.output_ultrasound()
        t = [float(c.replace("p[a.u.]@", "").replace("[25us/512]", "")) * 0.025 / 512.0 for c in df.columns]
        v = df.row(0)
        plt.plot(t, v)
        plt.xlim(0, 1)
        plt.ylim(-1.1, 1.1)
        plt.xlabel("time [ms]")
        plt.ylabel("p [a.u.]")
        plt.title("output ultrasound")
        plt.show()
