# -*- coding: utf-8 -*-
import re

SUB = str.maketrans("0123456789+-=()aeoxhklmnpst", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜ")
SUP = str.maketrans("0123456789+-=()ni", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ")
GREEK = {
    r"\theta": "θ", r"\Theta": "Θ", r"\lambda": "λ", r"\Lambda": "Λ",
    r"\sigma": "σ", r"\Sigma": "Σ", r"\pi": "π", r"\mu": "μ",
    r"\alpha": "α", r"\beta": "β", r"\approx": "≈", r"\le": "≤", r"\ge": "≥",
    r"\leq": "≤", r"\geq": "≥", r"\pm": "±", r"\times": "×", r"\cdot": "·",
}

def sub_token(tok: str) -> str:
    special = {
        "0": "₀", "1": "₁", "2": "₂", "x": "ₓ", "y": "ᵧ", "R": "ᵣ", "r": "ᵣ",
        "eff": "ₑff", "vis": "ᵥᵢₛ", "xy": "ₓᵧ", "in": "ᵢₙ",
        "0x": "₀ₓ", "0y": "₀ᵧ", "sigma": "σ",
    }
    tok = tok.strip()
    m = re.match(r"mathrm\{([^}]+)\}", tok)
    if m:
        return sub_token(m.group(1))
    if tok in special:
        return special[tok]
    return "".join(ch.translate(SUB) if ch.isalnum() else ch for ch in tok)

def convert_latex_math(expr: str) -> str:
    s = expr.strip()
    while True:
        m = re.search(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", s)
        if not m:
            break
        s = s[:m.start()] + f"({convert_latex_math(m.group(1))})/({convert_latex_math(m.group(2))})" + s[m.end():]
    while True:
        m = re.search(r"\\sqrt\{([^{}]+)\}", s)
        if not m:
            break
        s = s[:m.start()] + f"√({convert_latex_math(m.group(1))})" + s[m.end():]
    for k in sorted(GREEK.keys(), key=len, reverse=True):
        s = s.replace(k, GREEK[k])
    s = re.sub(r"\\mathrm\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\text\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\^\{([^{}]+)\}|\^(\w)", lambda m: "".join(ch.translate(SUP) for ch in (m.group(1) or m.group(2))), s)
    s = re.sub(r"_\{([^{}]+)\}", lambda m: sub_token(m.group(1)), s)
    s = re.sub(r"_(\\?[A-Za-z0-9]+)", lambda m: sub_token(m.group(1).lstrip("\\")), s)
    s = re.sub(r"\\([a-zA-Z]+)", r"\1", s)
    s = s.replace(r"\,", " ").replace(r"\;", " ").replace("~", " ")
    s = re.sub(r"(\d)\{,\}(\d)", r"\1,\2", s)
    return re.sub(r"\s+", " ", s).strip()

def convert_document(text: str) -> str:
    text = re.sub(r"\$\$(.+?)\$\$", lambda m: convert_latex_math(m.group(1)), text, flags=re.S)
    text = re.sub(r"\\\[(.+?)\\\]", lambda m: convert_latex_math(m.group(1)), text, flags=re.S)
    text = re.sub(r"\\\((.+?)\\\)", lambda m: convert_latex_math(m.group(1)), text, flags=re.S)
    text = re.sub(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", lambda m: convert_latex_math(m.group(1)), text, flags=re.S)
    for a, b in [
        (r"\bw0xy\b", "w₀ₓᵧ"), (r"\bzRxy\b", "zᵣₓᵧ"), (r"\bw0\b", "w₀"), (r"\bz0\b", "z₀"),
        (r"\bzR\b", "zᵣ"), (r"\bz_R\b", "zᵣ"), (r"\bw_0\b", "w₀"), (r"\bz_0\b", "z₀"),
        (r"\bM\^2\b", "M²"), (r"\bM2\b", "M²"), (r"\b1/e\^2\b", "1/e²"),
        (r"\bD4sigma\b", "D4σ"), (r"\bd_sigma\b", "dσ"), (r"\bsigma\^2\b", "σ²"),
        (r">=", "≥"), (r"<=", "≤"),
    ]:
        text = re.sub(a, b, text)
    text = text.replace("z_R", "zᵣ").replace("w_0", "w₀").replace("z_0", "z₀")
    text = text.replace("M^2", "M²").replace("1/e^2", "1/e²").replace("D4sigma", "D4σ")
    return text
