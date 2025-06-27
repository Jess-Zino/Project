import React from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Dimensions,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import MathView from "react-native-math-view";
const latexSymbols = [
  // Core math
  { id: "0", symbol: "=", display: "=" },
  { id: "1", symbol: "+", display: "+" },
  { id: "2", symbol: "-", display: "−" },
  { id: "3", symbol: "\\times", display: "×" },
  { id: "4", symbol: "\\div", display: "÷" },
  { id: "5", symbol: "<", display: "<" },
  { id: "6", symbol: ">", display: ">" },
  { id: "7", symbol: "\\leq", display: "≤" },
  { id: "8", symbol: "\\geq", display: "≥" },
  { id: "9", symbol: "\\neq", display: "≠" },
  { id: "68", symbol: "\\log", display: "log" },
  { id: "69", symbol: "\\ln", display: "ln" },
  { id: "70", symbol: "\\exp", display: "exp" },

  // Trigonometry
  { id: "10", symbol: "\\sin", display: "sin" },
  { id: "11", symbol: "\\cos", display: "cos" },
  { id: "12", symbol: "\\tan", display: "tan" },
  { id: "13", symbol: "\\cot", display: "cot" },
  { id: "14", symbol: "\\sec", display: "sec" },
  { id: "15", symbol: "\\csc", display: "csc" },
  { id: "16", symbol: "^\\circ", display: "°" },
  { id: "17", symbol: "\\theta", display: "θ" },
  { id: "36", symbol: "\\pi", display: "π" },

  // Algebra & Exponents
  { id: "18", symbol: "x^{}", display: "xⁿ" },
  { id: "19", symbol: "x^2", display: "x²" },
  { id: "20", symbol: "_{}", display: "xₙ" },
  { id: "21", symbol: "\\sqrt{}", display: "√" },
  { id: "22", symbol: "\\frac{}{}", display: "a⁄b" },
  { id: "23", symbol: "\\frac{1}{x}", display: "1⁄x" },

  // Delimiters
  { id: "50", symbol: "(", display: "(" },
  { id: "51", symbol: ")", display: ")" },
  { id: "52", symbol: "[", display: "[" },
  { id: "53", symbol: "]", display: "]" },
  { id: "54", symbol: "{", display: "{" },
  { id: "55", symbol: "}", display: "}" },
  { id: "56", symbol: "\\left(", display: "⎡" },
  { id: "57", symbol: "\\right)", display: "⎤" },

  // Calculus
  { id: "24", symbol: "\\int", display: "∫" },
  { id: "26", symbol: "\\frac{d}{dx}", display: "𝑑⁄𝑑𝑥" },
  { id: "27", symbol: "\\partial", display: "∂" },

  // Greek letters
  { id: "29", symbol: "\\alpha", display: "α" },
  { id: "30", symbol: "\\beta", display: "β" },
  { id: "31", symbol: "\\gamma", display: "γ" },
  { id: "32", symbol: "\\delta", display: "δ" },
  { id: "33", symbol: "\\epsilon", display: "ε" },
  { id: "34", symbol: "\\lambda", display: "λ" },
  { id: "35", symbol: "\\mu", display: "μ" },
  { id: "37", symbol: "\\sigma", display: "σ" },
  { id: "38", symbol: "\\phi", display: "ϕ" },
  { id: "39", symbol: "\\omega", display: "ω" },

  // Logic & Set Theory
  { id: "40", symbol: "\\forall", display: "∀" },
  { id: "41", symbol: "\\exists", display: "∃" },
  { id: "42", symbol: "\\in", display: "∈" },
  { id: "43", symbol: "\\notin", display: "∉" },
  { id: "44", symbol: "\\cup", display: "∪" },
  { id: "45", symbol: "\\cap", display: "∩" },
  { id: "46", symbol: "\\subset", display: "⊂" },
  { id: "47", symbol: "\\subseteq", display: "⊆" },
  { id: "48", symbol: "\\supset", display: "⊃" },
  { id: "49", symbol: "\\supseteq", display: "⊇" },

  // Arrows
  { id: "58", symbol: "\\rightarrow", display: "→" },
  { id: "59", symbol: "\\leftarrow", display: "←" },
  { id: "60", symbol: "\\Rightarrow", display: "⇒" },
  { id: "61", symbol: "\\Leftarrow", display: "⇐" },
  { id: "62", symbol: "\\leftrightarrow", display: "↔" },

  // Accents
  { id: "63", symbol: "\\hat{}", display: "x̂" },
  { id: "64", symbol: "\\bar{}", display: "x̄" },
  { id: "65", symbol: "\\vec{}", display: "→x" },

  // Constants
  { id: "66", symbol: "\\approx", display: "≈" },
  { id: "67", symbol: "\\cdot", display: "⋅" },
];

export default function LatexKeyboard({ onSelect }) {
  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.key} onPress={() => onSelect(item.symbol)}>
      <Text style={styles.symbol}>{item.display}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.keyboardContainer}>
      <FlatList
        data={latexSymbols}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        horizontal
        showsHorizontalScrollIndicator={true}
        contentContainerStyle={styles.sliderContent}
      />
    </View>
  );
}
const styles = StyleSheet.create({
  keyboardContainer: {
    position: "absolute",
    bottom: 0,
    width: "100%",
    backgroundColor: "#0F172A",
    paddingTop: 10,
    paddingBottom: 20,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    shadowColor: "#000",
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 10,
  },
  keyboardGrid: {
    paddingHorizontal: 12,
    justifyContent: "center",
  },
  key: {
    backgroundColor: "#1E293B",
    borderRadius: 12,
    margin: 6,
    paddingVertical: 12,
    paddingHorizontal: 16,
    justifyContent: "center",
    alignItems: "center",
    flex: 1,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  symbol: {
    fontSize: 20,
    color: "#FACC15",
    fontFamily: "PoppinsRegular",
    textAlign: "center",
  },
});
