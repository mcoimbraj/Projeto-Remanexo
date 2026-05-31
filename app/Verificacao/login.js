//Realizar as funções de login, como autenticação e redirecionamento para a página principal após o login bem-sucedido. Deve se comunicar com o backend para verificar as credenciais do usuário e armazenar o token de autenticação para futuras requisições.
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useRouter } from 'expo-router';
import { API_URL } from '../api'; 

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState(null);
  const [carregando, setCarregando] = useState(false);

  const fazerLogin = async () => {
    if (!email || !senha) {
      setErro('Preencha email e senha.');
      return;
    }

    setCarregando(true);
    setErro(null);

    try {
      const resposta = await fetch(`${API_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha }),
      });

      const json = await resposta.json();

      if (!resposta.ok) {
        setErro(json.erro ?? 'Erro ao fazer login.');
        return;
      }

      await AsyncStorage.setItem('usuario', JSON.stringify(json.usuario));
      router.replace('/abas/home');
    } catch (e) {
      setErro('Não foi possível conectar ao servidor.');
    } finally {
      setCarregando(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.caixa}>
        <Text style={styles.titulo}>Remanexo</Text>
        <Text style={styles.subtitulo}>Faça login para continuar</Text>

        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor="#aaa"
          keyboardType="email-address"
          autoCapitalize="none"
          value={email}
          onChangeText={setEmail}
        />

        <TextInput
          style={styles.input}
          placeholder="Senha"
          placeholderTextColor="#aaa"
          secureTextEntry
          value={senha}
          onChangeText={setSenha}
        />

        {erro && <Text style={styles.erro}>{erro}</Text>}

        <TouchableOpacity
          style={[styles.botao, carregando && styles.botaoDesabilitado]}
          onPress={fazerLogin}
          disabled={carregando}
        >
          {carregando
            ? <ActivityIndicator color="#fff" />
            : <Text style={styles.botaoTexto}>Entrar</Text>
          }
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#6200ee',
    justifyContent: 'center',
    padding: 24,
  },
  caixa: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 28,
    elevation: 6,
  },
  titulo: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#6200ee',
    textAlign: 'center',
  },
  subtitulo: {
    fontSize: 14,
    color: '#888',
    textAlign: 'center',
    marginBottom: 24,
    marginTop: 4,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 10,
    padding: 14,
    marginBottom: 14,
    fontSize: 15,
    color: '#333',
  },
  erro: {
    color: '#e53935',
    fontSize: 13,
    marginBottom: 10,
    textAlign: 'center',
  },
  botao: {
    backgroundColor: '#6200ee',
    borderRadius: 10,
    padding: 16,
    alignItems: 'center',
    marginTop: 4,
  },
  botaoDesabilitado: { opacity: 0.6 },
  botaoTexto: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});