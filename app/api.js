import AsyncStorage from '@react-native-async-storage/async-storage';

export const API_URL = 'http://10.0.2.2:5000'; // emulador
// export const API_URL = 'http://192.168.18.11:5000'; // celular físico

export async function apiFetch(rota, opcoes = {}) {
  const usuarioStr = await AsyncStorage.getItem('usuario');
  const usuario = usuarioStr ? JSON.parse(usuarioStr) : null;

  const headers = {
    'Content-Type': 'application/json',
    ...(usuario ? { 'X-Usuario-ID': String(usuario.id) } : {}),
    ...(opcoes.headers ?? {}),
  };

  const resposta = await fetch(`${API_URL}${rota}`, {
    ...opcoes,
    headers,
  });

  const json = await resposta.json();

  if (!resposta.ok) {
    throw new Error(json.erro ?? 'Erro desconhecido');
  }

  return json;
}