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
import * as Clipboard from "expo-clipboard";
import * as SecureStore from "expo-secure-store";
import * as ImagePicker from "expo-image-picker";
import * as FileSystem from "expo-file-system";
import * as Speech from "expo-speech";
import { FontAwesome } from "@expo/vector-icons";
import { useRouter } from "expo-router";

import { Colors } from "../../../constants/Colors";
import KaTeXView from "../../../components/ui/KaTeXView";

export default function InferenceScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [latexOutput, setLatexOutput] = useState("");
  const [imageUri, setImageUri] = useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const wsRef = useRef(null);
  const { width } = useWindowDimensions();
  const theme = darkMode ? Colors.dark : Colors.light;

  const styles = StyleSheet.create({
    container: {
      flexGrow: 1,
      paddingTop: 50,
      alignItems: "center",
      backgroundColor: theme.background,
    },
    header: {
      width: "95%",
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
      padding: 30,
    },
    title: {
      fontSize: 40,
      color: theme.text,
      fontFamily: "PoppinsBold",
    },
    dashedBox: {
      width: width * 0.8,
      height: width * 0.8,
      borderWidth: 5,
      borderColor: "#fff",
      borderStyle: "dashed",
      borderRadius: 10,
      justifyContent: "center",
      alignItems: "center",
      marginVertical: 0,
    },
    image: {
      width: width * 0.8,
      height: width * 0.8,
      borderRadius: 10,
      marginTop: -80,
    },
    buttonText: {
      color: theme.text,
      fontSize: 37,
      fontFamily: "PoppinsBold",
      marginTop: 10,
    },
      backButton: {
      position: "absolute",
      top: 25,
      right: 30,
      borderRadius: 20,
    },
      logo: {
      position: "absolute",
      top: 30,
      left: 20,
      padding: 10,
    },
    mainV: {
      flex: 1,
      alignItems: "center",
      width: "100%",
      justifyContent: "start",
      backgroundColor: theme.background,
    },
    actionButton: {
      width: "100%",
      backgroundColor: theme.tint,
      paddingVertical: 50,
      paddingHorizontal: 100,
      borderRadius: 10,
      marginTop: -50,
    },
    actionText: {
      color: "#000",
      fontSize: 40,
      fontWeight: "bold",
      fontFamily: "PoppinsBold",
    },
  });

  const token = SecureStore.getItem("userToken");

  // WebSocket connection
  useEffect(() => {
    const socket = new WebSocket(
      `ws://192.168.137.1:8000/convert/ws/image-to-latex?token=${token}`
    );

    socket.onopen = () => {
      console.log("✅ WebSocket connected");
      wsRef.current = socket;
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("📩 Message from server:", data);
      setLatexOutput(data.latex);
      Speech.speak(data.spoken_text, {
        language: "en",
        rate: 0.9,
        pitch: 1.0,
      });
    };

    socket.onerror = (error) => {
      console.error("❌ WebSocket error:", error?.message || error);
    };

    socket.onclose = (e) => {
      console.log("🛑 WebSocket closed", e.code, e.reason);
    };

    return () => {
      socket.close();
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
      runModel(uri); // 🚀 Automatically send to backend
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable style={styles.logo} onPress={() => router.back()}>
                    <FontAwesome
                      name="angle-left" // Use FontAwesome icon names
                      size={70}
                      color={theme.text}
                    />
                  </Pressable>
       
        <Text style={styles.title}>Image to LaTeX</Text>
         <Pressable onPress={() => setDarkMode(!darkMode)}>
          <FontAwesome
            name={darkMode ? "moon-o" : "sun-o"}
            size={50}
            color={theme.text}
          />
        </Pressable>
      </View>

      {/* Main Content */}
      <View style={styles.mainV}>
        {/* Dashed Upload Box */}
        {!imageUri && (
          <Pressable onPress={pickImage} style={styles.dashedBox}>
            <FontAwesome name="plus" size={90} color="#fff" />
            <Text style={styles.buttonText}>Select from gallery</Text>
          </Pressable>
        )}

        {/* Image Preview */}
        {imageUri && (
          <>
            {/* 📸 Image pressable for re-pick */}
            <Pressable onPress={pickImage}>
              <Image
                source={{ uri: imageUri }}
                style={styles.image}
                resizeMode="contain"
              />
            </Pressable>

            {/* Convert to Nemeth Button */}
          </>
        )}

        {/* KaTeX Output */}
        {loading && <ActivityIndicator size="large" color={theme.text} />}
        {!loading && latexOutput !== "" && (
          <View style={{ alignItems: "center", marginVertical: 0}}>
            <Pressable onPress={copyLatexToClipboard}>
              <KaTeXView latex={latexOutput} darkMode={theme} />
            </Pressable>
            <Pressable
              onPress={() => runModel(imageUri)}
              style={styles.actionButton}
            >
              <Text style={styles.actionText}>Convert to Nemeth</Text>
            </Pressable>
          </View>
        )}
      </View>
    </ScrollView>
  );
}
