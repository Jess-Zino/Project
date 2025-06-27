import React from "react";
import { TextInput, StyleSheet } from "react-native";

const LatexEditor = ({ latexText, setLatexText }) => {
  return (
    <TextInput
      multiline
      style={styles.input}
      value={latexText}
      onChangeText={setLatexText}
      placeholder="Type LaTeX here..."
      placeholderTextColor="#888"
    />
  );
};

const styles = StyleSheet.create({
  input: {
    margin: 16,
    padding: 16,
    fontSize: 18,
    backgroundColor: "#222",
    color: "#fff",
    borderRadius: 10,
    minHeight: 100,
    textAlignVertical: "top",
  },
});

export default LatexEditor;
