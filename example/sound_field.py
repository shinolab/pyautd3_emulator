import numpy as np
import polars as pl
from matplotlib import animation, colorbar
from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from pyautd3 import AUTD3, FociSTM, Focus, SamplingConfig, Silencer, Static, kHz
from pyautd3.gain.focus import FocusOption
from pyautd3.utils import Duration

from pyautd3_emulator import Emulator, InstantRecordOption, RangeXYZ, Recorder


def plot_focus() -> None:
    with Emulator([AUTD3(pos=[0.0, 0.0, 0.0], rot=[1.0, 0.0, 0.0, 0.0])]) as emulator:
        focus = emulator.center() + np.array([0.0, 0.0, 150.0])

        def f(autd: Recorder) -> None:
            autd.send(Silencer.disable())
            autd.send((Static(intensity=0xFF), Focus(pos=focus, option=FocusOption())))
            autd.tick(Duration.from_millis(1))

        record = emulator.record(f)

        sound_field = record.sound_field(
            RangeXYZ(
                x=(focus[0] - 20.0, focus[0] + 20.0),
                y=(focus[1] - 20.0, focus[1] + 20.0),
                z=(focus[2], focus[2]),
                resolution=1.0,
            ),
            InstantRecordOption(
                time_step=Duration.from_micros(1),
                print_progress=True,
                gpu=True,
            ),
        )
        print("Calculating sound field around focus...")

        df = sound_field.observe_points()
        x = np.unique(df["x[mm]"])
        y = np.unique(df["y[mm]"])

        df = sound_field.next(Duration.from_millis(1))

        times = [float(c.replace("p[Pa]@", "").replace("[ns]", "")) / 1000_000 for c in df.columns]
        p = df.get_columns()
        times = times[440:]
        p = p[440:]

        fig = plt.figure()
        spec = fig.add_gridspec(ncols=2, nrows=1, width_ratios=[10, 1])
        ax = fig.add_subplot(spec[0], projection="3d")
        cax = fig.add_subplot(spec[1])
        colorbar.ColorbarBase(cax, cmap="jet", norm=Normalize(vmin=-10e3, vmax=10e3))

        p_shape = [len(y), len(x)]
        aspect = (len(x), len(y), len(x))
        x, y = np.meshgrid(x, y)

        def anim(i: int):  # noqa: ANN202
            ax.cla()
            z = p[i].to_numpy().reshape(p_shape)
            plot = ax.plot_surface(x, y, z, shade=False, cmap="jet", norm=Normalize(vmin=-10e3, vmax=10e3))  # type: ignore[attr-defined]
            ax.set_zlim(-10e3, 10e3)  # type: ignore[attr-defined]
            ax.set_box_aspect(aspect)  # type: ignore[arg-type]
            ax.set_title(f"t={times[i]:.3f} [ms]")
            return plot

        _ = animation.FuncAnimation(fig, anim, frames=len(p), interval=1, repeat=False, blit=False)
        plt.show()

        # plot RMS
        fig = plt.figure()
        spec = fig.add_gridspec(ncols=2, nrows=1, width_ratios=[10, 1])
        ax = fig.add_subplot(spec[0], projection="3d")
        cax = fig.add_subplot(spec[1])
        rms = df.select(pl.exclude(r"^.\[mm\]$")).select(pl.all().pow(2)).mean_horizontal().sqrt()
        ax.plot_surface(  # type: ignore[attr-defined]
            x,
            y,
            rms.to_numpy().reshape(p_shape),
            shade=False,
            cmap="jet",
            norm=Normalize(vmin=0.0, vmax=rms.max()),  # type: ignore[arg-type]
        )
        colorbar.ColorbarBase(cax, cmap="jet", norm=Normalize(vmin=0.0, vmax=rms.max()))  # type: ignore[arg-type]
        plt.show()


def plot_stm() -> None:
    with Emulator([AUTD3(pos=[0.0, 0.0, 0.0], rot=[1.0, 0.0, 0.0, 0.0])]) as emulator:
        focus = emulator.center() + np.array([0.0, 0.0, 150.0])

        def f(autd: Recorder) -> None:
            autd.send(Silencer())
            autd.send(
                (
                    Static(intensity=0xFF),
                    FociSTM(
                        foci=(focus + 20.0 * np.array([np.cos(theta), np.sin(theta), 0]) for theta in (2.0 * np.pi * i / 4 for i in range(4))),
                        config=SamplingConfig(1.0 * kHz),
                    ),
                ),
            )
            autd.tick(Duration.from_millis(5))

        record = emulator.record(f)

        sound_field = record.sound_field(
            RangeXYZ(
                x=(focus[0] - 30.0, focus[0] + 30.0),
                y=(focus[1] - 30.0, focus[1] + 30.0),
                z=(focus[2], focus[2]),
                resolution=1.0,
            ),
            InstantRecordOption(
                time_step=Duration.from_nanos(2500),
                print_progress=True,
                gpu=True,
            ),
        )
        print("Calculating sound field around focus...")

        df = sound_field.observe_points()
        x = np.unique(df["x[mm]"])
        y = np.unique(df["y[mm]"])

        df = sound_field.next(Duration.from_millis(5))

        times = [float(c.replace("p[Pa]@", "").replace("[ns]", "")) / 1000_000 for c in df.columns]
        p = df.get_columns()

        times = times[700:]
        p = p[700:]

        fig = plt.figure()
        spec = fig.add_gridspec(ncols=2, nrows=1, width_ratios=[10, 1])
        ax = fig.add_subplot(spec[0], projection="3d")
        cax = fig.add_subplot(spec[1])
        colorbar.ColorbarBase(cax, cmap="jet", norm=Normalize(vmin=-10e3, vmax=10e3))

        p_shape = [len(y), len(x)]
        aspect = (len(x), len(y), len(x))
        x, y = np.meshgrid(x, y)

        def anim(i: int):  # noqa: ANN202
            ax.cla()
            z = p[i].to_numpy().reshape(p_shape)
            plot = ax.plot_surface(x, y, z, shade=False, cmap="jet", norm=Normalize(vmin=-10e3, vmax=10e3))  # type: ignore[attr-defined]
            ax.set_zlim(-10e3, 10e3)  # type: ignore[attr-defined]
            ax.set_box_aspect(aspect)  # type: ignore[arg-type]
            ax.set_title(f"t={times[i]:.3f} [ms]")
            return plot

        _ = animation.FuncAnimation(fig, anim, frames=len(p), interval=1, repeat=False, blit=False)
        plt.show()


if __name__ == "__main__":
    plot_focus()
    plot_stm()
