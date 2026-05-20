import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from "react-native";

export default function Login() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");

  function handleLogin() {
    if (!email || !senha) {
      Alert.alert("Erro", "Preencha todos os campos");
      return;
    }
    
    console.log({
      email,
      senha,
    });

    Alert.alert("Login", "Login realizado!");
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
        >
          <Text style={styles.botaoTexto}>Entrar</Text>
        </TouchableOpacity>

        <View style={styles.divisor} />

        <Text style={styles.cadastroTexto}>
          Sem conta?{" "}
          <Text style={styles.link}>
            Criar nova conta
          </Text>
        </Text>
      </View>

      <View style={styles.demoBox}>
        <Text style={styles.demoTitulo}>
          Testando? Credenciais demo:
        </Text>

        <Text style={styles.demoTexto}>
          E-mail: demo@remanexo.com
        </Text>

        <Text style={styles.demoTexto}>
          Senha: 123456
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
    backgroundColor: "#fff",
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

  demoBox: {
    marginTop: 20,
    backgroundColor: "#e9ecef",
    padding: 16,
    borderRadius: 10,
  },

  demoTitulo: {
    fontWeight: "bold",
    marginBottom: 8,
  },

  demoTexto: {
    color: "#555",
  },
});