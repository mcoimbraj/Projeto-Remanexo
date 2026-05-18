import { View, StyleSheet, ViewStyle } from 'react-native';
import { ReactNode } from 'react';
import { useTheme } from '@react-navigation/native';

type CardProps = {
  children: ReactNode;
  style?: ViewStyle;
};

export default function Card({ children, style }: CardProps) {
  const { colors, dark } = useTheme();

  return (
    <View
      style={[
        styles.card,
        {
          backgroundColor: colors.card,
          borderColor: colors.border,
          shadowColor: dark ? '#000' : '#000',
        },
        style,
      ]}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 16,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
});