import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '@react-navigation/native';
import { ReactNode } from 'react';

export default function GradientBackground({ children }: { children: ReactNode }) {
  const { dark } = useTheme();

  const colors = dark
    ? ['#022c22', '#052e16'] as const
    : ['#dcfce7', '#bbf7d0'] as const;

  return (
    <LinearGradient colors={colors} style={{ flex: 1 }}>
      {children}
    </LinearGradient>
  );
}