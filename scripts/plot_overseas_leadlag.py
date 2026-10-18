"""Optional Matplotlib plotter for the reviewed aggregate cost snapshot."""
import argparse
import json
from pathlib import Path


def main():
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), sharey=False, layout="constrained")
    for ax, target in zip(axes, ["510300", "512480"]):
        for model, title, color in [("global", "Domestic + FX + SPX", "#2563eb"),
                                    ("all_overseas", "+ HSI / N225 / KS11", "#c2410c"),
                                    ("always_long", "Always long", "#64748b")]:
            rows = sorted([r for r in data["costs"] if r["target"] == target
                           and r["model"] == model and r["lag_sessions"] == 0
                           and r["scenario"] == "flat_bps"], key=lambda r: r["round_trip_bp"])
            ax.plot([r["round_trip_bp"] for r in rows],
                    [r["mean_daily_net_bp"] for r in rows], marker="o", label=title, color=color)
        ax.axhline(0, color="#94a3b8", linewidth=.8)
        ax.set_title(f"{target} ETF | next tradable open")
        ax.set_xlabel("Assumed round-trip cost (bp)")
        ax.set_ylabel("Mean net return / interval (bp)")
        ax.grid(alpha=.2)
    axes[0].legend(fontsize=8)
    fig.suptitle("Retrospective T+1-compatible daily-bar proxy; not verified fills", fontsize=11)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Keep text searchable and the export accessible.
    plt.rcParams["svg.fonttype"] = "none"
    fig.savefig(args.output, metadata={"Date": None})
    # Matplotlib emits trailing spaces in multiline path attributes.
    if args.output.suffix.lower() == ".svg":
        args.output.write_text("\n".join(line.rstrip() for line in args.output.read_text().splitlines())
                               + "\n")


if __name__ == "__main__":
    main()
