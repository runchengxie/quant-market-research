"""Fixed expanding-year OLS comparisons with paired time-block uncertainty."""
import numpy as np
import pandas as pd

DOMESTIC = ["own_lag", "own_mom5", "own_vol20", "csi_lag", "csi_mom5",
            "cnh", "jpy", "eur"]
MODELS = {"domestic_fx": DOMESTIC, "global": DOMESTIC + ["spx"],
          "all_overseas": DOMESTIC + ["spx", "hsi", "n225", "ks11"]}


def purged_train(frame, first_decision):
    return frame[(frame.date < first_decision.tz_convert("Asia/Shanghai").tz_localize(None).normalize())
                 & (frame.label_end_utc < first_decision)]


def predict(train, test, columns):
    # Every transform is estimated on this fold's training rows only.
    center = train[columns].mean()
    scale = train[columns].std(ddof=0).replace(0, 1)
    x = np.column_stack([np.ones(len(train)), ((train[columns] - center) / scale)])
    z = np.column_stack([np.ones(len(test)), ((test[columns] - center) / scale)])
    return z @ np.linalg.lstsq(x, train.y.to_numpy(), rcond=None)[0]


def walk_forward(frame, start_year=2020):
    clean = frame.dropna(subset=MODELS["all_overseas"] + ["y", "label_end_utc"]).copy()
    forecasts, folds = [], []
    for year in range(start_year, int(clean.date.dt.year.max()) + 1):
        test = clean[clean.date.dt.year == year].copy()
        if test.empty:
            continue
        train = purged_train(clean, test.decision_utc.iloc[0])
        if len(train) < 252:
            continue
        for name, columns in MODELS.items():
            test[name] = predict(train, test, columns)
        test["train_mean"] = float(train.y.mean())
        test["fold"] = year
        forecasts.append(test)
        folds.append({"year": year, "train_n": len(train), "test_n": len(test),
                      "train_end": str(train.date.max().date()),
                      "last_training_label_utc": str(train.label_end_utc.max()),
                      "test_first_decision_utc": str(test.decision_utc.iloc[0])})
    if not forecasts:
        raise ValueError("No folds with 252 training rows")
    return pd.concat(forecasts, ignore_index=True), folds


def paired_summary(frame, baseline="global", augmented="all_overseas", bootstrap=1000):
    y = frame.y.to_numpy()
    base_loss = (y - frame[baseline].to_numpy()) ** 2
    aug_loss = (y - frame[augmented].to_numpy()) ** 2
    hit_base = np.sign(y) == np.sign(frame[baseline].to_numpy())
    hit_aug = np.sign(y) == np.sign(frame[augmented].to_numpy())
    rng = np.random.default_rng(20261018)
    n, block = len(frame), 10
    draws = (rng.integers(0, n, (bootstrap, int(np.ceil(n / block)), 1))
             + np.arange(block)).reshape(bootstrap, -1)[:, :n] % n
    gains = 1 - aug_loss[draws].mean(axis=1) / base_loss[draws].mean(axis=1)
    return {"n": n, "first": str(frame.date.min().date()),
            "last": str(frame.date.max().date()), "baseline": baseline, "augmented": augmented,
            "baseline_hit": float(hit_base.mean()), "augmented_hit": float(hit_aug.mean()),
            "mse_gain": float(1 - aug_loss.mean() / base_loss.mean()),
            "mse_gain_ci95": np.quantile(gains, [.025, .975]).tolist(),
            "baseline_rmse_bp": float(np.sqrt(base_loss.mean()) * 1e4),
            "augmented_rmse_bp": float(np.sqrt(aug_loss.mean()) * 1e4)}
