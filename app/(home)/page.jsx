import React, { useState, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  useWindowDimensions,
  FlatList,
} from "react-native";
import { AccessibilityInfo } from "react-native";
import * as SecureStore from "expo-secure-store";

import { Link } from "expo-router";
import { Colors } from "../../constants/Colors";
import { Feather, FontAwesome } from "@expo/vector-icons";
import * as Speech from "expo-speech"; // ✅ new import

const Home = () => {
  const [selectedOption, setSelectedOption] = useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const { width, height } = useWindowDimensions();
  const username = SecureStore.getItem("username");
  // Define slide height (e.g., 70% of screen height)
  const slideHeight = Math.max(height * 0.7, 300);

  // Your options
  const options = [
    {
      id: 1,
      label: "Convert Image to Latex",
      icon: "image",
      description: "Extract equations from uploaded images.",
      page: "/(ImageToLatex)",
    },
   {
      id: 2,
      label: "Camera to Latex",
      icon: "camera",
      description: "Turn your live pictures into Math Equations.",
      page: "/(Im2LatextoNemeth)",
    },
   {
      id: 3,
      label: "Latex to Braille",
      icon: "font",
      description: "Translate written Latex equations into braille.",
      page: "/(LatextoNemeth)",
    },

    


  ];

  const theme = darkMode ? Colors.dark : Colors.light;

  // Audio sound ref
  const currentSound = useRef(null);

  const playAudio = async (audioUrl) => {
    try {
      if (currentSound.current !== null) {
        await currentSound.current.unloadAsync();
        currentSound.current = null;
      }
      const { sound } = await Audio.Sound.createAsync({ uri: audioUrl });
      currentSound.current = sound;
      await sound.playAsync();
    } catch (error) {
      console.error("Error playing audio:", error);
    }
  };
const handleViewableItemsChanged = useRef(({ viewableItems }) => {
  if (viewableItems.length > 0) {
    const currentItem = viewableItems[0].item;

    // Stop any ongoing speech before starting new one
    Speech.stop();

    const speechText = `${currentItem.label}. ${currentItem.description}`;

    Speech.speak(speechText, {
      language: "en-US",
      pitch: 0.8,
      rate: 0.9,
    });

    AccessibilityInfo.announceForAccessibility(speechText);
  }
});



  const viewabilityConfig = {
    itemVisiblePercentThreshold: 50,
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.background,
    },
    header: {
      paddingTop: 90,
      paddingHorizontal: 30,
      alignItems: "center",
    },
    welcomeText: {
      fontSize: 36,
      color: theme.text,
      marginBottom: 10,
      textAlign: "center",
      fontFamily: "PoppinsBold",
    },
    subText: {
      fontSize: 22,
      color: theme.text,
      textAlign: "center",
      marginBottom: 20,
      fontFamily: "PoppinsMedium",
    },
    logo: {
      position: "absolute",
      top: 30,
      left: 20,
      padding: 10,
    },
    toggleButton: {
      position: "absolute",
      top: 30,
      right: 20,
      padding: 10,
    },
    optionContainer: {
      width, // full width container to center content horizontally
      alignItems: "center",
      justifyContent: "center",
      marginBottom: 60,
    },
    optionCard: {
      width: width * 0.75, // still 75% width for nice margin horizontally
      height: slideHeight,
      justifyContent: "center",
      alignItems: "center",
      borderRadius: 20,
      borderWidth: 4,
      padding: 20,
    },
    optionText: {
      fontSize: 45,
      textAlign: "center",
      fontFamily: "PoppinsExtraBold",
      marginTop: 20,
    },
    optionDescription: {
      fontSize: 30,
      textAlign: "center",
      marginTop: 10,
      fontFamily: "PoppinsRegular",
    },
  });

  return (
    <View style={styles.container}>
      {/* Header Section */}
      <View style={styles.header}>
        <Text style={styles.welcomeText}>Welcome back {username} 👋</Text>
        <Text style={styles.subText}>
          Scroll down to explore. Audio will notify you when a new option is in
          view.
        </Text>
      </View>

      {/* Navigation Buttons */}
      <Link href="/(auth)/(login)/page" asChild>
        <Pressable
          style={styles.logo}
          onPress={() => setDarkMode(!darkMode)}
          accessible={true}
          accessibilityLabel="Logout"
          accessibilityHint="Tap to logout"
          accessibilityRole="button"
        >
          <Feather name="log-out" size={60} color={theme.text} />
        </Pressable>
      </Link>
      {/*Need to do this */}
      <Pressable
        style={styles.toggleButton}
        onPress={() => setDarkMode(!darkMode)}
        accessible={true}
        accessibilityLabel="Toggle dark or light mode"
        accessibilityHint="Tap to switch between dark and light mode"
        accessibilityRole="button"
      >
        <Feather
          name={darkMode ? "sun" : "moon"}
          size={60}
          color={theme.text}
        />
      </Pressable>

      {/* FlatList for vertical swipeable options */}
      <FlatList
        data={options}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
        snapToInterval={slideHeight}
        snapToAlignment="start"
        decelerationRate="fast"
        // Add vertical content inset to center first/last items nicely
        contentInset={{
          top: (height - slideHeight) / 2,
          bottom: (height - slideHeight) / 2,
        }}
        onViewableItemsChanged={handleViewableItemsChanged.current}
        viewabilityConfig={viewabilityConfig}
        renderItem={({ item }) => (
          <View
            style={styles.optionContainer}

          >
            <Link href={item.page} asChild>
              <Pressable
                onPress={() => setSelectedOption(item.id)}
                accessibilityRole="button"
                accessibilityLabel={`${item.label}, ${item.description}`}
                accessibilityHint={`Activate to go to ${item.label} page`}
                accessibilityState={{ selected: selectedOption === item.id }}
                accessible={true}
                focusable={true}
              >
                <View
                  style={[
                    styles.optionCard,
                    {
                      backgroundColor:
                        selectedOption === item.id ? theme.tint : "transparent",
                      borderColor: theme.btnBorder,
                    },
                  ]}
                >
                  <FontAwesome
                    name={item.icon}
                    size={200}
                    color={
                      selectedOption === item.id ? theme.btnColor : theme.tint
                    }
                    accessibilityIgnoresInvertColors // useful on iOS dark mode
                    accessible={false} // avoid double reading icon name
                  />
                  <Text
                    style={[
                      styles.optionText,
                      {
                        color:
                          selectedOption === item.id
                            ? theme.btnColor
                            : theme.text,
                      },
                    ]}
                  >
                    {item.label}
                  </Text>
                  <Text
                    style={[styles.optionDescription, { color: theme.text }]}
                  >
                    {item.description}
                  </Text>
                </View>
              </Pressable>
            </Link>
          </View>
        )}
      />
    </View>
  );
};

export default Home;
