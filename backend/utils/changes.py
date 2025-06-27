import json
import re
from collections import defaultdict, Counter
from fractions import Fraction
import csv
import string
import random
import os

# Get the current directory of this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(CURRENT_DIR, "..", "data", "nemeth_cleaned.json")  # adjust the path as needed

with open(JSON_PATH, "r", encoding="utf-8") as f:
    nemeth_data = json.load(f)

nemeth_mapping = {
    **nemeth_data.get("letters", {}),
    **nemeth_data.get("mathSymbols", {}),
    **nemeth_data.get("theoremSymbols", {}),
    **nemeth_data.get("numbers", {}),
}


import re
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
