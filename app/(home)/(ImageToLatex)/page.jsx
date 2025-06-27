import React, { useState, useEffect, useRef } from "react";

import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Pressable,
  Image,
  ActivityIndicator,
  useWindowDimensions,
} from "react-native";
import { Linking } from "react-native";
import * as Clipboard from "expo-clipboard";
import * as SecureStore from "expo-secure-store";
import * as ImagePicker from "expo-image-picker";
import * as FileSystem from "expo-file-system";
import * as Speech from "expo-speech";
import { FontAwesome } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import * as Sharing from "expo-sharing";
import { Colors } from "../../../constants/Colors";
import KaTeXView from "../../../components/ui/KaTeXView";
import LiveKaTeXView from "@/components/ui/LiveKatexVieiw";

export default function InferenceScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [latexOutput, setLatexOutput] = useState("");
  const [nemethOutput, setNemethOutput] = useState("");
  const [imageUri, setImageUri] = useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const wsRef = useRef(null);
  const brfWsRef = useRef(null);

  const nemethWsRef = useRef(null);
  const { width } = useWindowDimensions();
  const theme = darkMode ? Colors.dark : Colors.light;

  const styles = StyleSheet.create({
    container: {
      flexGrow: 1,
      paddingTop: 40,
      paddingBottom: 100,
      backgroundColor: theme.background,
    },
    header: {
      width: "100%",
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      paddingHorizontal: 20,
      paddingVertical: 20,
      backgroundColor: theme.tint,
      borderBottomLeftRadius: 20,
      borderBottomRightRadius: 20,
      shadowColor: "#000",
      shadowOpacity: 0.1,
      shadowRadius: 6,
      elevation: 5,
    },
    title: {
      fontSize: 24,
      fontFamily: "PoppinsBold",
      color: "#000",
    },
    dashedBox: {
      width: width * 0.8,
      height: width * 0.6,
      borderWidth: 5,
      borderColor: theme.tint,
      borderStyle: "dashed",
      borderRadius: 12,
      marginTop: 200,
      justifyContent: "center",
      alignItems: "center",
      alignSelf: "center",
      marginVertical: 20,
      backgroundColor: theme.card,
    },
    image: {
      width: width * 0.6,
      height: width * 0.5,
      borderRadius: 12,
      marginBottom: 20,
      alignSelf: "center",
    },
    buttonText: {
      color: theme.icon,
      fontSize: 18,
      fontFamily: "PoppinsMedium",
      marginTop: 10,
    },
    outputBox: {
      marginHorizontal: 20,
      marginBottom: 20,
      padding: 16,
      borderRadius: 12,
      backgroundColor: theme.latexB,
      shadowColor: "#000",
      shadowOpacity: 0.05,
      shadowRadius: 5,
      elevation: 2,
    },
    sectionTitle: {
      fontSize: 25,
      fontFamily: "PoppinsBold",
      color: "#000",
      marginBottom: 6,
    },
    mainV: {
      flex: 1,
      alignItems: "center",
      width: "100%",
      backgroundColor: theme.background,
    },
    actionButton: {
      backgroundColor: theme.buttonBackground,
      paddingVertical: 16,
      paddingHorizontal: 20,
      borderRadius: 12,
      marginTop: 20,
      alignSelf: "center",
      width: "80%",
      borderWidth: 1,
      borderColor: theme.btnBorder,
      shadowColor: "#000",
      shadowOpacity: 0.15,
      shadowOffset: { width: 0, height: 2 },
      shadowRadius: 5,
      elevation: 4,
    },
    actionText: {
      textAlign: "center",
      color: theme.buttonText,
      fontSize: 18,
      fontFamily: "PoppinsBold",
    },
    backButton: {
      padding: 10,
    },
  });

  const token = SecureStore.getItem("userToken");

  // Image-to-LaTeX WebSocket
  useEffect(() => {
    const socket = new WebSocket(
      `ws://192.168.137.1:8000/convert/ws/image-to-latex?token=${token}`
    );

    socket.onopen = () => {
      console.log("✅ Image-to-LaTeX WebSocket connected");
      wsRef.current = socket;
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("📩 LaTeX Message:", data);
      setLatexOutput(data.latex);
      Speech.speak(data.spoken_text, {
        language: "en",
        rate: 0.9,
        pitch: 1.0,
      });
    };

    socket.onerror = (error) => {
      console.error("❌ LaTeX WebSocket error:", error?.message || error);
    };

    socket.onclose = (e) => {
      console.log("🛑 LaTeX WebSocket closed", e.code, e.reason);
    };

    return () => {
      socket.close();
    };
  }, []);

  // LaTeX-to-Nemeth WebSocket
  useEffect(() => {
    const ws = new WebSocket(
      `ws://192.168.137.1:8000/convert/ws/latex-nemeth?token=${token}`
    );

    ws.onopen = () => {
      console.log("✅ LaTeX-to-Nemeth WebSocket connected");
      nemethWsRef.current = ws;
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("📩 Nemeth Message:", data);
      setNemethOutput(data.nemeth);
      Speech.speak(data.nemeth_spoken || "Converted to Nemeth", {
        language: "en",
        rate: 0.9,
      });
    };

    ws.onerror = (error) => {
      console.error("❌ Nemeth WebSocket error:", error?.message || error);
    };

    ws.onclose = (e) => {
      console.log("🛑 Nemeth WebSocket closed", e.code, e.reason);
    };

    return () => {
      ws.close();
    };
  }, []);

  const copyLatexToClipboard = () => {
    if (latexOutput) {
      Clipboard.setStringAsync(latexOutput);
      alert("📋 LaTeX copied to clipboard!");
    }
  };

  const runModel = async (uri) => {
    try {
      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      });

      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ image: base64 }));
        console.log("📤 Sent image to server");
        setLoading(true);
      } else {
        console.warn("⚠️ WebSocket not connected");
        setLatexOutput("WebSocket is not connected");
      }
    } catch (error) {
      console.error("❌ Error processing image:", error);
      setLatexOutput("Failed to process image");
    } finally {
      setLoading(false);
    }
  };

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled && result.assets.length > 0) {
      const uri = result.assets[0].uri;
      setImageUri(uri);
      runModel(uri);
    }
  };

  const convertToNemeth = () => {
    if (
      nemethWsRef.current &&
      nemethWsRef.current.readyState === WebSocket.OPEN
    ) {
      nemethWsRef.current.send(JSON.stringify({ latex: latexOutput }));
      console.log("📤 Sent LaTeX to Nemeth converter");
    } else {
      console.warn("⚠️ Nemeth WebSocket not connected");
      alert("Nemeth WebSocket not connected");
    }
  };
const generateBRF = () => {
  if (!nemethOutput) {
    alert("Nemeth output is empty");
    return;
  }

  const brfSocket = new WebSocket("ws://192.168.137.1:8000/brf/ws/brf");

  brfSocket.onopen = () => {
    console.log("✅ BRF WebSocket connected");
    brfSocket.send(JSON.stringify({ nemeth: nemethOutput }));
  };

  brfSocket.onmessage = async (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log("📩 BRF Message:", data);

      if (data.error) {
        alert("❌ Error: " + data.error);
        return;
      }

      const { base64, filename } = data;
      const fileUri = FileSystem.documentDirectory + filename;

      await FileSystem.writeAsStringAsync(fileUri, base64, {
        encoding: FileSystem.EncodingType.Base64,
      });

      alert("✅ BRF file saved. Now choose where to share/save it...");

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(fileUri);
      } else {
        alert("Sharing not available on this device.");
      }

    } catch (e) {
      console.error("❌ Error handling BRF response:", e);
      alert("Something went wrong with the BRF file");
    } finally {
      brfSocket.close();
    }
  };

  brfSocket.onerror = (e) => {
    console.error("❌ BRF WebSocket error", e.message);
    alert("WebSocket error occurred");
  };
};


  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <Pressable style={styles.logo} onPress={() => router.back()}>
          <FontAwesome name="angle-left" size={70} color="#000" />
        </Pressable>

        <Text style={styles.title}>Image to LaTeX</Text>
        <Pressable onPress={() => setDarkMode(!darkMode)}>
          <FontAwesome
            name={darkMode ? "moon-o" : "sun-o"}
            size={50}
            color="#000"
          />
        </Pressable>
      </View>

      <View style={styles.mainV}>
        {!imageUri && (
          <Pressable onPress={pickImage} style={styles.dashedBox}>
            <FontAwesome name="plus" size={90} color="#fff" />
            <Text style={styles.buttonText}>Select from gallery</Text>
          </Pressable>
        )}

        {imageUri && (
          <>
            <Pressable onPress={pickImage}>
              <Image
                source={{ uri: imageUri }}
                style={styles.image}
                resizeMode="contain"
              />
            </Pressable>
          </>
        )}

        {!loading && latexOutput !== "" && (
          <View style={{ width: "100%", paddingHorizontal: 20 }}>
            <Pressable
              onPress={copyLatexToClipboard}
              style={[styles.outputBox, { paddingVertical: 8 }]}
            >
              <KaTeXView latex={latexOutput} darkMode={theme} />
            </Pressable>

            {nemethOutput !== "" && (
              <View style={[styles.outputBox, { marginTop: 20 }]}>
                <Text style={styles.sectionTitle}>Nemeth Render:</Text>
                <LiveKaTeXView value={nemethOutput} />
              </View>
            )}

            <Pressable
              onPress={
                nemethOutput
                  ? () => {
                      setImageUri(null);
                      setLatexOutput("");
                      setNemethOutput("");
                    }
                  : convertToNemeth
              }
              style={[
                styles.actionButton,
                nemethOutput && {
                  backgroundColor: "#DC2626", // Tailwind red-600
                  borderColor: "#B91C1C", // Tailwind red-700
                },
              ]}
            >
              <Text style={styles.actionText}>
                {nemethOutput ? "Reset" : "Convert to Nemeth"}
              </Text>
            </Pressable>
            {nemethOutput !== "" && (
              <Pressable onPress={generateBRF} style={styles.actionButton}>
                <Text style={styles.actionText}>Generate BRF</Text>
              </Pressable>
            )}
          </View>
        )}
      </View>
    </ScrollView>
  );
}
