import React from "react";
import { View, Text } from "react-native";
import { checkReactElement } from "react-native-accessibility-engine";
import App from "../../app/(SplashScreen)/index"; // update this to the correct path to your component

export default function AccessibilityTestScreen() {
  const result = checkReactElement(<App />);

  console.log("🔍 Accessibility Issues Found:");
  result.violations.forEach((violation, index) => {
    console.log(`\n${index + 1}. ${violation.message}`);
    console.log(`   🔗 Path: ${violation.path.join(" > ")}`);
  });

  return (
    <View>
      <Text>Check your terminal for accessibility issues.</Text>
    </View>
  );
}
