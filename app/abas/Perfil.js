// app/(abas)/Perfil.js

import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, ActivityIndicator, Alert, Image, Modal,
  RefreshControl,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import { apiFetch } from '../api';

// ═══════════════════════════════════════════════════
// FRASES MOTIVACIONAIS
// ═══════════════════════════════════════════════════
const FRASES = [
  'Cuide do seu dinheiro hoje para ter liberdade amanhã.',
  'Pequenos gastos evitados hoje são grandes conquistas no futuro.',
  'Investir em você mesmo é o melhor investimento.',
  'O segredo da riqueza está nos hábitos diários.',
  'Quem controla as finanças, controla o futuro.',
  'Economizar não é privação, é escolha inteligente.',
  'Cada real guardado é um passo rumo à independência.',
];

export default function Perfil() {
  const router = useRouter();

  const [usuario, setUsuario] = useState(null);
  const [dadosPerfil, setDadosPerfil] = useState(null);
  const [fotoPerfil, setFotoPerfil] = useState(null);
  const [frase, setFrase] = useState('');
  const [carregando, setCarregando] = useState(true);
  const [atualizando, setAtualizando] = useState(false);
  const [erro, setErro] = useState(null);

  // modais
  const [modalNome, setModalNome] = useState(false);
  const [modalSenha, setModalSenha] = useState(false);

  // campos de edição
  const [novoNome, setNovoNome] = useState('');
  const [senhaAtual, setSenhaAtual] = useState('');
  const [senhaNova, setSenhaNova] = useState('');
  const [senhaConfirma, setSenhaConfirma] = useState('');

  // ═══════════════════════════════════════════════════
  // INICIALIZAÇÃO
  // ═══════════════════════════════════════════════════

  useEffect(() => {
    // sorteia frase motivacional
    setFrase(FRASES[Math.floor(Math.random() * FRASES.length)]);
    carregarFoto();
    carregarUsuario();
  }, []);

  const carregarUsuario = async () => {
    const str = await AsyncStorage.getItem('usuario');
    if (str) setUsuario(JSON.parse(str));
  };

  const carregarFoto = async () => {
    const foto = await AsyncStorage.getItem('foto_perfil');
    if (foto) setFotoPerfil(foto);
  };

  // ═══════════════════════════════════════════════════
  // BUSCAR DADOS DO BACKEND
  // ═══════════════════════════════════════════════════

  const buscarDados = useCallback(async () => {
    try {
      setErro(null);
      const [resDash, resMetas, resTransacoes] = await Promise.all([
        apiFetch('/api/dashboard'),
        apiFetch('/api/metas'),
        apiFetch('/api/transacoes'),
      ]);

      setDadosPerfil({
        saldo: resDash.saldo_total,
        receitas_mes: resDash.receitas_mes,
        despesas_mes: resDash.despesas_mes,
        plano: resDash.assinatura?.tipo ?? 'gratuita',
        nexo: resDash.nexo?.estado ?? 'erro',
        numero_conta: resDash.conta?.numero_conta,
        total_transacoes: resTransacoes.transacoes?.length ?? 0,
        total_metas: resMetas.metas?.length ?? 0,
        metas_ativas: resMetas.metas?.filter(m => m.ativa).length ?? 0,
        metas_concluidas: resMetas.metas?.filter(m => !m.ativa).length ?? 0,
      });

      // atualiza nome no AsyncStorage
      if (resDash.usuario) {
        const usuarioAtualizado = resDash.usuario;
        await AsyncStorage.setItem('usuario', JSON.stringify(usuarioAtualizado));
        setUsuario(usuarioAtualizado);
      }
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

  // ═══════════════════════════════════════════════════
  // FOTO DE PERFIL
  // ═══════════════════════════════════════════════════

  const escolherFoto = async () => {
    const permissao = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permissao.granted) {
      Alert.alert('Permissão negada', 'Precisamos de acesso à galeria para trocar a foto.');
      return;
    }

    const resultado = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.5,
      base64: false,
    });

    if (!resultado.canceled && resultado.assets[0]) {
      const uri = resultado.assets[0].uri;
      setFotoPerfil(uri);
      await AsyncStorage.setItem('foto_perfil', uri);
    }
  };

  const removerFoto = async () => {
    Alert.alert('Remover foto', 'Deseja remover a foto de perfil?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Remover',
        style: 'destructive',
        onPress: async () => {
          setFotoPerfil(null);
          await AsyncStorage.removeItem('foto_perfil');
        },
      },
    ]);
  };

  // ═══════════════════════════════════════════════════
  // EDITAR NOME
  // ═══════════════════════════════════════════════════

  const salvarNome = async () => {
    if (!novoNome || novoNome.trim().length < 3) {
      Alert.alert('Atenção', 'Nome deve ter pelo menos 3 caracteres.');
      return;
    }

    try {
      await apiFetch('/api/perfil/nome', {
        method: 'POST',
        body: JSON.stringify({ nome: novoNome.trim() }),
      });

      const usuarioAtualizado = { ...usuario, nome: novoNome.trim() };
      await AsyncStorage.setItem('usuario', JSON.stringify(usuarioAtualizado));
      setUsuario(usuarioAtualizado);
      setModalNome(false);
      setNovoNome('');
      Alert.alert('✅', 'Nome atualizado com sucesso!');
    } catch (e) {
      Alert.alert('Erro', e.message);
    }
  };

  // ═══════════════════════════════════════════════════
  // ALTERAR SENHA
  // ═══════════════════════════════════════════════════

  const salvarSenha = async () => {
    if (!senhaAtual || !senhaNova || !senhaConfirma) {
      Alert.alert('Atenção', 'Preencha todos os campos.');
      return;
    }
    if (senhaNova !== senhaConfirma) {
      Alert.alert('Atenção', 'As senhas novas não coincidem.');
      return;
    }
    if (senhaNova.length < 6) {
      Alert.alert('Atenção', 'A nova senha deve ter pelo menos 6 caracteres.');
      return;
    }

    try {
      await apiFetch('/api/perfil/senha', {
        method: 'POST',
        body: JSON.stringify({
          senha_atual: senhaAtual,
          senha_nova: senhaNova,
          senha_confirma: senhaConfirma,
        }),
      });

      setModalSenha(false);
      setSenhaAtual('');
      setSenhaNova('');
      setSenhaConfirma('');
      Alert.alert('✅', 'Senha alterada com sucesso!');
    } catch (e) {
      Alert.alert('Erro', e.message);
    }
  };

  // ═══════════════════════════════════════════════════
  // LOGOUT
  // ═══════════════════════════════════════════════════

  const fazerLogout = async () => {
    Alert.alert('Sair', 'Deseja sair da conta?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Sair',
        style: 'destructive',
        onPress: async () => {
          await AsyncStorage.removeItem('usuario');
          router.replace('/verificacao/login');
        },
      },
    ]);
  };

  // ═══════════════════════════════════════════════════
  // RENDER
  // ═══════════════════════════════════════════════════

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
      {/* ── CABEÇALHO ── */}
      <View style={styles.cabecalho}>

        {/* Foto de perfil */}
        <TouchableOpacity onPress={escolherFoto} onLongPress={fotoPerfil ? removerFoto : undefined}>
          <View style={styles.fotoContainer}>
            {fotoPerfil ? (
              <Image source={{ uri: fotoPerfil }} style={styles.foto} />
            ) : (
              <View style={styles.fotoPlaceholder}>
                <Text style={styles.fotoInicial}>
                  {usuario?.nome?.[0]?.toUpperCase() ?? '?'}
                </Text>
              </View>
            )}
            <View style={styles.fotoBadge}>
              <Text style={styles.fotoBadgeTexto}>📷</Text>
            </View>
          </View>
        </TouchableOpacity>

        <Text style={styles.nome}>{usuario?.nome ?? 'Usuário'}</Text>
        <Text style={styles.email}>{usuario?.email ?? ''}</Text>
        <Text style={styles.conta}>#{dadosPerfil?.numero_conta}</Text>

        {/* Badge de plano */}
        <View style={[styles.planoBadge, dadosPerfil?.plano === 'premium' && styles.planoBadgePremium]}>
          <Text style={styles.planoTexto}>
            {dadosPerfil?.plano === 'premium' ? '⭐ Premium' : '🆓 Gratuito'}
          </Text>
        </View>
      </View>

      {/* ── FRASE MOTIVACIONAL ── */}
      <View style={styles.fraseCard}>
        <Text style={styles.fraseIcone}>💡</Text>
        <Text style={styles.fraseTexto}>"{frase}"</Text>
      </View>

      {/* ── RESUMO FINANCEIRO ── */}
      <Text style={styles.secaoTitulo}>Resumo financeiro</Text>
      <View style={styles.grade}>
        <View style={[styles.statCard, { backgroundColor: '#e8f5e9' }]}>
          <Text style={styles.statIcone}>💰</Text>
          <Text style={styles.statValor}>R$ {Number(dadosPerfil?.saldo ?? 0).toFixed(2)}</Text>
          <Text style={styles.statLabel}>Saldo atual</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: '#e3f2fd' }]}>
          <Text style={styles.statIcone}>🔄</Text>
          <Text style={styles.statValor}>{dadosPerfil?.total_transacoes ?? 0}</Text>
          <Text style={styles.statLabel}>Transações</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: '#f3e5f5' }]}>
          <Text style={styles.statIcone}>🎯</Text>
          <Text style={styles.statValor}>{dadosPerfil?.metas_ativas ?? 0}</Text>
          <Text style={styles.statLabel}>Metas ativas</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: '#fff8e1' }]}>
          <Text style={styles.statIcone}>✅</Text>
          <Text style={styles.statValor}>{dadosPerfil?.metas_concluidas ?? 0}</Text>
          <Text style={styles.statLabel}>Metas concluídas</Text>
        </View>
      </View>

      {/* ── NEXO ── */}
      <Text style={styles.secaoTitulo}>Nexo</Text>
      <View style={[styles.nexoCard, estiloNexo(dadosPerfil?.nexo)]}>
        <Text style={styles.nexoTexto}>
          {dadosPerfil?.nexo === 'ativo' && '🟢 Ativo — sincronizando normalmente'}
          {dadosPerfil?.nexo === 'instavel' && '🟡 Instável — dados em cache local'}
          {dadosPerfil?.nexo === 'erro' && '🔴 Erro — sincronização bloqueada'}
        </Text>
      </View>

      {/* ── EDITAR PERFIL ── */}
      <Text style={styles.secaoTitulo}>Editar perfil</Text>
      <View style={styles.secaoCard}>
        <TouchableOpacity
          style={styles.opcao}
          onPress={() => { setNovoNome(usuario?.nome ?? ''); setModalNome(true); }}
        >
          <Text style={styles.opcaoIcone}>✏️</Text>
          <View style={styles.opcaoTextos}>
            <Text style={styles.opcaoTitulo}>Alterar nome</Text>
            <Text style={styles.opcaoSub}>{usuario?.nome}</Text>
          </View>
          <Text style={styles.opcaoSeta}>›</Text>
        </TouchableOpacity>

        <View style={styles.divisor} />

        <TouchableOpacity style={styles.opcao} onPress={() => setModalSenha(true)}>
          <Text style={styles.opcaoIcone}>🔒</Text>
          <View style={styles.opcaoTextos}>
            <Text style={styles.opcaoTitulo}>Alterar senha</Text>
            <Text style={styles.opcaoSub}>••••••••</Text>
          </View>
          <Text style={styles.opcaoSeta}>›</Text>
        </TouchableOpacity>

        <View style={styles.divisor} />

        <TouchableOpacity style={styles.opcao} onPress={escolherFoto}>
          <Text style={styles.opcaoIcone}>📷</Text>
          <View style={styles.opcaoTextos}>
            <Text style={styles.opcaoTitulo}>Trocar foto de perfil</Text>
            <Text style={styles.opcaoSub}>{fotoPerfil ? 'Foto definida' : 'Nenhuma foto'}</Text>
          </View>
          <Text style={styles.opcaoSeta}>›</Text>
        </TouchableOpacity>
      </View>

      {/* ── LOGOUT ── */}
      <TouchableOpacity style={styles.botaoLogout} onPress={fazerLogout}>
        <Text style={styles.botaoLogoutTexto}>Sair da conta</Text>
      </TouchableOpacity>

      <View style={{ height: 32 }} />

      {/* ── MODAL NOME ── */}
      <Modal visible={modalNome} transparent animationType="slide">
        <View style={styles.modalFundo}>
          <View style={styles.modalCaixa}>
            <Text style={styles.modalTitulo}>Alterar nome</Text>
            <TextInput
              style={styles.input}
              placeholder="Novo nome"
              value={novoNome}
              onChangeText={setNovoNome}
              autoFocus
            />
            <View style={styles.modalBotoes}>
              <TouchableOpacity style={styles.botaoCancelar} onPress={() => setModalNome(false)}>
                <Text style={styles.botaoCancelarTexto}>Cancelar</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.botaoConfirmar} onPress={salvarNome}>
                <Text style={styles.botaoConfirmarTexto}>Salvar</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* ── MODAL SENHA ── */}
      <Modal visible={modalSenha} transparent animationType="slide">
        <View style={styles.modalFundo}>
          <View style={styles.modalCaixa}>
            <Text style={styles.modalTitulo}>Alterar senha</Text>
            <TextInput
              style={styles.input}
              placeholder="Senha atual"
              secureTextEntry
              value={senhaAtual}
              onChangeText={setSenhaAtual}
            />
            <TextInput
              style={styles.input}
              placeholder="Nova senha"
              secureTextEntry
              value={senhaNova}
              onChangeText={setSenhaNova}
            />
            <TextInput
              style={styles.input}
              placeholder="Confirmar nova senha"
              secureTextEntry
              value={senhaConfirma}
              onChangeText={setSenhaConfirma}
            />
            <View style={styles.modalBotoes}>
              <TouchableOpacity style={styles.botaoCancelar} onPress={() => setModalSenha(false)}>
                <Text style={styles.botaoCancelarTexto}>Cancelar</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.botaoConfirmar} onPress={salvarSenha}>
                <Text style={styles.botaoConfirmarTexto}>Salvar</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

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
  botaoTentar: { backgroundColor: '#6200ee', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
  botaoTentarTexto: { color: '#fff', fontWeight: 'bold' },

  cabecalho: {
    backgroundColor: '#6200ee',
    paddingTop: 52,
    paddingBottom: 32,
    alignItems: 'center',
    gap: 6,
  },
  fotoContainer: { position: 'relative', marginBottom: 8 },
  foto: { width: 90, height: 90, borderRadius: 45, borderWidth: 3, borderColor: '#fff' },
  fotoPlaceholder: {
    width: 90, height: 90, borderRadius: 45,
    backgroundColor: '#9c4dcc',
    alignItems: 'center', justifyContent: 'center',
    borderWidth: 3, borderColor: '#fff',
  },
  fotoInicial: { color: '#fff', fontSize: 36, fontWeight: 'bold' },
  fotoBadge: {
    position: 'absolute', bottom: 0, right: 0,
    backgroundColor: '#fff', borderRadius: 12,
    width: 24, height: 24, alignItems: 'center', justifyContent: 'center',
  },
  fotoBadgeTexto: { fontSize: 12 },

  nome: { color: '#fff', fontSize: 22, fontWeight: 'bold' },
  email: { color: '#d1b3ff', fontSize: 13 },
  conta: { color: '#b39ddb', fontSize: 12 },

  planoBadge: {
    marginTop: 4,
    backgroundColor: '#7c3aed',
    paddingHorizontal: 14,
    paddingVertical: 4,
    borderRadius: 20,
  },
  planoBadgePremium: { backgroundColor: '#f59e0b' },
  planoTexto: { color: '#fff', fontSize: 13, fontWeight: 'bold' },

  fraseCard: {
    margin: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
    elevation: 2,
    borderLeftWidth: 4,
    borderLeftColor: '#6200ee',
  },
  fraseIcone: { fontSize: 20 },
  fraseTexto: { flex: 1, color: '#555', fontSize: 14, fontStyle: 'italic', lineHeight: 20 },

  secaoTitulo: { fontSize: 13, color: '#888', marginHorizontal: 16, marginBottom: 8, marginTop: 4 },

  grade: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: 16,
    gap: 10,
    marginBottom: 16,
  },
  statCard: {
    width: '47%',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    elevation: 2,
    gap: 4,
  },
  statIcone: { fontSize: 24 },
  statValor: { fontSize: 18, fontWeight: 'bold', color: '#333' },
  statLabel: { fontSize: 12, color: '#888' },

  nexoCard: { marginHorizontal: 16, borderRadius: 12, padding: 14, marginBottom: 16, elevation: 2 },
  nexoTexto: { fontSize: 14 },

  secaoCard: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    borderRadius: 12,
    elevation: 2,
    marginBottom: 16,
  },
  opcao: { flexDirection: 'row', alignItems: 'center', padding: 16, gap: 12 },
  opcaoIcone: { fontSize: 20 },
  opcaoTextos: { flex: 1 },
  opcaoTitulo: { fontSize: 15, color: '#333', fontWeight: '500' },
  opcaoSub: { fontSize: 12, color: '#aaa', marginTop: 2 },
  opcaoSeta: { fontSize: 20, color: '#ccc' },
  divisor: { height: 1, backgroundColor: '#f0f0f0', marginLeft: 52 },

  botaoLogout: {
    marginHorizontal: 16,
    backgroundColor: '#ffebee',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    elevation: 2,
  },
  botaoLogoutTexto: { color: '#c62828', fontWeight: 'bold', fontSize: 15 },

  modalFundo: { flex: 1, backgroundColor: '#00000066', justifyContent: 'flex-end' },
  modalCaixa: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20, borderTopRightRadius: 20,
    padding: 24, gap: 12,
  },
  modalTitulo: { fontSize: 18, fontWeight: 'bold', color: '#333', marginBottom: 4 },
  input: {
    borderWidth: 1, borderColor: '#ddd',
    borderRadius: 10, padding: 14,
    fontSize: 15, color: '#333',
  },
  modalBotoes: { flexDirection: 'row', gap: 10, marginTop: 4 },
  botaoCancelar: {
    flex: 1, padding: 14, borderRadius: 10,
    borderWidth: 1, borderColor: '#ddd', alignItems: 'center',
  },
  botaoCancelarTexto: { color: '#888', fontWeight: 'bold' },
  botaoConfirmar: {
    flex: 1, padding: 14, borderRadius: 10,
    backgroundColor: '#6200ee', alignItems: 'center',
  },
  botaoConfirmarTexto: { color: '#fff', fontWeight: 'bold' },
});