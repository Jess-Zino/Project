# utils/braille.py

unicode_to_ascii_braille = {
    '⠀': ' ', '⠮': '!', '⠐': '"', '⠼': '#', '⠫': '$', '⠩': '%', '⠯': '&', '⠄': "'",
    '⠷': '(', '⠾': ')', '⠡': '*', '⠬': '+', '⠠': ',', '⠤': '-', '⠨': '.', '⠌': '/',
    '⠴': '0', '⠂': '1', '⠆': '2', '⠒': '3', '⠲': '4', '⠢': '5', '⠖': '6', '⠶': '7',
    '⠦': '8', '⠔': '9', '⠱': ':', '⠰': ';', '⠣': '<', '⠿': '=', '⠜': '>', '⠹': '?',
    '⠈': '@', '⠁': 'A', '⠃': 'B', '⠉': 'C', '⠙': 'D', '⠑': 'E', '⠋': 'F', '⠛': 'G',
    '⠓': 'H', '⠊': 'I', '⠚': 'J', '⠅': 'K', '⠇': 'L', '⠍': 'M', '⠝': 'N', '⠕': 'O',
    '⠏': 'P', '⠟': 'Q', '⠗': 'R', '⠎': 'S', '⠞': 'T', '⠥': 'U', '⠧': 'V', '⠺': 'W',
    '⠭': 'X', '⠽': 'Y', '⠵': 'Z', '⠪': '[', '⠳': '\\', '⠻': ']', '⠘': '^', '⠸': '_',
}

def convert_unicode_to_ascii_braille(unicode_text: str) -> str:
    ascii_text = ""
    for char in unicode_text:
        ascii_char = unicode_to_ascii_braille.get(char)
        if ascii_char is None:
            raise ValueError(f"Unsupported Unicode Braille character: {repr(char)}")
        ascii_text += ascii_char
    return ascii_text
