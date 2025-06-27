import { useRef, useState } from "react";
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import * as SecureStore from "expo-secure-store";
import {
  GestureHandlerRootView,
  Pressable,
  ScrollView,
} from "react-native-gesture-handler";
import { FontAwesome } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";

import LiveKaTeXView from "@/components/ui/LiveKatexVieiw";
import LatexKeyboard from "@/components/ui/LatexKeyboard";
import { Colors } from "../../../constants/Colors";

const ImageToLatex = () => {
  const [darkMode, setDarkMode] = useState(true);
  const theme = darkMode ? Colors.dark : Colors.light;

  const [nemeth, setNemeth] = useState("");
  const [latexText, setLatexText] = useState("");
  const [renderedLatex, setRenderedLatex] = useState("");
  const [showLatexKeyboard, setShowLatexKeyboard] = useState(false);

  const router = useRouter();
  const inputRef = useRef(null);
  const wsRef = useRef(null);

  const handleInput = (input) => {
    if (input === "backspace") {
      setLatexText((prev) => prev.slice(0, -1));
    } else {
      setLatexText((prev) => prev + input);
    }
  };

  const handleTranslate = async () => {
    try {
      if (wsRef.current) {
        wsRef.current.close();
      }

      const token = await SecureStore.getItemAsync("userToken");

      if (!token) {
        console.warn("User token not found.");
        return;
      }

      const ws = new WebSocket(
        `ws://192.168.137.1:8000/convert/ws/latex-nemeth?token=${token}`
      );
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("✅ WebSocket connected");
        if (latexText.trim()) {
          ws.send(JSON.stringify({ latex: latexText }));
        }
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
        setNemeth(data.nemeth);
        setRenderedLatex(data.rendered);
        ws.close();
      };

      ws.onerror = (err) => {
        console.error("WebSocket error", err);
      };

      ws.onclose = () => {
        console.log("❌ WebSocket disconnected");
      };
    } catch (error) {
      console.error("Translation error:", error);
    }
  };

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
  },
  header: {
    paddingTop: 50,
    paddingBottom: 30,
    paddingHorizontal: 20,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: theme.tint,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 5,
  },
  title: {
    fontSize: 28,
    color: "#000",
    fontFamily: "PoppinsBold",
  },
  inputBox: {
    margin: 20,
    fontSize: 39,
    backgroundColor: theme.card,
    color: theme.tint,
    padding: 16,
    borderRadius: 12,
    fontFamily: "PoppinsRegular",
    minHeight: 150,
    textAlignVertical: "top",
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
    borderWidth: 1,
    borderColor: theme.latexB,
  },
  outputBox: {
    marginHorizontal: 20,
    marginTop: 16,
    padding: 16,
    borderRadius: 12,
    backgroundColor: theme.latexB,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 1,
  },
  sectionTitle: {
    fontSize: 20,
    fontFamily: "PoppinsSemiBold",
    color: "#000",
    marginBottom: 8,
  },
  button: {
    marginHorizontal: 20,
    marginTop: 20,
    backgroundColor: theme.buttonBackground,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: "center",
    borderColor: theme.btnBorder,
    borderWidth: 1,
    shadowColor: "#000",
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
    elevation: 4,
  },
  buttonText: {
    color: theme.buttonText,
    fontSize: 18,
    fontFamily: "PoppinsBold",
  },
  toggleButton: {
    marginHorizontal: 20,
    marginTop: 16,
    paddingVertical: 12,
    borderRadius: 10,
  borderColor: theme.ran,
    borderWidth: 2,
    backgroundColor: "transparent",
    alignItems: "center",
  },
  toggleText: {
    fontSize: 16,
    color: theme.ran,
    fontFamily: "PoppinsMedium",
  },
  keyboardWrapper: {
    position: "absolute",
    bottom: -80,
    left: 0,
    right: 0,
    backgroundColor: theme.card,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
    paddingBottom: 10,
    borderTopWidth: 1,
    borderTopColor: theme.latexB,
  },
});


  return (
    <GestureHandlerRootView style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()}>
          <FontAwesome name="angle-left" size={50}  color="#000" />
        </Pressable>

        <Text style={styles.title}>LaTeX to Nemeth</Text>

        <Pressable onPress={() => setDarkMode(!darkMode)}>
          <FontAwesome
            name={darkMode ? "moon-o" : "sun-o"}
            size={40}
            color="#000"
          />
        </Pressable>
      </View>

      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={{ flex: 1 }}
      >
        <SafeAreaView style={{ flex: 1 }}>
          <View style={styles.container}>
            <ScrollView
              keyboardShouldPersistTaps="handled"
              contentContainerStyle={{ paddingBottom: 150 }}
            >
              {nemeth !== "" && (
                <View
                  style={[styles.outputBox, { backgroundColor: theme.tint }]}
                >
                  <Text style={[styles.sectionTitle, { color: "#333" }]}>
                    Nemeth Render:
                  </Text>
                  <LiveKaTeXView value={renderedLatex} />
                </View>
              )}

              <View
                style={[styles.outputBox, { backgroundColor: theme.latexB }]}
              >
                <Text style={styles.sectionTitle}>LaTeX Preview:</Text>
                <LiveKaTeXView
                  value={latexText || "\\text{Your LaTeX will show here}"}
                />
              </View>

              <TextInput
                ref={inputRef}
                multiline
                value={latexText}
                onChangeText={setLatexText}
                style={[styles.inputBox]}
                placeholder="Enter LaTeX here"
                placeholderTextColor={theme.placeholder}
              />

              <TouchableOpacity style={styles.button} onPress={handleTranslate}>
                <Text style={styles.buttonText}>Translate to Nemeth</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.toggleButton}
                onPress={() => {
                  if (!showLatexKeyboard) {
                    inputRef.current?.focus();
                  }
                  setShowLatexKeyboard((prev) => !prev);
                }}
              >
                <Text style={styles.toggleText}>
                  {showLatexKeyboard
                    ? "Hide Math Keyboard"
                    : "Show Math Keyboard"}
                </Text>
              </TouchableOpacity>
            </ScrollView>

            {showLatexKeyboard && (
              <View style={styles.keyboardWrapper}>
                <LatexKeyboard onSelect={handleInput} />
              </View>
            )}
          </View>
        </SafeAreaView>
      </KeyboardAvoidingView>
    </GestureHandlerRootView>
  );
};

export default ImageToLatex;
