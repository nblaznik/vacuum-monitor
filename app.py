import pandas as pd
import matplotlib.pyplot as plt
import time
import os

# Define time windows
TIME_WINDOWS = {
    "minute": pd.Timedelta(minutes=1),
    "hour": pd.Timedelta(hours=1),
    "5_hour": pd.Timedelta(hours=5),
    "day": pd.Timedelta(days=1),
    "week": pd.Timedelta(weeks=1),
    "month": pd.Timedelta(weeks=4),
    "all": pd.Timedelta.max,
}


NOMINAL_VALUES = [
1e-11,
1.5e-2,
9e-3,
4e-7,
5e-9,
1e-9
]

plt.close('all')  # Close any existing plots
from matplotlib.ticker import FormatStrFormatter

def plot_window(df, window_name, delta):
    now = pd.Timestamp.now()
    start_time = now - delta
    df_window = df[df["Timestamp"] >= start_time]

    if df_window.empty:
        print(f"[{window_name}] No data to plot.")
        return

    fig, axs = plt.subplots(6, 1, figsize=(10, 6), sharex=True, facecolor='white')

    for ch in range(1, 7):
        ax = axs[ch - 1]
        ch_data = df_window[df_window["Channel"] == ch]

        if ch_data.empty:
            ax.set_visible(False)
            continue

        # Apply Ch. 5 correction
        if ch == 5:
            pressure = ch_data["Pressure"].apply(lambda p: p * 1e-5 if p == 5e-4 else p)
        else:
            pressure = ch_data["Pressure"]

        ax.plot(ch_data["Timestamp"], pressure)
        ax.set_ylabel(f"Ch. {ch}")
        ax.tick_params(axis='y', labelsize=8)

        # Get min/max, ensure log safety
        pressure = pressure[pressure > 0]
        if pressure.empty:
            ax.set_visible(False)
            continue
        ymin, ymax = pressure.min(), pressure.max()
        if ymin == ymax:
            ymin *= 0.5
            ymax *= 2

        # ax.set_yscale("log")

        # ax.set_ylim(ymin, ymax)
        ax.set_yticks([ymin, ymax])
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1e'))

    for ax in axs:
        ax.set_xlabel("Time")

    axs[0].set_title(f"Pressure — Last {window_name.capitalize()}")
    fig.autofmt_xdate()
    plt.tight_layout()
    filename = f"PLOTS/plot_{window_name}.png"
    plt.savefig(filename, transparent=True, dpi=150)
    plt.close(fig)
    print(f"[{window_name}] Saved {filename}")


def update_vals(df):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.axis("off")  # Hide axes

    # Get latest pressure per channel
    latest = df.sort_values("Timestamp").groupby("Channel").tail(1)

    y_pos = 1.0
    spacing = 0.2

    for ch in range(1, 7):
        row = latest[latest["Channel"] == ch]
        if not row.empty:

            val = row["Pressure"].values[0]
            
            if ch == 5:
                if val == 4.996e-4:
                    val = 5e-9
            if val / NOMINAL_VALUES[ch - 1] > 2:
                txt = f"Ch. {ch}: {val:.2e} (!)"
                color = "#ebbe5d" 
            elif val / NOMINAL_VALUES[ch - 1] > 5:
                txt = f"Ch. {ch}: {val:.2e} (!!)"
                color = "#ff6f61"  
            else:
                color = "#45772D"  
                txt = f"Ch. {ch}: {val:.2e}"
        else:
            txt = f"Ch. {ch}: ---"
        ax.text(0, y_pos, txt, fontsize=28, fontfamily="monospace", color=color, transform=ax.transAxes)
        y_pos -= spacing

    plt.tight_layout()
    plt.savefig("PLOTS/plot_vals.png", dpi=150,  transparent=True)
    plt.close(fig)
    print("[vals] Saved PLOTS/plot_vals.png")



def plot_individual_channel(df, window_name, delta, channel):
    now = pd.Timestamp.now()
    start_time = now - delta
    df_window = df[(df["Timestamp"] >= start_time) & (df["Channel"] == channel)]

    if df_window.empty:
        print(f"[{window_name}] Channel {channel}: No data to plot.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    pressure = df_window["Pressure"].copy()

    # Special scaling for channel 5
    if channel == 5:
        pressure = pressure.apply(lambda p: p * 1e-5 if p > 1e-6 else p)

    ax.plot(df_window["Timestamp"], pressure)
    ax.set_yscale("log")
    ax.set_xlabel("Time")
    ax.set_ylabel("Pressure")
    ax.set_title(f"Channel {channel} — Last {window_name.capitalize()}")

    fig.autofmt_xdate()
    plt.tight_layout()

    filename = f"PLOTS/plot_ch{channel}_{window_name}.png"
    plt.savefig(filename, transparent=True)
    plt.close(fig)
    print(f"[{window_name}] Saved {filename}")


def update_all_plots():
    # try:
    df = pd.read_csv("pressure_readings.csv", names=["Timestamp", "Channel", "Pressure"], skiprows=1)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df["Channel"] = pd.to_numeric(df["Channel"], errors="coerce")
    df["Pressure"] = pd.to_numeric(df["Pressure"], errors="coerce")
    df = df.dropna()

    for name, delta in TIME_WINDOWS.items():
        plot_window(df, name, delta)
        plt.close('all')


    for name, delta in TIME_WINDOWS.items():
        for ch in range(1, 7):
            plot_individual_channel(df, name, delta, ch)


    update_vals(df)
    # except Exception as e:
    #     print("Plot update failed:", e)



if __name__ == "__main__":
    while True:
        update_all_plots()
        time.sleep(5)
