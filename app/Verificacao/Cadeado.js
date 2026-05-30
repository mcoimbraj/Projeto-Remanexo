// app/verificacao/Cadeado.js

import { useEffect } from 'react';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function Cadeado() {
  const router = useRouter();

  useEffect(() => {
    const verificar = async () => {
      const usuarioStr = await AsyncStorage.getItem('usuario');

      if (usuarioStr) {
        router.replace('/(abas)/home'); // já logado → vai pra home
      } else {
        router.replace('/verificacao/login'); // não logado → vai pro login
      }
    };

    verificar();
  }, []);

  return null; // não renderiza nada, só redireciona
}