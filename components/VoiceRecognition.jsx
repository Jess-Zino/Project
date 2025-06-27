import React, { useState } from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import * as Speech from 'expo-speech';

const VoiceRecognition = ({ theme }) => {
  const [recognizedText, setRecognizedText] = useState('');
  const [isListening, setIsListening] = useState(false);

  const startListening = async () => {
    setRecognizedText('');
    setIsListening(true);
    Speech.speak('Please speak now', {
      language: 'en-US',
      rate: 1.0,
      onDone: () => {
        setTimeout(() => {
          setIsListening(false);
        }, 10000); // 10 seconds timeout
      },
    });
  };

  const stopListening = () => {
    setIsListening(false);
    setRecognizedText('Voice recognition stopped');
  };

  return (
    <View style={styles.container}>
      <Text style={[styles.label, { color: theme.text }]}>Voice Login</Text>
      <Text style={[styles.text, { color: theme.text }]}>
        {recognizedText || 'Start speaking...'}
      </Text>

      {isListening ? (
        <Pressable
          style={[styles.button, { backgroundColor: theme.tint }]}
          onPress={stopListening}
        >
          <Text style={styles.buttonText}>Stop Listening</Text>
        </Pressable>
      ) : (
        <Pressable
          style={[styles.button, { backgroundColor: theme.tint }]}
          onPress={startListening}
        >
          <FontAwesome name="microphone" size={24} color={theme.btnColor} />
          <Text style={styles.buttonText}>Start Listening</Text>
        </Pressable>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  label: {
    fontSize: 25,
    marginBottom: 10,
    fontFamily: 'PoppinsMedium',
  },
  text: {
    fontSize: 20,
    marginBottom: 20,
    textAlign: 'center',
    fontFamily: 'PoppinsMedium',
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderRadius: 10,
    marginTop: 20,
    width: 200,
    justifyContent: 'center',
    borderWidth: 3,
  },
  buttonText: {
    marginLeft: 10,
    fontSize: 18,
    fontFamily: 'PoppinsBold',
    color: '#FFFFFF',
  },
});

export default VoiceRecognition;