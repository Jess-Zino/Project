import { useEffect, useRef, useState } from "react";
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  FlatList,
  Modal,
  Pressable,
  Platform,
} from "react-native";
import * as SecureStore from "expo-secure-store";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { FontAwesome } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";

import LiveKaTeXView from "@/components/ui/LiveKatexVieiw";
import { Colors } from "../../../constants/Colors";

const ImageToLatex = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [history, setHistory] = useState([]);
  const [selectedEquation, setSelectedEquation] = useState(null);

  const router = useRouter();
  const theme = darkMode ? Colors.dark : Colors.light;

  const loadHistory = async () => {
    const token = await SecureStore.getItemAsync("userToken");
    if (!token) return;

    const ws = new WebSocket(`ws://192.168.137.1:8000/history/ws/history?token=${token}`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.history) {
        setHistory(data.history);
      }
    };
    ws.onerror = (e) => console.error("WebSocket error:", e.message);
    ws.onclose = () => console.log("WebSocket closed");
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => setSelectedEquation(item)}
    >
      <LiveKaTeXView value={item.latex || "\\text{No LaTeX}"} />
      <Text style={styles.timestamp}>{new Date(item.timestamp).toLocaleString()}</Text>
    </TouchableOpacity>
  );

  return (
    <GestureHandlerRootView style={[styles.container, { backgroundColor: theme.background }]}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()}>
          <FontAwesome name="angle-left" size={50} color="#000" />
        </Pressable>

        <Text style={styles.title}>Equation History</Text>

        <Pressable onPress={() => setDarkMode(!darkMode)}>
          <FontAwesome name={darkMode ? "moon-o" : "sun-o"} size={40} color="#000" />
        </Pressable>
      </View>

      <SafeAreaView style={{ flex: 1 }}>
        <FlatList
          data={history}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ padding: 16 }}
          ListEmptyComponent={
            <Text style={{ color: theme.text, textAlign: "center", marginTop: 20 }}>
              No equations found.
            </Text>
          }
        />
      </SafeAreaView>

      <Modal
        visible={!!selectedEquation}
        transparent
        animationType="slide"
        onRequestClose={() => setSelectedEquation(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: theme.card }]}>
            <Text style={styles.modalTitle}>LaTeX</Text>
            <LiveKaTeXView value={selectedEquation?.latex || ""} />

            <Text style={styles.modalTitle}>Nemeth</Text>
            <Text style={[styles.nemethText, { color: theme.text }]}>
              {selectedEquation?.nemeth || "Not available"}
            </Text>

            <TouchableOpacity onPress={() => setSelectedEquation(null)} style={styles.closeButton}>
              <Text style={styles.closeButtonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    paddingTop: Platform.OS === "ios" ? 50 : 20,
    paddingBottom: 20,
    paddingHorizontal: 20,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#eee",
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  title: {
    fontSize: 24,
    fontFamily: "PoppinsBold",
    color: "#000",
  },
  card: {
    padding: 16,
    backgroundColor: "#f7f7f7",
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  timestamp: {
    fontSize: 12,
    color: "#666",
    marginTop: 8,
    fontFamily: "PoppinsRegular",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "#00000099",
    justifyContent: "center",
    padding: 20,
  },
  modalContent: {
    borderRadius: 16,
    padding: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontFamily: "PoppinsSemiBold",
    marginBottom: 8,
    color: "#000",
  },
  nemethText: {
    fontSize: 16,
    fontFamily: "PoppinsRegular",
    marginBottom: 20,
  },
  closeButton: {
    marginTop: 10,
    padding: 12,
    borderRadius: 8,
    backgroundColor: "#222",
    alignItems: "center",
  },
  closeButtonText: {
    color: "#fff",
    fontFamily: "PoppinsBold",
  },
});

export default ImageToLatex;
