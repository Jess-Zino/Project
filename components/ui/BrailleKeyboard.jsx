import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons'; // For backspace icon

const braillePatterns = Array.from({ length: 64 }, (_, i) => ({
  id: i.toString(),
  unicode: String.fromCharCode(0x2800 + i),
}));

const numColumns = 8;
const cellSize = Dimensions.get('window').width / numColumns;

export default function BrailleKeyboard({ onSelect }) {
  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.key} onPress={() => onSelect(item.unicode)}>
      <Text style={styles.braille}>{item.unicode}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.keyboardContainer}>
      <FlatList
        data={braillePatterns}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        numColumns={numColumns}
        scrollEnabled={false}
      />

      {/* Custom row for Space, Enter, and Backspace */}
      <View style={styles.controlsRow}>
        <TouchableOpacity
          style={[styles.controlKey, { flex: 1 }]}
          onPress={() => onSelect('\n')}
        >
          <Text style={styles.controlText}>↵</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.controlKey, { flex: 2 }]}
          onPress={() => onSelect(' ')}
        >
          <Text style={styles.controlText}>Space</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.controlKey, { flex: 1 }]}
          onPress={() => onSelect('backspace')}
        >
          <Ionicons name="backspace-outline" size={24} color="#fff" />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  keyboardContainer: {
    position: 'absolute',
    bottom: 0,
    width: '100%',
    backgroundColor: '#1a1a1a',
    borderTopWidth: 1,
    borderColor: '#333',
    paddingVertical: 8,
    justifyContent: 'center',
    alignItems: 'center',
  
  },
  key: {
    width: cellSize - 10,
    height: cellSize - 10,
    margin: 2,
    backgroundColor: '#333',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  braille: {
    fontSize: 50,
    color: '#fff',
  },
  controlsRow: {
    flexDirection: 'row',
    marginTop: 10,
    marginHorizontal: 10,
    justifyContent: 'space-between',
  },
  controlKey: {
    backgroundColor: '#444',
    borderRadius: 8,
    paddingVertical: 12,
    marginHorizontal: 5,
    alignItems: 'center',
    justifyContent: 'center',
  },
  controlText: {
    color: '#fff',
    fontSize: 26,
  },
});
