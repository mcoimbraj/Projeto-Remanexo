import { useEffect, useState } from 'react';
import { Redirect } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function Index() {
  const [destino, setDestino] = useState(null);

  useEffect(() => {
    AsyncStorage.getItem('usuario').then((valor) => {
      setDestino(valor ? '/(abas)/home' : '/verificacao/login');
    });
  }, []);

  if (!destino) return null; // aguarda verificação

  return <Redirect href={destino} />;
}