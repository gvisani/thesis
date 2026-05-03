#!/usr/bin/env python3
"""Replace Unicode characters that pdflatex can't handle in .bib files."""

import sys
import glob

REPLACEMENTS = {
    "⋅": r"$\cdot$",       # ⋅ dot operator
    "×": r"$\times$",      # × multiplication sign
    "−": r"$-$",           # − minus sign
    "≥": r"$\geq$",        # ≥
    "≤": r"$\leq$",        # ≤
    "≠": r"$\neq$",        # ≠
    "∞": r"$\infty$",      # ∞
    "α": r"$\alpha$",      # α
    "β": r"$\beta$",       # β
    "γ": r"$\gamma$",      # γ
    "δ": r"$\delta$",      # δ
    "σ": r"$\sigma$",      # σ
    "μ": r"$\mu$",         # μ
    "π": r"$\pi$",         # π
    "→": r"$\to$",         # →
    "←": r"$\leftarrow$",  # ←
}

def fix_file(path):
    with open(path, encoding="utf-8") as f:
        original = f.read()

    fixed = original
    changes = []
    for char, latex in REPLACEMENTS.items():
        if char in fixed:
            count = fixed.count(char)
            fixed = fixed.replace(char, latex)
            changes.append((char, latex, count))

    if changes:
        with open(path, "w", encoding="utf-8") as f:
            f.write(fixed)
        for char, latex, count in changes:
            print(f"{path}: replaced {count}x U+{ord(char):04X} '{char}' → {latex}")
    else:
        print(f"{path}: nothing to fix")

if __name__ == "__main__":
    paths = sys.argv[1:] if len(sys.argv) > 1 else sorted(glob.glob("*.bib"))
    if not paths:
        print("No .bib files found.")
        sys.exit(1)
    for p in paths:
        fix_file(p)
