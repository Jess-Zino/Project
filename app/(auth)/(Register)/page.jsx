import {
  TextInput,
  View,
  Text,
  StyleSheet,
  Pressable,
  ActivityIndicator,
} from "react-native";
import React, { useState, useEffect, useFocusEffect, useCallback } from "react";
import { FontAwesome, MaterialIcons } from "@expo/vector-icons";
import { Colors } from "../../../constants/Colors";
import {
  GestureHandlerRootView,
  PanGestureHandler,
} from "react-native-gesture-handler";
import { useRouter } from "expo-router";
import { Audio } from "expo-av";
import * as Speech from "expo-speech";

import * as SecureStore from "expo-secure-store";
import { Link } from "expo-router"; // Ensure you're using expo-router

const Register = () => {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [pin, setPin] = useState("");
  const [password, setPassword] = useState("");
  const [sound, setSound] = useState(null);
    const hasSpokenWelcome = React.useRef(false);
    const hasAnnouncedOption = React.useRef(false);
  
  const [socket, setSocket] = useState(null);
  const [error, setError] = useState("");
  const [darkMode, setDarkMode] = useState(true);
  const [selectedOption, setSelectedOption] = useState("password");
  const router = useRouter();

  const theme = darkMode ? Colors.dark : Colors.light;

  const options = [
    { id: "pin", label: "PIN", icon: "dialpad" },
    { id: "password", label: "Password", icon: "lock" },
  ];

  const handleGesture = (event) => {
    if (event.nativeEvent.translationX < -50) {
      setSelectedOption("pin");
      Speech.speak(`You selected pin}`);
    } else if (event.nativeEvent.translationX > 50) {
      setSelectedOption("password");
      Speech.speak(`You selected Password }`);
    }
  };

  const loadCredentials = async () => {
    const savedEmail = await SecureStore.getItemAsync("userEmail");
    const savedUsername = await SecureStore.getItemAsync("userName");

    const savedPassword = await SecureStore.getItemAsync("userPassword");
    if (savedEmail) setEmail(savedEmail);
    if (savedUsername) setUsername(savedUsername);
    if (savedPassword) setPassword(savedPassword);
  };

  useEffect(() => {
    loadCredentials();

    const ws = new WebSocket("ws://192.168.137.1:8000/auth/ws/register");
    ws.onopen = () => console.log("WebSocket connected.");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "register_success") {
        Speech.speak("Registration successful");
        alert("Registration successful!");
        setName("");
        setEmail("");
        setUsername("");
        setPin("");
        setPassword("");
        setError("");
        setLoading(false);
        setTimeout(() => {
    router.replace("/login"); // or router.push("/login") depending on your routing setup
  }, 1000); // 1 second delay
      } else if (data.type === "register_error") {
        setError(data.detail || "Registration failed");
        Speech.speak(data.detail || "Registration failed");
        setLoading(false);
      }
    };
    ws.onerror = (e) => {
      console.error("WebSocket error:", e.message);
      setError("WebSocket error occurred");
      setLoading(false);
    };
    ws.onclose = () => {
      console.log("WebSocket connection closed.");
      setLoading(false);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  const validatePin = (value) => /^(\d{4}|\d{6})$/.test(value);

  const handleRegister = async () => {
    if (!email.trim()) {
      setError("Email is required");
      return;
    }
    if (!username.trim()) {
      setError("Username is required");
      return;
    }
    if (selectedOption === "password") {
      if (password.length < 6) {
        setError("Password must be at least 6 characters long");
        return;
      }
    } else if (selectedOption === "pin") {
      if (!validatePin(pin)) {
        setError("PIN must be 4 or 6 digits long.");
        return;
      }
    }
    setError("");
    setLoading(true);
    const payload = {
      username,
      email,
      password,
      pin,
    };

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(payload));
    } else {
      setError("WebSocket not connected. Please try again later.");
    }
  };
React.useEffect(() => {
    const timeout = setTimeout(() => {
      Speech.speak("Registration page. Please select a Registration method. Password method selected. swipe left or right to change the options", {
        language: "en-US",
        rate: 0.9,
        onDone: () => {
          hasSpokenWelcome.current = true;
          hasAnnouncedOption.current = false; // allow initial option to be spoken
        },
      });
    }, 500);

    return () => clearTimeout(timeout);
  }, []);
  React.useEffect(() => {
    if (!hasSpokenWelcome.current) return;

    // Stop previous speech before speaking the new one
    Speech.stop();

    const message =
      selectedOption === "pin"
        ? "PIN method selected"
        : "Password method selected";

    // Speak only if it hasn't been auto-spoken after login welcome, or user changed selection
    if (!hasAnnouncedOption.current || selectedOption) {
      hasAnnouncedOption.current = true;
      Speech.speak(message, { rate: 0.9 });
    }
  }, [selectedOption]);

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      justifyContent: "space-evenly",
      padding: 30,
      paddingTop: 90,
      backgroundColor: theme.background,
    },
    toggleButton: {
      position: "absolute",
      top: 50,
      right: 30,
      borderRadius: 20,
    },
    label: {
      fontSize: 25,
      marginBottom: 5,
      fontFamily: "PoppinsMedium",
      color: theme.text,
    },
    input: {
      height: 90,
      borderWidth: 3,
      borderRadius: 10,
      paddingHorizontal: 15,
      fontSize: 26,
      fontFamily: "PoppinsMedium",
      backgroundColor: theme.background,
      color: theme.text,
      borderColor: theme.tint,
      marginBottom: 30,
    },

    button: {
      padding: 20,
      borderRadius: 10,
      alignItems: "center",
      width: "100%",
      paddingVertical: 30,
      backgroundColor: theme.tint,
      borderWidth: 3,
      marginTop: 20,
    },
    buttonText: {
      fontSize: 30,
      fontFamily: "PoppinsBold",
      color: theme.btnColor,
    },
    errorText: {
      color: "red",
      fontSize: 16,
      marginBottom: 10,
    },
    optionsContainer: {
      flexDirection: "row",
      justifyContent: "space-around",
      marginBottom: 20,
    },
    option: {
      padding: 15,
      alignItems: "center",
      borderRadius: 10,
      paddingTop: 40,
      width: "45%",
    },
    optionText: {
      fontSize: 28,
      fontFamily: "PoppinsBold",
      marginTop: 8,
    },
    logbutton: {
      padding: 20,
      borderRadius: 10,
      alignItems: "center",
      width: "100%",
      paddingVertical: 25,
      backgroundColor: theme.tint,
      borderWidth: 3,
      marginTop: 20,
    },
    logo: {
      position: "absolute",
      top: 30,
      left: 20,
    },
    pageName: {
      position: "absolute",
      top: 40,
      left: "40%",
      fontSize: 35,
      marginBottom: 5,
      fontFamily: "PoppinsBold",
      color: theme.text,
    },
  });

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <PanGestureHandler onGestureEvent={handleGesture}>
        <View style={styles.container}>
          <Pressable
            style={styles.logo}
            onPress={() => {
              router.navigate("/(SplashScreen)");
            }}
          >
            <FontAwesome name="angle-left" size={70} color={theme.text} />
          </Pressable>
          <Text style={styles.pageName}>Register</Text>
          <Pressable
            style={styles.toggleButton}
            onPress={() => setDarkMode(!darkMode)}
          >
            <FontAwesome
              name={darkMode ? "moon-o" : "sun-o"}
              size={50}
              color={theme.text}
            />
          </Pressable>

          <View style={styles.optionsContainer}>
            {options.map((option) => (
              <Pressable
                key={option.id}
                style={[
                  styles.option,
                  { borderWidth: 3, borderColor: theme.btnBorder },
                  selectedOption === option.id && {
                    backgroundColor: theme.tint,
                    borderColor: theme.tint,
                  },
                ]}
                onPress={() => setSelectedOption(option.id)}
              >
                <MaterialIcons
                  name={option.icon}
                  size={90}
                  color={
                    selectedOption === option.id ? theme.btnColor : theme.text
                  }
                />
                <Text
                  style={[
                    styles.optionText,
                    {
                      color:
                        selectedOption === option.id
                          ? theme.btnColor
                          : theme.text,
                    },
                  ]}
                >
                  {option.label}
                </Text>
              </Pressable>
            ))}
          </View>

          {error ? <Text style={styles.errorText}>{error}</Text> : null}
          <View>
            
            <Text style={styles.label}>Email:</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter your email..."
              placeholderTextColor={theme.placeholder}
              value={email}
              onChangeText={setEmail}
              autoComplete="email"
            />

            <Text style={styles.label}>Username:</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter your Username..."
              placeholderTextColor={theme.placeholder}
              value={username}
              onChangeText={setUsername}
              autoComplete="username"
            />
            {selectedOption === "password" && (
              <View>
                <Text style={styles.label}>Password:</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Enter your password..."
                  placeholderTextColor={theme.placeholder}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  autoComplete="password"
                />
              </View>
            )}

            {selectedOption === "pin" && (
              <View>
                <Text style={styles.label}>Pin:</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Enter your pin"
                  placeholderTextColor={theme.placeholder}
                  keyboardType="numeric"
                  maxLength={6}
                  value={pin}
                  secureTextEntry
                  onChangeText={setPin}
                  autoComplete="pin"

                />
              </View>
            )}
          </View>
          <View>
            <Pressable style={styles.button} onPress={handleRegister}>
              {loading ? (
                <>
                  <ActivityIndicator size="small" color={theme.btnColor} />
                  <Text style={styles.buttonText}> Registering...</Text>
                </>
              ) : (
                <Text style={styles.buttonText}>Register</Text>
              )}
            </Pressable>
          </View>
        </View>
      </PanGestureHandler>
    </GestureHandlerRootView>
  );
};

export default Register;
