import random
import csv
import string
import re
import json
from fractions import Fraction
# === LATEX EXPRESSION GENERATORS ===

def random_int():
    return random.randint(-99, 99)
def generate_digit():
    return f"{random.randint(0, 10)}"
def generate_double_digit():
    return  f"{random.randint(10, 99)}"
def generate_three_digits():
    return  f"{random.randint(100, 999)}"

def random_var():
    return random.choice(string.ascii_letters)

def generate_addition():
    return f"{random_int()} + {random_int()}"

def generate_subtraction():
    return f"{random_int()} - {random_int()}"

def generate_multiplication():
    return f"{random_int()} \\times {random_int()}"

def generate_division():
    b = random.randint(1, 99)
    a = b * random.randint(-99, 99)
    return f"{a} \\div {b}"

def generate_variable_expression():
    return f"{random_var()} + {random_int()} = {random_int()}"

def generate_quadratic():
    a, b, c = [random.randint(-100, 100) for _ in range(3)]
    x = random_var()
    return f"{a}{x}^2 + {b}{x} + {c} "

def generate_cubic():
    a, b, c, d = [random.randint(-100, 100) for _ in range(4)]
    x = random_var()
    return f"{a}{x}^3 + {b}{x}^2 + {c}{x} + {d}"

def generate_fraction():
    return f"\\frac{{{random_int()}}}{{{random.randint(1, 99)}}}"

def generate_mixed_fraction():
    whole = random_int()
    numerator = random.randint(1, 9)
    denominator = random.randint(numerator + 1, 12)  # ensure it's a proper fraction
    return f"{whole}\\frac{{{numerator}}}{{{denominator}}}"

def generate_variable_fraction():
    var = random_var()
    return f"\\frac{{{var}}}{{{random.randint(1, 99)}}}"

def generate_linear_fraction():
    a, b, c, d = [random_int() for _ in range(4)]
    var = random_variable()
    numerator = f"{a}{var} {'+' if b >= 0 else '-'} {abs(b)}"
    denominator = f"{c}{var} {'+' if d >= 0 else '-'} {abs(d)}"
    return f"\\frac{{{numerator}}}{{{denominator}}}"

def generate_quadratic_fraction():
    a, b, c, d, e = [random_int() for _ in range(5)]
    var = random_variable()
    numerator = f"{a}{var}^2 {'+' if b >= 0 else '-'} {abs(b)}{var} {'+' if c >= 0 else '-'} {abs(c)}"
    denominator = f"{d}{var} {'+' if e >= 0 else '-'} {abs(e)}"
    return f"\\frac{{{numerator}}}{{{denominator}}}"


def generate_cubic_fraction():
    a, b, c, d, e, f = [random_int() for _ in range(6)]
    var = random_var()
    numerator = f"{a}{var}^3 {'+' if b >= 0 else '-'} {abs(b)}{var}^2 {'+' if c >= 0 else '-'} {abs(c)}{var} {'+' if d >= 0 else '-'} {abs(d)}"
    denominator = f"{e}{var}^2 {'+' if f >= 0 else '-'} {abs(f)}"
    return f"\\frac{{{numerator}}}{{{denominator}}}"
def generate_bracketed_fraction():
    var1 = random_var()
    var2 = random_var()
    while var2 == var1:
        var2 = random_var()

    a, b = random_int(), random_int()
    exponent = random.choice([1, 2, 3])
    bracket_expr = f"({a}{var1} {'+' if b >= 0 else '-'} {abs(b)}{var2})^{exponent}"

    # Randomly choose if it goes in numerator or denominator
    if random.choice([True, False]):
        numerator = bracket_expr
        denominator = str(random.randint(1, 9))
    else:
        numerator = str(random.randint(1, 9))
        denominator = bracket_expr

    return f"\\frac{{{numerator}}}{{{denominator}}}"

def generate_polynomial_fraction():
    coeffs = [random_int() for _ in range(5)]  # a, b, c, d, e
    var = random_var()
    numerator_terms = []
    powers = [4, 3, 2, 1, 0]
    for coeff, power in zip(coeffs, powers):
        if coeff == 0:
            continue
        if power == 0:
            term = f"{abs(coeff)}"
        elif power == 1:
            term = f"{abs(coeff)}{var}"
        else:
            term = f"{abs(coeff)}{var}^{power}"
        sign = '+' if coeff > 0 else '-'
        numerator_terms.append(f"{sign} {term}")
    numerator = ' '.join(numerator_terms).lstrip('+ ').strip()

    a, b = random_int(), random_int()
    denominator = f"{a}{var} {'+' if b >= 0 else '-'} {abs(b)}"
    return f"\\frac{{{numerator}}}{{{denominator}}}"

def generate_inequality():
    ops = ["<", ">", "\\leq", "\\geq"]
    return f"{random_int()} {random.choice(ops)} {random_int()}"

def generate_variable_inequality():
    ops = ["<", ">", "\\leq", "\\geq"]
    x = random_var()
    a, b = random.randint(1, 10), random_int()
    return f"{a}{x} + {b} {random.choice(ops)} {random_int()}"

def generate_compound_inequality():
    x = random_var()
    mid = random.randint(-10, 10)
    left = random.randint(mid - 10, mid - 1)
    right = random.randint(mid + 1, mid + 10)
    return random.choice([
        f"{left} < {x} < {right}",
        f"{left} \\leq {x} < {right}",
        f"{left} < {x} \\leq {right}",
        f"{left} \\leq {x} \\leq {right}"
    ])
def generate_fraction_inequality():
    ops = ["<", ">", "\\leq", "\\geq"]
    num = f"{random_var()} + {random.randint(1, 9)}"
    denom = random.randint(2, 10)
    rhs = random.randint(1, 20)
    return f"\\frac{{{num}}}{{{denom}}} {random.choice(ops)} {rhs}"


def generate_absolute_inequality():
    ops = ["<", ">", "\\leq", "\\geq"]
    expr = f"{random_var()} - {random.randint(1, 10)}"
    return f"|{expr}| {random.choice(ops)} {random.randint(1, 10)}"

def generate_power_inequality():
    ops = ["<", ">", "\\leq", "\\geq"]
    base = random_var()
    exponent = random.randint(2, 3)
    return f"{base}^{exponent} {random.choice(ops)} {random.randint(1, 50)}"



def generate_trig():
    funcs = ["\\sin", "\\cos", "\\tan", "\\arctan", "\\arccos", "\\arcsin", "\\cosh","\\sinh", "\\tanh"]
    angle = random.randint(0, 360)
    return f"{random.choice(funcs)}({angle}^{{\\circ}})"
def generate_power():
    base = random_int()
    exponent = random.randint(0, 1000)
    return f"{base}^{{{exponent}}}"

def generate_root():
    radicand = random.randint(1, 100)
    return f"\\sqrt{{{radicand}}}"

def generate_nth_root():
    degree = random.randint(2, 5)
    radicand = random.randint(1, 100)
    return f"\\sqrt[{degree}]{{{radicand}}}"

def generate_logarithm():
    base = random.choice([2, 10, 'e', 'a'])
    arg = random.randint(1, 100)
    if base == 'e':
        return f"\\ln({arg})"
    return f"\\log_{{{base}}}({arg})"

def generate_exponential():
    base = random.choice(['e', 2, 10])
    exponent = random.randint(1, 5)
    return f"{base}^{{{exponent}}}"

def generate_absolute_value():
    value = random_int()
    return f"|{value}|"

def generate_modulus():
    a = random_int()
    b = random.randint(1, 10)
    return f"{a} \\bmod {b}"

def generate_set_notation():
    A = random.choice(['A', 'B', 'C'])
    B = random.choice(['X', 'Y', 'Z'])
    ops = ["\\cup", "\\cap", "\\setminus", "\\subseteq", "\\supseteq"]
    return f"{A} {random.choice(ops)} {B}"
def derivative_normal():
    # Normal derivative: d(variable) / d(variable)
    numerator = 'd' + random_var(1)   # e.g. dy
    denominator = 'd' + random_var(1) # e.g. dx
    return f"\\frac{{{numerator}}}{{{denominator}}}"

def derivative_partial():
    # Partial derivative: ∂(variable) / ∂(variable)
    numerator_var = random_var(1)
    denominator_var = random_var(1)
    return f"\\frac{{\\partial {numerator_var}}}{{\\partial {denominator_var}}}"

def quadratic_factored():
    x = random_var()
    a = random.randint(1, 5)
    b = random.randint(1, 5)
    return f"({x} + {a})({x} + {b}) = 0"

def quadratic_completed_square():
    x = random_var()
    a = random.randint(1, 5)
    b = random.randint(1, 5)
    return f"({x} + {a})^2 - {b}^2 = 0"

def cubic_expanded():
    x = random_var()
    a, b, c, d = [random.randint(-5, 5) for _ in range(4)]
    return f"{a}{x}^3 + {b}{x}^2 + {c}{x} + {d} = 0"


def exponential_eq():
    base = random.choice(['e', 2, 10, random_int()])
    exp = random.randint(0, 100)
    return f"{base}^{{{ exp}}}"

def with_subscripts():
    var = random_var()
    sub = random.randint(1, 1000)
    return f"{var}_{{{sub}}}"

def decimal_addition():
    a = round(random.uniform(1, 100), 2)
    b = round(random.uniform(1, 100), 2)
    return f"{a} + {b}"
def decimal_single():
    a = random.randint(0, 1000)
    b= random.randint(0, 9)
    return f"{a}.{b}"
def decimal_double():
    a = random.randint(0, 1000)
    b= random.randint(11, 99)
    return f"{a}.{b}"
def decimal_point():
    b= random.randint(11, 99)
    return f".{b}"
def decimal_triple():
    a = random.randint(0, 1000)
    b= random.randint(111, 999)
    return f"{a}.{b}"

def decimal_multiplication():
    a = round(random.uniform(0.1, 10), 2)
    b = round(random.uniform(0.1, 10), 2)
    return f"{a} \\times {b}"



def mult_random_var(length=2):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

# --- Decimal versions (from before) ---

def mult_addition_terms_dec(num_terms=4):
    terms = [round(random.uniform(1, 100), 2) for _ in range(num_terms)]
    return " + ".join(map(str, terms))

def mult_subtraction_terms_dec(num_terms=4):
    terms = [round(random.uniform(1, 100), 2) for _ in range(num_terms)]
    return " - ".join(map(str, terms))

def mult_multiplication_terms_dec(num_terms=4):
    terms = [round(random.uniform(1, 10), 2) for _ in range(num_terms)]
    return " \\times ".join(map(str, terms))

def mult_division_terms_dec(num_terms=4):
    terms = [round(random.uniform(1, 10), 2) for _ in range(num_terms)]
    return " \\div ".join(map(str, terms))

def mult_addition_vars(num_terms=4):
    terms = [random_var() for _ in range(num_terms)]
    return " + ".join(terms)

def mult_subtraction_vars(num_terms=4):
    terms = [random_var() for _ in range(num_terms)]
    return " - ".join(terms)

def mult_multiplication_vars(num_terms=4):
    terms = [random_var() for _ in range(num_terms)]
    return " \\times ".join(terms)

def mult_division_vars(num_terms=4):
    terms = [random_var() for _ in range(num_terms)]
    return " \\div ".join(terms)

def linear_equation_mult_vars(num_terms=2):
    left_terms = []
    for _ in range(num_terms):
        coef = random.randint(1, 10)
        var = mult_random_var()
        left_terms.append(f"{coef}{var}")
    right = random.randint(1, 100)
    left_expr = " + ".join(left_terms)
    return f"{left_expr} = {right}"

# --- New integer versions ---

def mult_addition_terms_int(num_terms=4):
    terms = [random.randint(1, 100) for _ in range(num_terms)]
    return " + ".join(map(str, terms))

def mult_subtraction_terms_int(num_terms=4):
    terms = [random.randint(1, 100) for _ in range(num_terms)]
    return " - ".join(map(str, terms))

def mult_multiplication_terms_int(num_terms=4):
    terms = [random.randint(1, 10) for _ in range(num_terms)]
    return " \\times ".join(map(str, terms))

def mult_division_terms_int(num_terms=4):
    terms = [random.randint(1, 10) for _ in range(num_terms)]
    return " \\div ".join(map(str, terms))

# --- New fraction versions ---

def random_fraction():
    numerator = random.randint(1, 10)
    denominator = random.randint(1, 10)
    frac = Fraction(numerator, denominator)
    return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"

def mult_addition_terms_frac(num_terms=4):
    terms = [random_fraction() for _ in range(num_terms)]
    return " + ".join(terms)

def mult_subtraction_terms_frac(num_terms=4):
    terms = [random_fraction() for _ in range(num_terms)]
    return " - ".join(terms)

def mult_multiplication_terms_frac(num_terms=4):
    terms = [random_fraction() for _ in range(num_terms)]
    return " \\times ".join(terms)

def mult_division_terms_frac(num_terms=4):
    terms = [random_fraction() for _ in range(num_terms)]
    return " \\div ".join(terms)


def generate_large_number():
    return str(random.choice([1, -1]) * random.randint(1000, 100000))


def square_root():
    return f"\\sqrt{{{random.randint(1, 1000)}}}"
def cube_root():
    return f"\\sqrt [{{{random.randint(3,100 )}}}] {{{random.randint(1, 100)}}}"
def surd_with_coeff():
    coeff = random.randint(1, 100)
    inner = random.randint(2, 30000)
    return f"{coeff}\\sqrt{{{inner}}}"
def factorial_expr():
    n = random.randint(0, 100)
    return f"{n}!"


def fraction_with_var():
    return f"\\frac{{{random_var()} + {random.randint(1,5)}}}{{{random.randint(1, 10)}}}"


def generate_ratio():
    return f"{random.randint(1, 2000)} : {random.randint(1, 2000)}"

def set_operations():
    A = random.choice(['A', 'B'])
    B = random.choice(['X', 'Y'])
    ops = ["\\cup", "\\cap", "\\setminus", "\\subseteq", "\\supseteq", "\\in", "\\notin"]
    return f"{A} {random.choice(ops)} {B}"

def comparison_signs():
    signs = ["<", ">", "\\leq", "\\geq", "\\neq", "="]
    return f"{random_int()} {random.choice(signs)} {random_int()}"

def approximate():
    return f"{random.randint(1, 10)} \\approx {random.randint(1, 10)}"

def similar_to():
    return f"\\triangle{random_var()+random_var()+random_var()}\\sim \\triangle {random_var()+random_var()+random_var()}"

def congruent_to():
    return f"\\angle {random_var()+random_var()+random_var()} \\cong \\angle {random_var()+random_var()+random_var()}"

import random

greek_latex = [
    "\\alpha", "\\beta", "\\gamma", "\\delta", "\\epsilon", "\\zeta", "\\eta", "\\theta", "\\iota", "\\kappa",
    "\\lambda", "\\mu", "\\nu", "\\xi", "\\pi", "\\rho", "\\sigma", "\\tau", "\\upsilon", "\\phi", "\\chi", "\\psi", "\\omega",
    "\\varepsilon", "\\vartheta", "\\varpi", "\\varrho", "\\varsigma", "\\varphi", "\\varkappa",
    "\\Gamma", "\\Delta", "\\Theta", "\\Lambda", "\\Xi", "\\Pi", "\\Sigma", "\\Upsilon", "\\Phi", "\\Psi", "\\Omega",
    "\\digamma", "\\Stigma", "\\Sampi", "\\Qoppa", "\\beth", "\\gimel", "\\daleth"
]

def random_greek():
    return random.choice(greek_latex)

def generate_greek_equation_simple():
    return f"{random_greek()} = {random.randint(1, 20)}"

def generate_greek_quadratic():
    x = random_greek()
    a = random.randint(1, 5)
    b = random.randint(1, 5)
    return f"{a}{x}^2 + {b}{x} = 0"

def generate_greek_derivative():
    var = random_greek()
    fx = random_greek()
    return f"\\frac{{d}}{{d{var}}}({fx}^2)"



def random_integral_indefinite():
    var = mult_random_var(1)
    func = mult_random_var(2)
    return f"\\int {func} \\, d{var}"

def random_integral_definite():
    var = mult_random_var(1)
    func = mult_random_var(2)
    a = random.randint(1, 5)
    b = random.randint(6, 10)
    return f"\\int_{{{a}}}^{{{b}}} {func} \\, d{var}"

def random_integral_indefinite():
    var = mult_random_var(1)
    func = mult_random_var(2)
    return f"\\int {func} \\, d{var}"



def mult_random_var(n=1):
    # Dummy implementation for demonstration
    vars = ['x', 'y', 'z']
    funcs = ['x^2', 'e^x', '\\sin x', '\\ln x', '1/x']
    return random.choice(vars if n == 1 else funcs)

def random_integral_definite_inf():
    var = mult_random_var(1)
    func = mult_random_var(2)

    # Bounds can be finite or infinity
    bounds = ['-\\infty', '\\infty', "-1", "0", "1","\\pi", "-\\pi" ] 
    a = random.choice(bounds)
    b = random.choice(bounds)
    
    # Ensure lower < upper in a numeric sense, or just switch for readability
    if bounds.index(str(a)) > bounds.index(str(b)):
        a, b = b, a

    return f"\\int_{{{"\\infty"}}}^{{{b}}} {func} \\, d{var}"
def generate_logic_expression():
    def rand_sym():
        # Randomly return a letter or number
        if random.random() < 0.5:
            return random.choice(string.ascii_lowercase)
        else:
            return str(random.randint(0, 9))

    a = rand_sym()
    b = rand_sym()

    expressions = [
        rf"{random.randint(1, 360)}^\circ",
        rf"-{a}",
        rf"\bar{{{a}}}",
        rf"{a}'",
        rf"{a} \wedge {b}",
        rf"{a} \cdot {b}",
        rf"{a} \mid {b}",
        rf"\frac{{{a}}}{{{b}}}",
        rf"{a} \downarrow {b}",
        rf"{a} \Delta {b}",
        rf"{a} \therefore {b}",
        rf"{a} > {b}",
        rf"{a} \subset {b}",
        r"\leftrightarrow",
        r"\equiv",
        rf"{a} \bigoplus {b}",
    ]

    return random.choice(expressions)

def derivative_normal_order(order=1):
    numerator = 'd' + random_var(1)
    denominator = 'd' + random_var(1)
    if order == 1:
        return f"\\frac{{{numerator}}}{{{denominator}}}"
    else:
        return f"\\frac{{d^{order}{numerator[1:]}}}{{d{denominator[1:]}^{order}}}"

def derivative_partial_order(order=1):
    numerator_var = random_var(1)
    denominator_var = random_var(1)
    if order == 1:
        return f"\\frac{{\\partial {numerator_var}}}{{\\partial {denominator_var}}}"
    else:
        return f"\\frac{{\\partial^{order} {numerator_var}}}{{\\partial {denominator_var}^{order}}}"

def generate_mixed_expression():
    parts = [
        generate_variable_expression(),
        generate_fraction(),
        generate_trig(),
    ]
    random.shuffle(parts)
    return " + ".join(parts)

generators = [
    # Arithmetic
    ("Addition", generate_addition),
    ("Subtraction", generate_subtraction),
    ("Multiplication", generate_multiplication),
    ("Division", generate_division),
    ("Single Digits", generate_digit),
    ("Double Digits", generate_double_digit),
    ("Three Digits", generate_three_digits),
    ("Decimal Addition", decimal_addition),
    ("Decimal Multiplication", decimal_multiplication),
    ("Decimal Single", decimal_single),
    ("Decimal Double", decimal_double),
    ("Decimal Triple", decimal_triple),
    ("Decimal starting with point", decimal_point),

    # Fractions
    ("Fraction", generate_fraction),
    ("Mixed fraction", generate_mixed_fraction),
    ("Fraction with Variable", fraction_with_var),
    ("Addition Fractions", mult_addition_terms_frac),
    ("Subtraction Fractions", mult_subtraction_terms_frac),
    ("Multiplication Fractions", mult_multiplication_terms_frac),
    ("Division Fractions", mult_division_terms_frac),

    # Integers
    ("Addition Integers", mult_addition_terms_int),
    ("Subtraction Integers", mult_subtraction_terms_int),
    ("Multiplication Integers", mult_multiplication_terms_int),
    ("Division Integers", mult_division_terms_int),

    # Variables
    ("Variables", random_var),
    ("Addition Variables", mult_addition_vars),
    ("Subtraction Variables", mult_subtraction_vars),
    ("Multiplication Variables", mult_multiplication_vars),
    ("Division Variables", mult_division_vars),
    ("Variable Expression", generate_variable_expression),
    ("Linear Equation Mult Vars", linear_equation_mult_vars),

    # Equations
    ("Quadratic Equations", generate_quadratic),
    ("Quadratic Factored Form", quadratic_factored),
    ("Quadratic Completed Square", quadratic_completed_square),
    ("Cubic Equation", generate_cubic),
    ("Cubic Expanded", cubic_expanded),
    ("Exponential Equation", exponential_eq),

    # Inequalities
    ("Inequality", generate_inequality),
    ("Variable Inequality", generate_variable_inequality),
    ("Compound Inequality", generate_compound_inequality),
    ("Fraction Inequality", generate_fraction_inequality),
    ("Absolute Value Inequality", generate_absolute_inequality),
    ("Power Inequality", generate_power_inequality),

    # Special Functions
    ("Absolute Value", generate_absolute_value),
    ("Modulus", generate_modulus),
    ("Factorial", factorial_expr),
    ("Root", generate_root),
    ("Nth Root", generate_nth_root),
    ("Square Root", square_root),
    ("Cube Root", cube_root),
    ("Surd with Coefficient", surd_with_coeff),

    # Advanced Topics
    ("Logarithm", generate_logarithm),
    ("Exponential", generate_exponential),
    ("Power", generate_power),
    ("Trig", generate_trig),

    # Sets
    ("Set Notation", generate_set_notation),
    ("Set Operations", set_operations),

    # Other
    ("Greek Letters", random_greek),
    ("Subscripts", with_subscripts),
    ("Large Numbers", generate_large_number),

    # Multiple Term Expressions
    ("Multi-Term Addition Decimals", mult_addition_terms_dec),
    ("Multi-Term Subtraction Decimals", mult_subtraction_terms_dec),
    ("Multi-Term Multiplication Decimals", mult_multiplication_terms_dec),
    ("Multi-Term Division Decimals", mult_division_terms_dec),

    # Calculus
    ("Definite Integral", random_integral_definite),
    ("Indefinite Integral", random_integral_indefinite),
    ("Improper Integral", random_integral_definite_inf),
]
grade_mapping = {
    # Arithmetic
    "Addition": "Elementary",
    "Subtraction": "Elementary",
    "Multiplication": "Elementary",
    "Division": "Elementary",
    "Single Digits": "Elementary",
    "Double Digits": "Elementary",
    "Three Digits": "Elementary",
    "Decimal Addition": "Elementary",
    "Decimal Multiplication": "Elementary",
    "Decimal Single": "Elementary",
    "Decimal Double": "Elementary",
    "Decimal Triple": "Elementary",
    "Decimal starting with point": "Elementary",
    
    # Fractions
    "Fraction": "Elementary",
    "Mixed fraction": "Elementary",
    "Fraction with Variable": "Middle",
    "Addition Fractions": "Middle",
    "Subtraction Fractions": "Middle",
    "Multiplication Fractions": "Middle",
    "Division Fractions": "Middle",
    
    # Integers
    "Addition Integers": "Elementary",
    "Subtraction Integers": "Elementary",
    "Multiplication Integers": "Elementary",
    "Division Integers": "Elementary",
    
    # Variables
    "Variables": "Middle",
    "Addition Variables": "Middle",
    "Subtraction Variables": "Middle",
    "Multiplication Variables": "Middle",
    "Division Variables": "Middle",
    "Variable Expression": "Middle",
    "Linear Equation Mult Vars": "Middle",
    
    # Equations
    "Quadratic Equations": "High",
    "Quadratic Factored Form": "High",
    "Quadratic Completed Square": "High",
    "Cubic Equation": "High",
    "Cubic Expanded": "High",
    "Exponential Equation": "High",
    
    # Inequalities
    "Inequality": "Middle",
    "Variable Inequality": "Middle",
    "Compound Inequality": "High",
    "Fraction Inequality": "High",
    "Absolute Value Inequality": "High",
    "Power Inequality": "High",
    
    # Special Functions
    "Absolute Value": "Elementary",
    "Modulus": "Middle",
    "Factorial": "Middle",
    "Root": "Elementary",
    "Nth Root": "Middle",
    "Square Root": "Elementary",
    "Cube Root": "Middle",
    "Surd with Coefficient": "Middle",
    
    # Advanced Topics
    "Logarithm": "High",
    "Exponential": "High",
    "Power": "Middle",
    "Trig": "High",
    
    # Sets
    "Set Notation": "Middle",
    "Set Operations": "Middle",
    
    # Other
    "Greek Letters": "Middle",
    "Subscripts": "Middle",
    "Large Numbers": "Middle",
    
    # Multiple Term Expressions
    "Multi-Term Addition Decimals": "Elementary",
    "Multi-Term Subtraction Decimals": "Elementary",
    "Multi-Term Multiplication Decimals": "Elementary",
    "Multi-Term Division Decimals": "Elementary",
    
    # Calculus
    "Definite Integral": "High",
    "Indefinite Integral": "High",
    "Improper Integral":"High",
    # Greek Specific
    "Greek Equation Simple": "Middle",
    "Greek Quadratic": "High",
    "Greek Derivative": "High",
}


# === LOAD NEMETH MAPPING ===
with open("nemeth_cleaned.json", "r", encoding="utf-8") as f:
    nemeth_data = json.load(f)

nemeth_mapping = {
    **nemeth_data.get("letters", {}),
    **nemeth_data.get("mathSymbols", {}),
    **nemeth_data.get("theoremSymbols", {}),
    **nemeth_data.get("numbers", {}),
}


import re

def preprocess_latex(latex_str):
    """Cleans and standardizes LaTeX expressions before conversion."""
    latex_str = latex_str.replace("^ { 0 } / 。", "%")
    latex_str = latex_str.replace("^ { 0 } / _ { 0 }", "%")

    latex_str = latex_str.replace("。", ".")
    # Basic cleanup (removes excessive spaces and strips any unwanted extra spaces)
    latex_str = re.sub(r'\s+', ' ', latex_str).strip()

    # Remove spaces inside \operatorname and \operatorname* to avoid parsing issues
    latex_str = re.sub(r'\\operatorname\*?\s*\{\s*([a-zA-Z\s]+?)\s*\}', lambda m: '\\operatorname*{' + m.group(1).replace(' ', '') + '}', latex_str)

    # Handle \underset { x \to 0 } { \lim }
    latex_str = re.sub(
        r'\\underset\s*\{\s*([^{}]+?)\s*\}\s*\{\s*(\\lim)\s*\}',
        r'\\lim_{\1}',  # Replace with \lim_{x \to 0}
        latex_str
    )

    # Handle \underset { x \to 0 } { \operatorname* { l i m } }
    latex_str = re.sub(
        r'\\underset\s*\{\s*([^{}]+?)\s*\}\s*{\\operatorname\*\{\s*([^{}]+?)\s*\}}',
        r'\\lim_{\1}',  # Replace with \lim_{x \to 0}
        latex_str
    )

    # Handle \operatorname* and \operatorname and remove spaces inside operators
    latex_str = re.sub(
        r'\\operatorname\*?\s*\{\s*([a-zA-Z]+)\s*\}',
        lambda m: '\\' + m.group(1),  # Converts \operatorname{cos} -> \cos
        latex_str
    )
    latex_str = re.sub(
        r'(\d+)\s*\\frac\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}',
        r'\1 \\mixedfrac-b \2 \\frac-separator \3 \\mixedfrac-e',
        latex_str
    )
    latex_str = re.sub(
        r'(\d+)\s*\\frac\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}',
        r'\1 \\mixedfrac-b \2 \\frac-separator \3 \\mixedfrac-e',
        latex_str
    )
    latex_str = re.sub(
        r'(\d+)\s*\\vec\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}',
        r'\1 \\mixedfrac-b \2 \\frac-separator \3 \\mixedfrac-e',
        latex_str
    )
    # Format fractions like \frac{a}{b} (handling LaTeX math fractions)
    latex_str = re.sub(
        r'\\frac\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}',
        r'\\frac-b \1 \\frac-separator \2 \\frac-e',  # Formatting fractions
        latex_str
    )

    # Handle mixed fractions (whole number with fraction)
 
    latex_str = re.sub(
        r'\smallsetminus',
        r'\therefore',
        latex_str
    )

    # Handle simple array environments like \begin{array}{cc} { -1 } & {} \\ \end{array}
    latex_str = latex_str.replace(
        r'\begin{array} { c c } { - 1 } & { } \\ \end{array}',
        '-1'
    )


    # Remove \operatorname{...} but keep the inner content without spaces
    latex_str = re.sub(
        r'\\operatorname\s*\{\s*([\w\s]+?)\s*\}',
        lambda m: "\\" + m.group(1).replace(" ", " "),
        latex_str
    )

    # STRIP ALL MATH FORMATTING
    latex_str = re.sub(r'\\(mathfrak|mathbf|mathit|mathrm|mathsf|mathtt|bf|textbf|rm|it|sf|sc|qquad|quad)\s*\{\s*([^{}]+?)\s*\}', r'\2', latex_str)
    latex_str = re.sub(r'\{\s*\\(mathfrak|mathbf|mathit|mathrm|mathsf|mathtt|bf|textbf|rm|it|sf|sc)\s+([^{}]+?)\s*\}', r'\2', latex_str)
    latex_str = re.sub(r'\\(mathfrak|mathbf|mathit|mathrm|mathsf|mathtt|bf|textbf|rm|it|sf|sc)\s+', '', latex_str)

    # Fix exponent and subscript spacing
    latex_str = re.sub(r'([a-zA-Z0-9])([\^_])', r'\1\2', latex_str)

    # Wrap superscripts with tags: handle ^{...}
    latex_str = re.sub(
        r'\^\s*\{\s*([^{}]+?)\s*\}',
        r'\\superscript-b \1 \\superscript-e',
        latex_str
    )

    # Wrap superscripts with tags: handle ^x (no braces)
    latex_str = re.sub(
        r'\^([a-zA-Z0-9])',
        r'\\superscript-b \1 \\superscript-e',
        latex_str
    )
    latex_str = re.sub(
        r'\\qquad',
        r' ',
        latex_str
    )
    # Handle subscripts like _{...}
    latex_str = re.sub(
        r'\_\s*\{\s*([^{}]+?)\s*\}',
        r'\\subscript-b \1 \\subscript-e',
        latex_str
    )

    # Handle \sqrt[...]{...}, separating the index and base
    latex_str = re.sub(r'\\sqrt\s*\[(.*?)\]\s*\{(.*?)\}', r'\\sqrtib \1 \\sqrtie \\sqrt-b  \2 \\sqrt-e', latex_str)

    # Handle \sqrt{...} (no index)
    latex_str = re.sub(r'\\sqrt\s*\{(.*?)\}', r'\\sqrt-b  \1 \\sqrt-e', latex_str)
    latex_str = latex_str.replace(r'\begin{array}{cc} {', '')
    latex_str = latex_str.replace(r'\begin{array} { c c } {', '')

    latex_str = latex_str.replace(r'\begin{array}{cc}', '')
    latex_str = latex_str.replace(r'\begin{array} { c c }', '')
    latex_str = latex_str.replace(r'\begin{array}{cc}{', '')
    latex_str = latex_str.replace(r'\begin{array} { c c }{', '')
    # Remove the literal \end{array}
    latex_str = latex_str.replace(r'} \\ \end{array}', '')
    # Remove the literal \end{array}
    latex_str = latex_str.replace(r'\end{array}', '')

    # Fix decimals
    latex_str = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', latex_str)
    latex_str = re.sub(r'(?<!\d)\.\s*(\d+)', r'.\1', latex_str)

    # Merge digit groups like 1 234 -> 1234
    latex_str = re.sub(r'(?:\d(?: \d)+)', lambda m: m.group(0).replace(" ", ""), latex_str)
# Merge digit groups like 1 234 -> 1234
    latex_str = re.sub(r'\s+', ' ', latex_str).strip()

    latex_str = re.sub(r'~+', ' ~ ', latex_str)

    # Remove unwanted space between digits and next character
    latex_str = re.sub(r'(?<=\d)\s+(?=[a-zA-Z])', ' ', latex_str)  # only allow digit-letter merging

# Remove \superscript-e only if it comes after \int and \superscript-b
    # Remove \subscript-e when it's directly after an \int ... \subscript-b ...
    latex_str = re.sub(
        r'(\\int(?:\\[a-z]+)*\s+\\subscript-b\s+[^\s]+)\s+\\subscript-e',
        r'\1',
        latex_str
    )
    latex_str = re.sub(
        r'(\\int(?:\\subscript-b\s*\S+)\s*)\\subscript-e',
        r'\1',
        latex_str
    )


    return latex_str



def translate_to_braille(token):
    return nemeth_mapping.get(token, token)

def translate_latex(latex_str):
    if not isinstance(latex_str, str):
        raise ValueError("Input must be a string")

    latex_str = latex_str.replace(r'\,', ' ')  # Add this to convert \\, to space
    latex_str = latex_str.replace(r'd ', r'd')
    latex_str = latex_str.replace(r'\\~', r'\\TILDE')
    latex_str = re.sub(r'~+', ' ', latex_str)
    latex_str = re.sub(r'[{}]', '', latex_str)
    latex_str = re.sub(r'\s+', ' ', latex_str).strip()

    tokens = re.findall(
        r'\\[a-zA-Z]+(?:-[a-zA-Z0-9]+)?'
        r'|[0-9]+[a-zA-Z]+'
        r'|[0-9]*\.[0-9]+'
        r'|[0-9]+'
        r'|[a-zA-Z]+'
        r'|[^\s]',
        latex_str
    )

    # Merge negative numbers
    merged_tokens = []
    i = 0
    while i < len(tokens):
        if (
            tokens[i] == '-' and
            i + 1 < len(tokens) and
            (tokens[i + 1].isdigit() or re.match(r'[0-9]*\.[0-9]+', tokens[i + 1])) and
            (i == 0 or tokens[i - 1] in ['=', '+', '-', '*', '/', '^', '(', '[', '{'])
        ):
            merged_tokens.append('-' + tokens[i + 1])
            i += 2
        else:
            merged_tokens.append(tokens[i])
            i += 1
    tokens = merged_tokens

    output = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        braille_piece = ""

        if token == "\\superscript-b":
                segment = [nemeth_mapping[token]]  # start superscript ⠘
                i += 1
                while i < len(tokens) and tokens[i] != "\\superscript-e":
                    inner_token = tokens[i]
                    if inner_token in nemeth_mapping:
                        segment.append(nemeth_mapping[inner_token])  # use the mapping directly
                    else:
                        for ch in inner_token:
                            segment.append(translate_to_braille(ch))  # fallback: translate character by character
                    i += 1
                if i < len(tokens) and tokens[i] == "\\superscript-e":
                    segment.append(nemeth_mapping[tokens[i]])  # ⠘⠄
                    i += 1
                braille_piece = ''.join(segment)
                output.append(braille_piece)
                continue


        
        elif token == "\\subscript-b":
              segment = [nemeth_mapping[token]]
              i += 1
              number_started = False
              while i < len(tokens) and tokens[i] not in ["\\superscript-b", "\\subscript-e"]:
                    inner_token = tokens[i]
                    if inner_token in nemeth_mapping:
                        segment.append(nemeth_mapping[inner_token])  # use the mapping directly
                    else:
                        for ch in inner_token:
                            segment.append(translate_to_braille(ch))  # fallback: translate character by character
                    i += 1
              # Only append subscript-e if explicitly found
              if i < len(tokens) and tokens[i] == "\\subscript-e":
                  segment.append(nemeth_mapping[tokens[i]])
                  i += 1
              # If the loop broke because of superscript-b, do NOT append subscript-e; leave as is
              braille_piece = ''.join(segment)
              output.append(braille_piece)
              continue

        elif token == "\\frac-b":
                segment = [nemeth_mapping[token]]  # start superscript ⠘
                i += 1
                while i < len(tokens) and tokens[i] not in ["\\frac-seperator", "\\frac-b"]:              
                    inner_token = tokens[i]
                    if inner_token in nemeth_mapping:
                        segment.append(nemeth_mapping[inner_token])  # use the mapping directly
                    else:
                        for ch in inner_token:
                            segment.append(translate_to_braille(ch))  # fallback: translate character by character
                    i += 1
                if i < len(tokens) and tokens[i] == "\\frac-e":
                    segment.append(nemeth_mapping[tokens[i]])  # ⠘⠄
                    i += 1
                braille_piece = ''.join(segment)
                output.append(braille_piece)
                continue
        elif token == "\\mixedfrac-b":
                segment = [nemeth_mapping[token]]  # start superscript ⠘
                i += 1
                while i < len(tokens) and tokens[i] not in ["\\frac-seperator", "\\mixedfrac-b"]:              
                    inner_token = tokens[i]
                    if inner_token in nemeth_mapping:
                        segment.append(nemeth_mapping[inner_token])  # use the mapping directly
                    else:
                        for ch in inner_token:
                            segment.append(translate_to_braille(ch))  # fallback: translate character by character
                    i += 1
                if i < len(tokens) and tokens[i] == "\\mixedfrac-e":
                    segment.append(nemeth_mapping[tokens[i]])  # ⠘⠄
                    i += 1
                braille_piece = ''.join(segment)
                output.append(braille_piece)
                continue

        elif re.match(r'-?[0-9]+[a-zA-Z]+', token):
            match = re.match(r'(-?)([0-9]+)([a-zA-Z]+)', token)
            sign, digits, letters = match.groups()
            num = nemeth_mapping["NUMBER-SYMBOL"] + ''.join(translate_to_braille(d) for d in digits)
            letters = ''.join(translate_to_braille(c) for c in letters)
            braille_piece = nemeth_mapping["-"] + num + letters if sign else num + letters

        elif re.match(r'-?\d*\.\d+', token):
            match = re.match(r'(-?)(\d*)\.(\d+)', token)
            sign, whole, decimal = match.groups()

            # ⠼⠨⠖⠢ for .65
            num = (
                nemeth_mapping["NUMBER-SYMBOL"] +
                (''.join(translate_to_braille(d) for d in whole) if whole else '') +
                nemeth_mapping["."] +
                ''.join(translate_to_braille(d) for d in decimal)
            )

            braille_piece = nemeth_mapping["-"] + num if sign else num

        elif token.lstrip('-').isdigit():
            digits = token.lstrip('-')
            num = nemeth_mapping["NUMBER-SYMBOL"] + ''.join(translate_to_braille(d) for d in digits)
            braille_piece = nemeth_mapping["-"] + num if token.startswith('-') else num

        elif token in ['+', '-', '=', '*', '/', '^', '_']:
            braille_piece = translate_to_braille(token)
        elif token == "\\sqrt-b":
            segment = [nemeth_mapping["\\sqrt-b"]]
            i += 1
            while i < len(tokens) and tokens[i] != "\\sqrt-e":
                inner = tokens[i]
                if inner.lstrip('-').isdigit():
                    braille_num = ''.join(translate_to_braille(d) for d in inner.lstrip('-'))
                    if inner.startswith('-'):
                        segment.append(nemeth_mapping["-"] + braille_num)
                    else:
                        segment.append(braille_num)
                elif re.match(r'-?\d*\.\d+', inner):  # float
                    match = re.match(r'(-?)(\d*)\.(\d+)', inner)
                    sign, whole, decimal = match.groups()
                    num = (
                        (''.join(translate_to_braille(d) for d in whole) if whole else '') +
                        nemeth_mapping["."] +
                        ''.join(translate_to_braille(d) for d in decimal)
                    )
                    if sign:
                        segment.append(nemeth_mapping["-"] + num)
                    else:
                        segment.append(num)
                else:
                    segment.append(translate_to_braille(inner))
                i += 1
            if i < len(tokens) and tokens[i] == "\\sqrt-e":
                segment.append(nemeth_mapping["\\sqrt-e"])
                i += 1
            braille_piece = ''.join(segment)

        elif token == "\\sqrtib":
            segment = [nemeth_mapping["\\sqrtib"]]
            i += 1
            while i < len(tokens) and tokens[i] != "\\sqrtie":
                inner = tokens[i]
                if inner.lstrip('-').isdigit():
                    braille_num = ''.join(translate_to_braille(d) for d in inner.lstrip('-'))
                    if inner.startswith('-'):
                        segment.append(nemeth_mapping["-"] + braille_num)
                    else:
                        segment.append(braille_num)
                elif re.match(r'-?\d*\.\d+', inner):  # float
                    match = re.match(r'(-?)(\d*)\.(\d+)', inner)
                    sign, whole, decimal = match.groups()
                    num = (
                        (''.join(translate_to_braille(d) for d in whole) if whole else '') +
                        nemeth_mapping["."] +
                        ''.join(translate_to_braille(d) for d in decimal)
                    )
                    if sign:
                        segment.append(nemeth_mapping["-"] + num)
                    else:
                        segment.append(num)
                else:
                    segment.append(translate_to_braille(inner))
                i += 1
            if i < len(tokens) and tokens[i] == "\\sqrtie":
                segment.append(nemeth_mapping["\\sqrtie"])
                i += 1
            braille_piece = ''.join(segment)
        
        elif token in ["|", r"\abs{"]:
            segment = [nemeth_mapping["|"]]
            i += 1
            while i < len(tokens) and tokens[i] != "|":
                inner = tokens[i]
                if inner.lstrip('-').isdigit():
                    braille_num = ''.join(translate_to_braille(d) for d in inner.lstrip('-'))
                    if inner.startswith('-'):
                        segment.append(nemeth_mapping["-"] + braille_num)
                    else:
                        segment.append(braille_num)
                elif re.match(r'-?\d*\.\d+', inner):  # float
                    match = re.match(r'(-?)(\d*)\.(\d+)', inner)
                    sign, whole, decimal = match.groups()
                    num = (
                        (''.join(translate_to_braille(d) for d in whole) if whole else '') +
                        nemeth_mapping["."] +
                        ''.join(translate_to_braille(d) for d in decimal)
                    )
                    if sign:
                        segment.append(nemeth_mapping["-"] + num)
                    else:
                        segment.append(num)
                else:
                    segment.append(translate_to_braille(inner))
                i += 1
            if i < len(tokens) and tokens[i] == "|":
                segment.append(nemeth_mapping["|"])
                i += 1
            braille_piece = ''.join(segment)
        else:
            if token in nemeth_mapping:
                braille_piece = nemeth_mapping[token]
            else:
                braille_piece = ''.join(translate_to_braille(char) for char in token)

        output.append(braille_piece)
    
        if (
            i + 1 < len(tokens)
            and re.match(r'[a-zA-Z0-9]+', token)
            and re.match(r'[a-zA-Z0-9]+', tokens[i + 1])
        ):
            output.append("⠀")  # blank for clarity

        i += 1

    output_str = ''.join(output)
    output_str = re.sub(r'([a-zA-Z0-9])\s*(\^|\_)', r'\1\2', output_str)
    return output_str

def latex_to_nemeth(latex_str):
    return f"⠇⠩{translate_latex(latex_str)}⠇⠱"




# === DATASET GENERATION ===
def generate_latex_dataset(n=10):
    dataset = []
    for i in range(n):
        name, func = random.choice(generators)   # Pick (name, function)
        expr = func()
        convert = preprocess_latex(expr)
        nemeth = latex_to_nemeth(convert)
        grade = grade_mapping.get(name, "Unknown")

        dataset.append({
            "input": f"latex2nemeth: {convert}",
            "output": nemeth,
            "name" : name,
            "grade": grade

        })
    return dataset


# === SAVE FUNCTIONS ===
def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_csv(data, path):
    keys = data[0].keys()
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

# === RUN PIPELINE ===
latex_dataset = generate_latex_dataset(10000)

save_csv(latex_dataset, "latex_nemeth_dataset.csv")

print("✅ Dataset generation complete and saved to JSON & CSV!")

