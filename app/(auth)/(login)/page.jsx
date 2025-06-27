import React, { useState } from "react";
import { TextInput, View, Text, StyleSheet, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { Colors } from "../../../constants/Colors";
import { FontAwesome, MaterialIcons, Feather } from "@expo/vector-icons";
import {
  GestureHandlerRootView,
  PanGestureHandler,
} from "react-native-gesture-handler";
import * as SecureStore from "expo-secure-store";
import * as LocalAuthentication from "expo-local-authentication";
import * as Speech from "expo-speech";

const Login = () => {
  const router = useRouter();
  const [username, setusername] = useState("");
  const [password, setPassword] = useState("");
  const [pin, setPin] = useState("");
  const [selectedOption, setSelectedOption] = useState("pin");
  const [darkMode, setDarkMode] = useState(true);
  const hasSpokenWelcome = React.useRef(false);
  const hasAnnouncedOption = React.useRef(false);

  const theme = darkMode ? Colors.dark : Colors.light;
  const options = [
    { id: "pin", label: "PIN", icon: "dialpad" },
    { id: "password", label: "Password", icon: "lock" },
  ];

  const handleGesture = (event) => {
    if (event.nativeEvent.translationX < -50) {
      setSelectedOption("pin");
    } else if (event.nativeEvent.translationX > 50) {
      setSelectedOption("password");
    }
  };

  const socketRef = React.useRef(null);

  React.useEffect(() => {
    socketRef.current = new WebSocket("ws://192.168.137.1:8000/auth/ws/login");

    socketRef.current.onopen = () => {
      console.log("WebSocket connected ✅");
    };

    socketRef.current.onclose = () => {
      console.log("WebSocket disconnected ❌");
    };

    return () => {
      socketRef.current.close();
    };
  }, []);
  const handleLogin = () => {
    const loginPayload = {
      type: "login",
      username,
      method: selectedOption,
      password: selectedOption === "password" ? password : undefined,
      pin: selectedOption === "pin" ? pin : undefined, // assuming pin and password share state
    };

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(loginPayload));
    } else {
      alert("Unable to connect to server.");
    }
  };

  // Optional: Handle messages
  React.useEffect(() => {
    if (!socketRef.current) return;

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data);

      if (data.status === "success") {
        SecureStore.setItemAsync("username", data.user.username);
        SecureStore.setItemAsync("userToken", data.token);
        setusername("");
        setPin("");
        setPassword("");
        alert("Login Successful");
        router.navigate("/(home)/page");
      } else {
        alert(data.message || "Login failed ❌");
      }
    };
  }, [username, password, pin]);
  React.useEffect(() => {
    const timeout = setTimeout(() => {
      Speech.speak("Login page opened. Please select a login method. Pin login selected. swipe left or right to change the options", {
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
        ? "PIN login selected"
        : "Password login selected";

    // Speak only if it hasn't been auto-spoken after login welcome, or user changed selection
    if (!hasAnnouncedOption.current || selectedOption) {
      hasAnnouncedOption.current = true;
      Speech.speak(message, { rate: 0.9 });
    }
  }, [selectedOption]);

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      justifyContent: "space-around",
      alignItems: "center",
      padding: 30,
      paddingTop: 30,
    },
    logo: {
      marginBottom: 20,
      position: "absolute",
      top: 5,
      left: 20,
      padding: 10,
      borderRadius: 20,
    },
    backButton: {
      position: "absolute",
      top: 25,
      right: 30,
      borderRadius: 20,
    },
    toggleButton: {
      position: "absolute",
      top: 40,
      right: 20,
      padding: 10,
      borderRadius: 20,
    },
    optionsContainer: {
      flexDirection: "row",
      flexWrap: "wrap", // Enables wrapping to the next line
      justifyContent: "center", // Centers items horizontally
      alignItems: "center", // Aligns items vertically
      marginTop: 50,
      width: "100%",
    },

    option: {
      width: "45%", // Adjusted to fit two items per row
      paddingVertical: 45,

      borderRadius: 10,
      margin: 5, // Added margin to prevent overlap
      alignItems: "center", // Centers text inside
      justifyContent: "center",
    },
    optionText: {
      fontSize: 29,
      color: "#00",
      fontFamily: "PoppinsBlack",
    },
    label: {
      fontSize: 25,
      marginBottom: 8,
      fontFamily: "PoppinsMedium",
    },
    input: {
      height: 90,
      borderWidth: 3,
      borderRadius: 10,
      paddingHorizontal: 10,
      marginBottom: 30,
      fontSize: 25,
      fontFamily: "PoppinsMedium",
    },

    output: {
      marginTop: 20,
      fontSize: 27,
      fontWeight: "bold",
    },
    button: {
      padding: 35,
      borderRadius: 10,
      marginTop: 20,
      alignItems: "center",
      width: 200,
    },
    buttonText: {
      color: "#FFFFFF",
      fontSize: 29,
      fontWeight: "600",
      fontFamily: "PoppinsBold",
    },
    logbutton: {
      borderWidth: 3,
      borderColor: theme == "dark" ? theme.btnBorder : theme.tint,

      padding: 25,
      backgroundColor: theme.tint,
      borderRadius: 10,
      width: "90%",
      alignItems: "center",
      marginVertical: 10,
    },
  });
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <PanGestureHandler onGestureEvent={handleGesture}>
        <View style={[styles.container, { backgroundColor: theme.background }]}>
          <Pressable style={styles.logo} onPress={() => router.back()}>
            <FontAwesome
              name="angle-left" // Use FontAwesome icon names
              size={60}
              color={theme.text}
            />
          </Pressable>
          <Pressable
            style={styles.logo}
            onPress={() => router.navigate("/(SplashScreen)")}
            accessibilityLabel="Go back"
            accessibilityRole="button"
            accessible
          >
            <FontAwesome
              name="angle-left"
              size={60}
              color={theme.text}
              accessibilityElementsHidden // hides from screen reader since the Pressable already describes the button
            />
          </Pressable>
          <Pressable
            style={styles.toggleButton}
            onPress={() => setDarkMode(!darkMode)}
            accessible={true}
            accessibilityLabel="Toggle dark or light mode"
            accessibilityHint="Double tap to switch between dark and light mode"
            accessibilityRole="button"
          >
            <Feather
              name={darkMode ? "sun" : "moon"}
              size={60}
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

          <View style={{ width: "90%" }}>
            <Text style={[styles.label, { color: theme.text }]}>Username:</Text>
            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: theme.background,
                  color: theme.text,
                  borderColor: theme.tint,
                },
              ]}
              placeholder="Enter your username..."
              placeholderTextColor={theme.placeholder}
              value={username}
              onChangeText={setusername}
              autoComplete="username"
            />

            {selectedOption === "password" && (
              <>
                <Text style={[styles.label, { color: theme.text }]}>
                  Password:
                </Text>
                <TextInput
                  style={[
                    styles.input,
                    {
                      backgroundColor: theme.background,
                      color: theme.text,
                      borderColor: theme.tint,
                    },
                  ]}
                  placeholder="Enter your password..."
                  placeholderTextColor={theme.placeholder}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  autoComplete="password"
                />
              </>
            )}

            {selectedOption === "pin" && (
              <>
                <Text style={[styles.label, { color: theme.text }]}>Pin:</Text>
                <TextInput
                  style={[
                    styles.input,
                    {
                      backgroundColor: theme.background,
                      color: theme.text,
                      borderColor: theme.tint,
                    },
                  ]}
                  placeholder="Enter your pin"
                  placeholderTextColor={theme.placeholder}
                  keyboardType="numeric"
                  onChangeText={setPin}
                  maxLength={6}
                  secureTextEntry
                  value={pin}
                />
              </>
            )}
          </View>

          <Pressable style={styles.logbutton} onPress={() => handleLogin()}>
            <Text style={[styles.buttonText, { color: "#000" }]}>Login</Text>
          </Pressable>
        </View>
      </PanGestureHandler>
    </GestureHandlerRootView>
  );
};

export default Login;
