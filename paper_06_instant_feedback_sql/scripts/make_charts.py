#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


@dataclass(frozen=True)
class Quiz:
    quiz_num: int
    assignment_id: str
    title: str


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _quiz_num_from_title(title: str) -> int | None:
    # Expected: "DB Quiz 1" .. "DB Quiz 6"
    if not isinstance(title, str):
        return None
    parts = title.strip().split()
    if len(parts) >= 2 and parts[-2].lower() == "quiz":
        try:
            return int(parts[-1])
        except ValueError:
            return None
    # Fallback: last token int
    try:
        return int(parts[-1])
    except Exception:
        return None


def load_data(csv_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[Quiz]]:
    assignments = pd.read_csv(csv_dir / "assignments.csv")
    attempts = pd.read_csv(csv_dir / "question_submission_attempts.csv")
    survey = pd.read_csv(csv_dir / "assignment_feedback_survey.csv")

    assignments["id"] = assignments["id"].astype(str)
    attempts["assignment_id"] = attempts["assignment_id"].astype(str)
    survey["assignment_id"] = survey["assignment_id"].astype(str)

    # Parse quiz number from title and sort
    quizzes: list[Quiz] = []
    for _, row in assignments.iterrows():
        title = str(row.get("title", ""))
        qn = _quiz_num_from_title(title)
        if qn is None:
            continue
        quizzes.append(Quiz(quiz_num=qn, assignment_id=str(row["id"]), title=title))
    quizzes.sort(key=lambda q: q.quiz_num)

    return assignments, attempts, survey, quizzes


def add_rubric_columns(attempts: pd.DataFrame) -> pd.DataFrame:
    def parse_rubric(val: object) -> dict:
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return {}
        if isinstance(val, dict):
            return val
        try:
            return json.loads(str(val))
        except Exception:
            return {}

    rubric = attempts["rubric"].apply(parse_rubric)
    for key in ["syntax", "semantics", "results"]:
        attempts[key] = rubric.apply(lambda d: d.get(key) if isinstance(d, dict) else np.nan).astype(float)

    attempts["grade"] = pd.to_numeric(attempts["grade"], errors="coerce")
    attempts["attempt"] = pd.to_numeric(attempts["attempt"], errors="coerce").astype("Int64")
    attempts["created_at"] = pd.to_datetime(attempts["created_at"], errors="coerce", utc=True)
    return attempts


def _r2_score(y: np.ndarray, yhat: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    yhat = np.asarray(yhat, dtype=float)
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    if ss_tot == 0:
        return float("nan")
    return 1.0 - ss_res / ss_tot


def plot_avg_grade_rubric(attempts: pd.DataFrame, quizzes: list[Quiz], out_path: Path) -> None:
    colors = {
        "Grade": "#1f77b4",
        "Syntax": "#2ca02c",
        "Semantics": "#ff7f0e",
        "Results": "#17becf",
    }

    fig, axes = plt.subplots(2, 3, figsize=(20.48, 6.48), constrained_layout=True)
    axes = axes.flatten()

    for ax, quiz in zip(axes, quizzes, strict=False):
        df = attempts.loc[attempts["assignment_id"] == quiz.assignment_id].copy()
        df = df.dropna(subset=["attempt"])

        grp = df.groupby("attempt", dropna=True).agg(
            grade=("grade", "mean"),
            syntax=("syntax", "mean"),
            semantics=("semantics", "mean"),
            results=("results", "mean"),
        )
        grp = grp.sort_index()

        x = grp.index.astype(int).to_numpy()

        ax.plot(x, grp["grade"].to_numpy(), marker="o", color=colors["Grade"], label="Grade")
        ax.plot(x, grp["syntax"].to_numpy(), marker="o", color=colors["Syntax"], label="Syntax")
        ax.plot(x, grp["semantics"].to_numpy(), marker="o", color=colors["Semantics"], label="Semantics")
        ax.plot(x, grp["results"].to_numpy(), marker="o", color=colors["Results"], label="Results")

        ax.set_title(f"Quiz {quiz.quiz_num}")
        ax.set_xlabel("Attempt #")
        ax.set_ylabel("Average Grade / Rubric")
        ax.set_ylim(0, 1.0)
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.legend(loc="lower left", fontsize=9)

    # Hide unused axes if any
    for ax in axes[len(quizzes):]:
        ax.axis("off")

    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_students_reaching_attempt(attempts: pd.DataFrame, quizzes: list[Quiz], out_path: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(20.48, 6.48), constrained_layout=True)
    axes = axes.flatten()

    bar_color = "#2f3e9e"  # deep blue 
    lin_color = "#000000"
    exp_color = "#7f7f7f"

    for ax, quiz in zip(axes, quizzes, strict=False):
        df = attempts.loc[attempts["assignment_id"] == quiz.assignment_id, ["student", "attempt"]].copy()
        df = df.dropna(subset=["student", "attempt"])
        df["attempt"] = df["attempt"].astype(int)

        max_attempt = df.groupby("student")["attempt"].max()
        max_n = int(max_attempt.max())
        xs = np.arange(1, max_n + 1)
        ys = np.array([(max_attempt >= n).sum() for n in xs], dtype=float)

        ax.bar(xs, ys, color=bar_color, edgecolor="white")

        # bar labels
        for x, y in zip(xs, ys):
            ax.text(x, y + max(ys) * 0.01, f"{int(y)}", ha="center", va="bottom", fontsize=9)

        # Linear trend
        coeff = np.polyfit(xs, ys, 1)
        y_lin = np.polyval(coeff, xs)
        r2_lin = _r2_score(ys, y_lin)
        ax.plot(xs, y_lin, linestyle="--", color=lin_color, linewidth=2, label=f"Linear trend (R²={r2_lin:.2f})")

        # Exponential trend: y = a * exp(bx)
        # Fit on log(y) (ignore zeros)
        mask = ys > 0
        if mask.sum() >= 2:
            b, loga = np.polyfit(xs[mask], np.log(ys[mask]), 1)
            a = float(np.exp(loga))
            y_exp = a * np.exp(b * xs)
            r2_exp = _r2_score(ys, y_exp)
            ax.plot(xs, y_exp, linestyle=":", color=exp_color, linewidth=2, label=f"Exponential trend (R²={r2_exp:.2f})")

        ax.set_title(f"Quiz {quiz.quiz_num}")
        ax.set_xlabel("Attempt #")
        ax.set_ylabel("Students Reaching Attempt")
        ax.grid(True, axis="y", linestyle=":", alpha=0.35)
        ax.legend(loc="upper right", fontsize=9, frameon=False)

    for ax in axes[len(quizzes):]:
        ax.axis("off")

    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _pearson_r(x: Iterable[float], y: Iterable[float]) -> float:
    x = np.asarray(list(x), dtype=float)
    y = np.asarray(list(y), dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2:
        return float("nan")
    return float(np.corrcoef(x[mask], y[mask])[0, 1])


def plot_survey_ratings(survey: pd.DataFrame, quizzes: list[Quiz], out_path: Path) -> None:
    # Layout: 2 rows of quizzes (1-3, 4-6), each quiz has two stacked plots.
    fig = plt.figure(figsize=(12.8, 9.6), constrained_layout=True)
    gs = fig.add_gridspec(4, 3)

    helped_color = "#2f3e9e"
    understand_color = "#00897b"

    for idx, quiz in enumerate(quizzes):
        col = idx % 3
        row_block = 0 if idx < 3 else 2

        df = survey.loc[survey["assignment_id"] == quiz.assignment_id].copy()
        df["helped_fix"] = pd.to_numeric(df["helped_fix"], errors="coerce")
        df["improved_understanding"] = pd.to_numeric(df["improved_understanding"], errors="coerce")
        df["improvement"] = pd.to_numeric(df["improvement"], errors="coerce")

        # Top: Helped Fix Errors
        ax1 = fig.add_subplot(gs[row_block + 0, col])
        ax2 = fig.add_subplot(gs[row_block + 1, col])

        ax1.set_title(f"Quiz {quiz.quiz_num}")

        for ax, colname, color, subtitle in [
            (ax1, "helped_fix", helped_color, "Helped Fix Errors"),
            (ax2, "improved_understanding", understand_color, "Improved Understanding"),
        ]:
            counts = df[colname].value_counts(dropna=True).reindex([1, 2, 3, 4, 5], fill_value=0)
            total = int(counts.sum())
            xs = np.array([1, 2, 3, 4, 5])
            ys = counts.to_numpy(dtype=float)

            ax.bar(xs, ys, color=color)
            ax.set_xticks(xs)
            ax.set_xlabel("Rating")
            ax.set_ylabel("# Responses")
            ax.set_title(subtitle, fontsize=11)

            # Percent labels
            for x, y in zip(xs, ys):
                pct = 0 if total == 0 else int(round((y / total) * 100))
                ax.text(x, y + max(ys) * 0.02 + 0.2, f"{pct}%", ha="center", va="bottom", fontsize=9)

            # Pearson r with improvement
            r = _pearson_r(df[colname], df["improvement"])
            ax.text(
                0.02,
                0.92,
                f"Pearson r = {r:.2f}",
                transform=ax.transAxes,
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="0.7", alpha=0.9),
            )

            ax.grid(True, axis="y", linestyle=":", alpha=0.3)

    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_time_gap_vs_improvement(attempts: pd.DataFrame, out_path: Path) -> None:
    df = attempts[["question_submission_id", "created_at", "grade"]].copy()
    df = df.dropna(subset=["question_submission_id", "created_at", "grade"])

    gaps_hours: list[float] = []
    deltas: list[float] = []

    for _, g in df.groupby("question_submission_id", sort=False):
        g = g.sort_values("created_at")
        # `created_at` is timezone-aware (UTC). Converting to int64 nanoseconds
        # avoids pandas/numpy object-dtype arrays.
        t_ns = g["created_at"].astype("int64").to_numpy(dtype=np.int64)
        y = g["grade"].to_numpy(dtype=float)
        if len(y) < 2:
            continue
        dt = (t_ns[1:] - t_ns[:-1]) / (3600.0 * 1e9)
        dy = y[1:] - y[:-1]

        # Keep finite
        mask = np.isfinite(dt) & np.isfinite(dy)
        gaps_hours.extend(dt[mask].tolist())
        deltas.extend(dy[mask].tolist())

    x = np.asarray(gaps_hours, dtype=float)
    y = np.asarray(deltas, dtype=float)

    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]

    # Stats 
    rho = float(spearmanr(x, y, nan_policy="omit").correlation)
    avg_gap_min = float(np.mean(x) * 60.0) if len(x) else float("nan")

    # Plot
    fig, ax = plt.subplots(1, 1, figsize=(10.8, 7.6), constrained_layout=True)

    pos = y >= 0
    ax.scatter(x[pos], y[pos], s=70, c="#2e7d32", alpha=0.8, edgecolors="white", linewidths=0.5)
    ax.scatter(x[~pos], y[~pos], s=70, c="#d32f2f", alpha=0.8, edgecolors="white", linewidths=0.5)

    # Horizontal zero line
    ax.axhline(0, color="0.6", linestyle="--", linewidth=1.5)

    # Trend line
    if len(x) >= 2:
        m, b = np.polyfit(x, y, 1)
        xs = np.linspace(0, max(60, float(np.nanmax(x))), 200)
        ax.plot(xs, m * xs + b, color="0.2", linestyle="-.", linewidth=2.5, label="Trend")
        ax.legend(loc="upper right", frameon=False, fontsize=20)

    ax.set_xlabel("Time Gap Between Attempts (hours)", fontsize=24)
    ax.set_ylabel("Grade Improvement (Δ)", fontsize=24)
    ax.tick_params(axis="both", labelsize=18)

    ax.set_xlim(0, 60)
    ax.set_ylim(-1.1, 1.05)
    ax.grid(True, linestyle=":", alpha=0.35)

    ax.text(
        0.70,
        0.08,
        f"Spearman ρ = {rho:.2f}\nAvg gap = {avg_gap_min:.1f} min",
        transform=ax.transAxes,
        fontsize=18,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="0.7", alpha=0.95),
    )

    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    script_dir = Path(__file__).resolve().parent
    cwd = Path.cwd()

    def _default_csv_dir() -> Path:
        required = {
            "assignments.csv",
            "question_submission_attempts.csv",
            "assignment_feedback_survey.csv",
        }
        candidates = [cwd, script_dir, script_dir / "socoles-csv"]
        for c in candidates:
            if all((c / name).exists() for name in required):
                return c
        # Most common expectation: user runs from folder containing the CSVs
        return cwd

    parser.add_argument("--csv-dir", type=Path, default=_default_csv_dir())
    parser.add_argument("--out-dir", type=Path, default=cwd)
    args = parser.parse_args()

    csv_dir: Path = args.csv_dir
    out_dir: Path = args.out_dir
    _ensure_dir(out_dir)

    _, attempts, survey, quizzes = load_data(csv_dir)
    attempts = add_rubric_columns(attempts)

    # Convert titles "DB Quiz N" -> "Quiz N" in plot labels
    quizzes = [Quiz(q.quiz_num, q.assignment_id, q.title.replace("DB ", "")) for q in quizzes]

    plot_avg_grade_rubric(attempts, quizzes, out_dir / "01_avg_grade_rubric.png")
    plot_students_reaching_attempt(attempts, quizzes, out_dir / "02_students_reaching_attempt.png")
    plot_survey_ratings(survey, quizzes, out_dir / "03_survey_ratings.png")
    plot_time_gap_vs_improvement(attempts, out_dir / "04_time_gap_vs_improvement.png")

    print("Wrote figures to:", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
