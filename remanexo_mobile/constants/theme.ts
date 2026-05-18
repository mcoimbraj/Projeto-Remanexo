import { DefaultTheme, DarkTheme as NavDark } from '@react-navigation/native';
import { greenPalette } from './colors';

export const LightTheme = {
  ...DefaultTheme,
  dark: false,
  colors: {
    ...DefaultTheme.colors,
    primary: greenPalette.primary,
    background: greenPalette.backgroundLight,
    card: greenPalette.cardLight,
    text: greenPalette.textLight,
    border: greenPalette.borderLight,
  },
};

export const DarkTheme = {
  ...NavDark,
  dark: true,
  colors: {
    ...NavDark.colors,
    primary: greenPalette.primaryLight,
    background: greenPalette.backgroundDark,
    card: greenPalette.cardDark,
    text: greenPalette.textDark,
    border: greenPalette.borderDark,
  },
};