import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useRouter } from 'expo-router';
import { apiFetch } from'../api';

export default function Home() {
  const router = useRouter();
  const [dados, setDados] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [atualizando, setAtualizando] = useState(false);
  const [erro, setErro] = useState(null);

  const buscarDados = useCallback(async () => {
    try {
      setErro(null);
      const json = await apiFetch('/api/dashboard');
      setDados(json);
    } catch (e) {
      setErro(e.message);
    } finally {
      setCarregando(false);
      setAtualizando(false);
    }
  }, []);

  useEffect(() => {
    buscarDados();
  }, []);

  const aoAtualizar = () => {
    setAtualizando(true);
    buscarDados();
  };

  const fazerLogout = async () => {
    await AsyncStorage.removeItem('usuario');
    router.replace('/verificacao/login');
  };

  if (carregando) {
    return (
      <View style={styles.centro}>
        <ActivityIndicator size="large" color="#6200ee" />
      </View>
    );
  }

  if (erro) {
    return (
      <View style={styles.centro}>
        <Text style={styles.erroTexto}>⚠️ {erro}</Text>
        <TouchableOpacity style={styles.botaoTentar} onPress={buscarDados}>
          <Text style={styles.botaoTentarTexto}>Tentar novamente</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={atualizando} onRefresh={aoAtualizar} tintColor="#6200ee" />
      }
    >
      {/* Cabeçalho */}
      <View style={styles.cabecalho}>
        <View>
          <Text style={styles.saudacao}>Olá, {dados?.usuario?.nome ?? 'usuário'} 👋</Text>
          <Text style={styles.subconta}>Conta {dados?.conta?.numero_conta}</Text>
        </View>
        <TouchableOpacity onPress={fazerLogout}>
          <Text style={styles.logout}>Sair</Text>
        </TouchableOpacity>
      </View>

      {/* Saldo */}
      <View style={styles.cartaoSaldo}>
        <Text style={styles.labelSaldo}>Saldo atual</Text>
        <Text style={styles.valorSaldo}>
          R$ {Number(dados?.saldo_total ?? 0).toFixed(2)}
        </Text>
        <Text style={styles.labelPlano}>
          {dados?.assinatura?.tipo === 'premium' ? '⭐ Premium' : '🆓 Gratuito'}
        </Text>
      </View>

      {/* Receitas e Despesas */}
      <View style={styles.fileira}>
        <View style={[styles.cartaoMes, { backgroundColor: '#e8f5e9' }]}>
          <Text style={styles.labelMes}>📈 Receitas</Text>
          <Text style={[styles.valorMes, { color: '#2e7d32' }]}>
            R$ {Number(dados?.receitas_mes ?? 0).toFixed(2)}
          </Text>
        </View>
        <View style={[styles.cartaoMes, { backgroundColor: '#ffebee' }]}>
          <Text style={styles.labelMes}>📉 Despesas</Text>
          <Text style={[styles.valorMes, { color: '#c62828' }]}>
            R$ {Number(dados?.despesas_mes ?? 0).toFixed(2)}
          </Text>
        </View>
      </View>

      {/* Alerta de gasto */}
      {dados?.alerta_gasto && (
        <View style={styles.alerta}>
          <Text style={styles.alertaTexto}>
            ⚠️ Você já gastou {Number(dados.percentual_gasto).toFixed(0)}% da sua receita este mês!
          </Text>
        </View>
      )}

      {/* Status do Nexo */}
      <View style={styles.secao}>
        <Text style={styles.tituloSecao}>Status do Nexo</Text>
        <View style={[styles.nexoBadge, estiloNexo(dados?.nexo?.estado)]}>
          <Text style={styles.nexoTexto}>
            {dados?.nexo?.estado === 'ativo' && '🟢 Ativo — sincronizando normalmente'}
            {dados?.nexo?.estado === 'instavel' && '🟡 Instável — dados em cache local'}
            {dados?.nexo?.estado === 'erro' && '🔴 Erro — sincronização bloqueada'}
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

function estiloNexo(estado) {
  if (estado === 'ativo') return { backgroundColor: '#e8f5e9' };
  if (estado === 'instavel') return { backgroundColor: '#fff8e1' };
  return { backgroundColor: '#ffebee' };
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  centro: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 16 },
  erroTexto: { color: '#c62828', fontSize: 15, textAlign: 'center', paddingHorizontal: 32 },

  botaoTentar: {
    backgroundColor: '#6200ee',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  botaoTentarTexto: { color: '#fff', fontWeight: 'bold' },

  cabecalho: {
    backgroundColor: '#6200ee',
    padding: 24,
    paddingTop: 52,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  saudacao: { color: '#fff', fontSize: 20, fontWeight: 'bold' },
  subconta: { color: '#d1b3ff', fontSize: 12, marginTop: 2 },
  logout: { color: '#d1b3ff', fontSize: 14, marginTop: 4 },

  cartaoSaldo: {
    backgroundColor: '#fff',
    margin: 16,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    elevation: 4,
  },
  labelSaldo: { color: '#888', fontSize: 13 },
  valorSaldo: { color: '#6200ee', fontSize: 38, fontWeight: 'bold', marginTop: 4 },
  labelPlano: { color: '#aaa', fontSize: 12, marginTop: 8 },

  fileira: {
    flexDirection: 'row',
    marginHorizontal: 16,
    gap: 12,
    marginBottom: 16,
  },
  cartaoMes: {
    flex: 1,
    borderRadius: 12,
    padding: 16,
    elevation: 2,
  },
  labelMes: { fontSize: 13, color: '#555' },
  valorMes: { fontSize: 18, fontWeight: 'bold', marginTop: 4 },

  alerta: {
    marginHorizontal: 16,
    marginBottom: 16,
    backgroundColor: '#fff3e0',
    borderRadius: 10,
    padding: 14,
    borderLeftWidth: 4,
    borderLeftColor: '#ff9800',
  },
  alertaTexto: { color: '#e65100', fontSize: 14 },

  secao: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 12,
    padding: 16,
    elevation: 2,
  },
  tituloSecao: { fontSize: 13, color: '#888', marginBottom: 8 },
  nexoBadge: { borderRadius: 8, padding: 12 },
  nexoTexto: { fontSize: 14 },
});