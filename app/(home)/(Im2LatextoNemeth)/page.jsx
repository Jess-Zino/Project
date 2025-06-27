import React, { useState, useEffect, useRef } from "react";
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView, Pressable, Image,
  ActivityIndicator, useWindowDimensions, PanResponder, Alert, Animated
} from "react-native";
import * as ImageManipulator from "expo-image-manipulator";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as FileSystem from "expo-file-system";
import * as Speech from "expo-speech";
import * as Clipboard from "expo-clipboard";
import { FontAwesome } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import * as SecureStore from "expo-secure-store";
import { Colors } from "../../../constants/Colors";
import KaTeXView from "../../../components/ui/KaTeXView";

export default function InferenceScreen() {
  const router = useRouter();
  const [permission, requestPermission] = useCameraPermissions();
  const [cameraReady, setCameraReady] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [latexOutput, setLatexOutput] = useState("");
  const [imageUri, setImageUri] = useState(null);
  const [showCamera, setShowCamera] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [nemeth, setNemeth] = useState("");
  const nemethWsRef = useRef(null);
  const cameraRef = useRef(null);
  const wsRef = useRef(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;

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
      fontSize: 40,
      color: "#000",
      fontFamily: "PoppinsBold",
    },
button: {
  width: "100%",
  paddingVertical: 16,
  paddingHorizontal: 24,
  borderRadius: 14,
  alignItems: "center",
  justifyContent: "center",
  borderWidth: 2,
  backgroundColor: theme.tint,
  elevation: 2,
  shadowColor: "#000",
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.2,
  shadowRadius: 4,
  marginTop: 12,
},
buttonText: {
  color: "#fff",
  fontSize: 20,
  fontFamily: "PoppinsBold",
},
camera: {
  width: "85%",
  height: 480,
  borderRadius: 20,
  borderWidth: 2,
  borderColor: "#ccc",
  marginBottom: 30,
  marginTop: 10,
},

connectionStatus: {
  color: "red",
  marginBottom: 10,
  fontSize: 16,
  fontWeight: "500",
},

outputCard: {
  width: "90%",
  alignItems: "center",
  backgroundColor: "#fff",
  padding: 20,
  borderRadius: 20,
  shadowColor: "#000",
  shadowOffset: { width: 0, height: 3 },
  shadowOpacity: 0.2,
  shadowRadius: 4,
  elevation: 5,
  backgroundColor: theme.card,
},

nemethBox: {
  borderWidth: 2,
  borderColor: "#ccc",
  borderRadius: 10,
  padding: 10,
  width: "100%",
  marginBottom: 20,
  backgroundColor: theme.background,
},

nemethTitle: {
  fontFamily: "PoppinsBold",
  fontSize: 18,
  marginBottom: 5,
  color: theme.text,
},

nemethText: {
  fontFamily: "monospace",
  fontSize: 16,
  color: theme.text,
},

latexBox: {
  width: "100%",
  padding: 12,
  borderRadius: 10,
  borderWidth: 2,
  borderColor: theme.text,
  backgroundColor: theme.background,
  marginBottom: 20,
  alignItems: "center",
},

shutterButton: {
  marginTop: 20,
  backgroundColor: "#000",
  padding: 20,
  borderRadius: 50,
  elevation: 3,
  shadowColor: "#000",
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.25,
  shadowRadius: 3.84,
},

  
    image: {
  width: width * 0.8,
  height: width * 0.8,
  borderRadius: 20,
  marginTop: -130,
  borderWidth: 2,
  borderColor: theme.border,
  shadowColor: "#000",
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.2,
  shadowRadius: 3,
  elevation: 4,
},

    mainV: {
      flex: 1,
      alignItems: "center",
      width: "100%",
      justifyContent: "center",
      backgroundColor: theme.background,
    },
  });

  useEffect(() => {
    if (!permission || !permission.granted) requestPermission();
  }, [permission]);

  useEffect(() => {
    const initWebSocket = async () => {
      const token = await SecureStore.getItemAsync("userToken");
      if (!token) return;

      const socket = new WebSocket(
        `ws://192.168.137.1:8000/convert/ws/image-to-latex?token=${token}`
      );

      socket.onopen = () => {
        wsRef.current = socket;
        setWsConnected(true);
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLatexOutput(data.latex);
        setNemeth(data.nemeth);
        Speech.speak(data.spoken_text, { language: "en", rate: 0.9 });
        setLoading(false);
      };

      socket.onerror = (err) => {
        setWsConnected(false);
      };

      socket.onclose = () => {
        setWsConnected(false);
      };
    };

    initWebSocket();
  }, []);

  useEffect(() => {
    const initNemethSocket = async () => {
      const token = await SecureStore.getItemAsync("userToken");
      if (!token) return;

      const socket = new WebSocket(
        `ws://192.168.137.1:8000/convert/ws/latex-nemeth?token=${token}`
      );

      socket.onopen = () => {
        nemethWsRef.current = socket;
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setNemeth(data.nemeth);
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }).start();
        Speech.speak(data.spoken_text || data.nemeth || "Nemeth output ready", {
          language: "en",
          rate: 0.9,
          pitch: 1.0,
        });
      };
    };

    initNemethSocket();
  }, []);

  const convertLatexToNemeth = () => {
    if (latexOutput && nemethWsRef.current?.readyState === WebSocket.OPEN) {
      nemethWsRef.current.send(JSON.stringify({ latex: latexOutput }));
    } else {
      Alert.alert("Error", "WebSocket not connected or LaTeX is empty");
    }
  };

  const runModel = async (uri) => {
    try {
      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      });

      if (wsRef.current?.readyState === 1) {
        wsRef.current.send(JSON.stringify({ image: base64 }));
        setLoading(true);
      } else {
        setLatexOutput("WebSocket is not connected.");
      }
    } catch (error) {
      setLatexOutput("Error sending image.");
    }
  };

  const takePicture = async () => {
    if (cameraRef.current && cameraReady) {
      const photo = await cameraRef.current.takePictureAsync({
        base64: false,
        quality: 1,
      });

      setImageUri(photo.uri);
      setShowCamera(false);
      await runModel(photo.uri);
    }
  };

  const copyLatex = async () => {
    if (latexOutput) {
      await Clipboard.setStringAsync(latexOutput);
      Alert.alert("Copied", "LaTeX copied to clipboard.");
    }
  };


  const resetAll = () => {
    setImageUri(null);
    setLatexOutput("");
    setNemeth("");
    setShowCamera(true);
    fadeAnim.setValue(0);
    Alert.alert("Reset", "You’re back at the start.");
  };

  const panResponder = PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onPanResponderRelease: (_, gestureState) => {
      if (gestureState.dx > 50) resetAll();
    },
  });

  if (!permission) return <View style={styles.container}><Text>Requesting camera permission...</Text></View>;
  if (!permission.granted) return <View style={styles.container}><Text>No camera access.</Text></View>;
return (
  <ScrollView contentContainerStyle={styles.container} {...panResponder.panHandlers}>
    <View style={styles.header}>
      <Pressable onPress={() => router.back()}>
        <FontAwesome name="angle-left" size={40} color={theme.text} />
      </Pressable>
      <Text style={styles.title}>Camera to LaTeX</Text>
      <Pressable onPress={() => setDarkMode(!darkMode)}>
        <FontAwesome name={darkMode ? "moon-o" : "sun-o"} size={30} color={theme.text} />
      </Pressable>
    </View>

    {!wsConnected && (
      <Text style={styles.connectionStatus}>🔌 Connecting to server...</Text>
    )}

    <View style={styles.mainV}>
      {showCamera ? (
        <CameraView
          ref={cameraRef}
          style={styles.camera}
          onCameraReady={() => setCameraReady(true)}
          facing="back"
          autoFocus="on"
        />
      ) : (
        <>
          {imageUri && (
            <Image source={{ uri: imageUri }} style={styles.image} resizeMode="contain" />
          )}

          {loading && <ActivityIndicator size="large" color={theme.text} />}

          {!loading && latexOutput && (
            <View style={styles.outputCard}>
              {nemeth !== "" && (
                <Animated.View style={[styles.nemethBox, { opacity: fadeAnim }]}>
                  <Text style={styles.nemethTitle}>Nemeth Output:</Text>
                  <Text style={styles.nemethText}>{nemeth}</Text>
                </Animated.View>
              )}

              <Pressable onPress={copyLatex} style={styles.latexBox}>
                <KaTeXView latex={latexOutput} darkMode={theme} />
              </Pressable>

              <TouchableOpacity
                onPress={nemeth ? resetAll : convertLatexToNemeth}
                style={[
                  styles.button,
                  {
                    backgroundColor: nemeth ? "#DC2626" : theme.tint,
                    borderColor: nemeth ? "#B91C1C" : theme.text,
                  },
                ]}
              >
                <Text style={styles.buttonText}>
                  {nemeth ? "🔁 Reset" : "♿ Convert to Nemeth"}
                </Text>
              </TouchableOpacity>
            </View>
          )}
        </>
      )}

      {showCamera && wsConnected && (
        <Pressable onPress={takePicture} style={styles.shutterButton}>
          <FontAwesome name="camera" size={40} color="#fff" />
        </Pressable>
      )}
    </View>
  </ScrollView>
);
}