import re
def preprocess_latex(latex_str):
    """Cleans and standardizes LaTeX expressions before conversion."""
    latex_str = latex_str.replace("^ { 0 } / 。", "%")
    latex_str = latex_str.replace("^ { 0 } / _ { 0 }", "%")

    latex_str = latex_str.replace("。", ".")
    # Basic cleanup (removes excessive spaces and strips any unwanted extra spaces)
    latex_str = re.sub(r"\s+", " ", latex_str).strip()

    # Remove spaces inside \operatorname and \operatorname* to avoid parsing issues
    latex_str = re.sub(
        r"\\operatorname\*?\s*\{\s*([a-zA-Z\s]+?)\s*\}",
        lambda m: "\\operatorname*{" + m.group(1).replace(" ", "") + "}",
        latex_str,
    )

    # Handle \underset { x \to 0 } { \lim }
    latex_str = re.sub(
        r"\\underset\s*\{\s*([^{}]+?)\s*\}\s*\{\s*(\\lim)\s*\}",
        r"\\lim_{\1}",  # Replace with \lim_{x \to 0}
        latex_str,
    )

    # Handle \underset { x \to 0 } { \operatorname* { l i m } }
    latex_str = re.sub(
        r"\\underset\s*\{\s*([^{}]+?)\s*\}\s*{\\operatorname\*\{\s*([^{}]+?)\s*\}}",
        r"\\lim_{\1}",  # Replace with \lim_{x \to 0}
        latex_str,
    )

    # Handle \operatorname* and \operatorname and remove spaces inside operators
    latex_str = re.sub(
        r"\\operatorname\*?\s*\{\s*([a-zA-Z]+)\s*\}",
        lambda m: "\\" + m.group(1),  # Converts \operatorname{cos} -> \cos
        latex_str,
    )
    latex_str = re.sub(
        r"(\d+)\s*\\frac\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}",
        r"\1 \\mixedfrac-b \2 \\frac-separator \3 \\mixedfrac-e",
        latex_str,
    )
    latex_str = re.sub(
        r"(\d+)\s*\\frac\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}",
        r"\1 \\mixedfrac-b \2 \\frac-separator \3 \\mixedfrac-e",
        latex_str,
    )
    latex_str = re.sub(
        r"(\d+)\s*\\vec\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}",
        r"\1 \\mixedfrac-b \2 \\frac-separator \3 \\mixedfrac-e",
        latex_str,
    )
    # Format fractions like \frac{a}{b} (handling LaTeX math fractions)
    latex_str = re.sub(
        r"\\frac\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}",
        r"\\frac-b \1 \\frac-separator \2 \\frac-e",  # Formatting fractions
        latex_str,
    )

    # Handle mixed fractions (whole number with fraction)

    latex_str = re.sub(r"\smallsetminus", r"\therefore", latex_str)

    # Handle simple array environments like \begin{array}{cc} { -1 } & {} \\ \end{array}
    latex_str = latex_str.replace(
        r"\begin{array} { c c } { - 1 } & { } \\ \end{array}", "-1"
    )

    # Remove \operatorname{...} but keep the inner content without spaces
    latex_str = re.sub(
        r"\\operatorname\s*\{\s*([\w\s]+?)\s*\}",
        lambda m: "\\" + m.group(1).replace(" ", " "),
        latex_str,
    )

    # STRIP ALL MATH FORMATTING
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

    # Wrap superscripts with tags: handle ^{...}
    latex_str = re.sub(
        r"\^\s*\{\s*([^{}]+?)\s*\}", r"\\superscript-b \1 \\superscript-e", latex_str
    )

    # Wrap superscripts with tags: handle ^x (no braces)
    latex_str = re.sub(
        r"\^([a-zA-Z0-9])", r"\\superscript-b \1 \\superscript-e", latex_str
    )
    latex_str = re.sub(r"\\qquad", r" ", latex_str)
    # Handle subscripts like _{...}
    latex_str = re.sub(
        r"\_\s*\{\s*([^{}]+?)\s*\}", r"\\subscript-b \1 \\subscript-e", latex_str
    )

    # Handle \sqrt[...]{...}, separating the index and base
    latex_str = re.sub(
        r"\\sqrt\s*\[(.*?)\]\s*\{(.*?)\}",
        r"\\sqrtib \1 \\sqrtie \\sqrt-b  \2 \\sqrt-e",
        latex_str,
    )

    # Handle \sqrt{...} (no index)
    latex_str = re.sub(r"\\sqrt\s*\{(.*?)\}", r"\\sqrt-b  \1 \\sqrt-e", latex_str)
    latex_str = latex_str.replace(r"\begin{array}{cc} {", "")
    latex_str = latex_str.replace(r"\begin{array} { c c } {", "")

    latex_str = latex_str.replace(r"\begin{array}{cc}", "")
    latex_str = latex_str.replace(r"\begin{array} { c c }", "")
    latex_str = latex_str.replace(r"\begin{array}{cc}{", "")
    latex_str = latex_str.replace(r"\begin{array} { c c }{", "")
    # Remove the literal \end{array}
    latex_str = latex_str.replace(r"} \\ \end{array}", "")
    # Remove the literal \end{array}
    latex_str = latex_str.replace(r"\end{array}", "")

    # Fix decimals
    latex_str = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", latex_str)
    latex_str = re.sub(r"(?<!\d)\.\s*(\d+)", r".\1", latex_str)

    # Merge digit groups like 1 234 -> 1234
    latex_str = re.sub(
        r"(?:\d(?: \d)+)", lambda m: m.group(0).replace(" ", ""), latex_str
    )
    # Merge digit groups like 1 234 -> 1234
    latex_str = re.sub(r"\s+", " ", latex_str).strip()

    latex_str = re.sub(r"~+", " ~ ", latex_str)

    # Remove unwanted space between digits and next character
    latex_str = re.sub(
        r"(?<=\d)\s+(?=[a-zA-Z])", " ", latex_str
    )  # only allow digit-letter merging

    # Remove \superscript-e only if it comes after \int and \superscript-b
    # Remove \subscript-e when it's directly after an \int ... \subscript-b ...
    latex_str = re.sub(
        r"(\\int(?:\\[a-z]+)*\s+\\subscript-b\s+[^\s]+)\s+\\subscript-e",
        r"\1",
        latex_str,
    )
    latex_str = re.sub(
        r"(\\int(?:\\subscript-b\s*\S+)\s*)\\subscript-e", r"\1", latex_str
    )

    return latex_str

