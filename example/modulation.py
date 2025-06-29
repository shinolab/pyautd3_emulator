import numpy as np
from matplotlib import pyplot as plt
from pyautd3 import AUTD3, Focus, Hz, Intensity, Silencer, Sine, Uniform
from pyautd3.driver.firmware.fpga.phase import Phase
from pyautd3.gain.focus import FocusOption
from pyautd3.modulation.sine import SineOption
from pyautd3.utils import Duration

from pyautd3_emulator import Emulator, InstantRecordOption, RangeXYZ, Recorder

if __name__ == "__main__":
    with Emulator([AUTD3(pos=[0.0, 0.0, 0.0], rot=[1.0, 0.0, 0.0, 0.0])]) as emulator:
        # pulse width under 200Hz sine modulation with silencer
        def f(autd: Recorder) -> None:
            autd.send(Silencer())
            autd.send((Sine(freq=200.0 * Hz, option=SineOption()), Uniform(intensity=Intensity(0xFF), phase=Phase(0))))
            autd.tick(Duration.from_millis(10))

        record = emulator.record(f)

        df = record.pulse_width()
        t = [float(c.replace("pulse_width@", "").replace("[ns]", "")) / 1_000_000 for c in df.columns]
        pulse_width = df.row(0)
        plt.plot(t, pulse_width)
        plt.xlim(5, 10)
        plt.ylim(0, 256)
        plt.xlabel("time [ms]")
        plt.ylabel("pulse width")
        plt.title("pulse width under 200Hz sine modulation with silencer")
        plt.show()

        # pulse width under 200Hz sine modulation without silencer
        def f(autd: Recorder) -> None:
            autd.send(Silencer.disable())
            autd.send((Sine(freq=200.0 * Hz, option=SineOption()), Uniform(intensity=Intensity(0xFF), phase=Phase(0))))
            autd.tick(Duration.from_millis(10))

        record = emulator.record(f)

        df = record.pulse_width()
        t = [float(c.replace("pulse_width@", "").replace("[ns]", "")) / 1_000_000 for c in df.columns]
        pulse_width = df.row(0)
        plt.plot(t, pulse_width)
        plt.xlim(5, 10)
        plt.ylim(0, 256)
        plt.xlabel("time [ms]")
        plt.ylabel("pulse width")
        plt.title("pulse width under 200Hz sine modulation with silencer")
        plt.show()

        # plot sound pressure at focus under 200Hz sin modulation with silencer
        focus = emulator.center() + np.array([0.0, 0.0, 150.0])

        def f(autd: Recorder) -> None:
            autd.send(Silencer())
            autd.send((Sine(freq=200.0 * Hz, option=SineOption()), Focus(pos=focus, option=FocusOption())))
            autd.tick(Duration.from_millis(20))

        record = emulator.record(f)

        print("Calculating sound pressure at focus under 200Hz sin modulation with silencer...")
        sound_field = record.sound_field(
            RangeXYZ(
                x=(focus[0], focus[0]),
                y=(focus[1], focus[1]),
                z=(focus[2], focus[2]),
                resolution=1.0,
            ),
            InstantRecordOption(
                time_step=Duration.from_micros(1),
                print_progress=True,
            ),
        )

        df = sound_field.next(Duration.from_millis(20))
        time = np.array([float(t.replace("p[Pa]@", "").replace("[ns]", "")) for t in df.columns])
        p = df.row(0)
        plt.plot(time / 1000_000, p)
        plt.xlim(0, 20)
        plt.xlabel("time [ms]")
        plt.ylabel("p[Pa]")
        plt.title("sound pressure at focus under 200Hz sin modulation with silencer")
        plt.show()
