import React, { useState } from "react";
import { View, Button, Alert, ActivityIndicator, Linking } from "react-native";

const SERVER_URL = "ws://your-server-address/ws/brf"; // change this to your actual server URL
const API_HOST = "http://your-server-address";        // for download links

const GenerateBRFButton = ({ nemethUnicode, token }) => {
  const [loading, setLoading] = useState(false);

  const handleGenerateBRF = () => {
    setLoading(true);

    const ws = new WebSocket(`${SERVER_URL}?token=${token}`);

    ws.onopen = () => {
      console.log("WebSocket connected");
      ws.send(JSON.stringify({ nemeth: nemethUnicode }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.error) {
          Alert.alert("Error", data.error);
        } else if (data.download_url) {
          const fullURL = API_HOST + data.download_url;
          Alert.alert("BRF Ready", "Click to download/view", [
            { text: "Download", onPress: () => Linking.openURL(fullURL) },
            { text: "Cancel", style: "cancel" },
          ]);
        } else {
          Alert.alert("Unexpected Response", JSON.stringify(data));
        }
      } catch (err) {
        Alert.alert("Parse Error", err.message);
      } finally {
        setLoading(false);
        ws.close();
      }
    };

    ws.onerror = (e) => {
      console.error("WebSocket error", e.message);
      Alert.alert("WebSocket Error", e.message);
      setLoading(false);
    };

    ws.onclose = () => {
      console.log("WebSocket closed");
    };
  };

  return (
    <View style={{ marginVertical: 10 }}>
      {loading ? (
        <ActivityIndicator size="small" color="#007AFF" />
      ) : (
        <Button title="Generate BRF" onPress={handleGenerateBRF} />
      )}
    </View>
  );
};

export default GenerateBRFButton;
