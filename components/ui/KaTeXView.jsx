import React from "react";
import { View, StyleSheet, Dimensions } from "react-native";
import { WebView } from "react-native-webview";
import { Colors } from "../../constants/Colors"; // Importing Colors

const KaTeXView = ({ latex, darkMode }) => {
  const theme = darkMode ? Colors.dark : Colors.light;
  const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <!-- MathJax -->
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <!-- Speech Rule Engine -->
  <script src="https://cdn.jsdelivr.net/npm/speech-rule-engine"></script>
  <style>
    body {
      margin: 0;
      padding: 10px;
      font-size: 80px;
      font-weight:700;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: ${theme.background};
      color: ${theme.text};
    }
    #math {
      text-align: center;
    }
  </style>
</head>
<body>
  <div id="math">\\(${latex}\\)</div>

  <script>
    document.addEventListener("DOMContentLoaded", async function () {
      // Wait for MathJax to typeset
      MathJax.typesetPromise().then(() => {
        // Wait a little to ensure MathJax finishes rendering
        setTimeout(() => {
          try {
            // Initialize Speech Rule Engine (SRE)
            sre.System.getInstance().setupEngine({ 
              locale: 'en', 
              domain: 'mathspeak', 
              style: 'default'
            });

            const mathEl = document.querySelector('mjx-container');
            if (mathEl) {
              const mathML = MathJax.startup.toMathML(mathEl);
              const speech = sre.System.getInstance().toSpeech(mathML);
              window.ReactNativeWebView?.postMessage(speech); // Send back to React Native
            }
          } catch (e) {
            console.error("Speech generation error:", e);
          }
        }, 500);
      });
    });
  </script>
</body>
</html>
`;

  const screenWidth = Dimensions.get("window").width;

  return (
    <View style={[styles.container, { width: screenWidth - 40, height:140 }]}>
      <WebView
        originWhitelist={["*"]}
        source={{ html: htmlContent }}
        style={styles.webview}
        scrollEnabled={false}
        onMessage={(event) => {
          const spokenText = event.nativeEvent.data;
        }}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    height: 400,
    alignSelf: "center",
  },
  webview: {
    backgroundColor: "transparent",
    flex: 1,
  },
});

export default KaTeXView;
