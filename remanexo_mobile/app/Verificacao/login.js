import { useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";

export default function Login({ navigation }) {

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {

    if (!email || !senha) {
      Alert.alert("Erro", "Preencha todos os campos");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch("http://10.0.2.2:5000/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          senha,
        }),
      });

      const data = await response.json();

      setLoading(false);

      if (!response.ok) {
        Alert.alert("Erro", data.erro || "Erro ao fazer login");
        return;
      }

      // 🔐 SALVANDO SESSÃO (ASYNC STORAGE)
      await AsyncStorage.setItem(
        "user",
        JSON.stringify(data.usuario)
      );

      Alert.alert(
        "Sucesso",
        `Bem-vindo ${data.usuario.nome}`
      );

      // 🚀 REDIRECIONA PARA HOME
      navigation.replace("Home");

    } catch (error) {
      setLoading(false);

      console.log(error);

      Alert.alert(
        "Erro",
        "Não foi possível conectar ao servidor"
      );
    }
  }

  return (
    <View style={styles.container}>

      <View style={styles.card}>

        <Text style={styles.titulo}>Remanexo</Text>

        <Text style={styles.subtitulo}>
          Sistema Financeiro com Open Finance Simulado
        </Text>

        <View style={styles.formGroup}>
          <Text style={styles.label}>E-mail</Text>

          <TextInput
            style={styles.input}
            placeholder="seu@email.com"
            keyboardType="email-address"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Senha</Text>

          <TextInput
            style={styles.input}
            placeholder="••••••••"
            secureTextEntry
            value={senha}
            onChangeText={setSenha}
          />
        </View>

        <TouchableOpacity
          style={styles.botao}
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.botaoTexto}>Entrar</Text>
          )}
        </TouchableOpacity>

        <View style={styles.divisor} />

        <Text style={styles.cadastroTexto}>
          Sem conta? <Text style={styles.link}>Criar nova conta</Text>
        </Text>

      </View>
    </View>
  );
}

const styles = StyleSheet.create({

  container: {
    flex: 1,
    backgroundColor: "#f4f4f4",
    justifyContent: "center",
    padding: 20,
  },

  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 24,
    elevation: 3,
  },

  titulo: {
    fontSize: 28,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 8,
  },

  subtitulo: {
    textAlign: "center",
    color: "#666",
    marginBottom: 28,
  },

  formGroup: {
    marginBottom: 18,
  },

  label: {
    marginBottom: 6,
    fontWeight: "600",
  },

  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    padding: 12,
  },

  botao: {
    backgroundColor: "#0d6efd",
    padding: 14,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 10,
  },

  botaoTexto: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },

  divisor: {
    height: 1,
    backgroundColor: "#ddd",
    marginVertical: 24,
  },

  cadastroTexto: {
    textAlign: "center",
    color: "#666",
  },

  link: {
    color: "#0d6efd",
    fontWeight: "bold",
  },
});