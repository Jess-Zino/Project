import re

def clean_latex(latex_str: str) -> str:
    # Custom replacements
    latex_str = latex_str.replace("^ { 0 } / 。", "%")
    latex_str = latex_str.replace("^ { 0 } / _ { 0 }", "%")
    latex_str = latex_str.replace("。", ".")
    latex_str = re.sub(
        r"(?<=\d)\s+(?=[a-zA-Z])", " ", latex_str
    ) 
    # Normalize whitespace
    latex_str = re.sub(r"\s+", " ", latex_str).strip()

    # Clean up \operatorname
    latex_str = re.sub(
        r"\\operatorname\*?\s*\{\s*([a-zA-Z\s]+?)\s*\}",
        lambda m: "\\operatorname*{" + m.group(1).replace(" ", "") + "}",
        latex_str,
    )
    latex_str = re.sub(
        r"\\operatorname\*?\s*\{\s*([a-zA-Z]+)\s*\}",
        lambda m: "\\" + m.group(1),
        latex_str,
    )
    latex_str = re.sub(
            r"\\(mathfrak|mathbf|mathit|mathrm|mathsf|mathtt|bf|textbf|rm|it|sf|sc|qquad|quad)\s*\{\s*([^{}]+?)\s*\}",
            r"\2",
            latex_str,
        )
    latex_str = re.sub(
            r"\{\s*\\(mathfrak|mathbf|mathit|mathrm|mathsf|mathtt|bf|textbf|rm|it|sf|sc)\s+([^{}]+?)\s*\}",
            r"\2",
            latex_str,
        )
    latex_str = re.sub(
        r"\\(mathfrak|mathbf|mathit|mathrm|mathsf|mathtt|bf|textbf|rm|it|sf|sc)\s+",
        "",
        latex_str,
    )

    # Fix exponent and subscript spacing
    latex_str = re.sub(r"([a-zA-Z0-9])([\^_])", r"\1\2", latex_str)

    # Fix decimals
    latex_str = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", latex_str)
    latex_str = re.sub(r"(?<!\d)\.\s*(\d+)", r".\1", latex_str)

    # Convert fractions like 5/4 into \frac{5}{4}
    # Ensures it's not already inside a \frac
    latex_str = re.sub(
        r"(?<!\\frac\{)(?<![a-zA-Z0-9])(\d+)\s*/\s*(\d+)(?!\})",
        r"\\frac{\1}{\2}",
        latex_str,
    )
    return latex_str


