// app/(abas)/Info.js

import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  RefreshControl,
  Alert,
  Modal,
} from 'react-native';
import { apiFetch } from '../../App/api';

export default function Info() {
  const [abaSelecionada, setAbaSelecionada] = useState('transacoes'); // 'transacoes' ou 'metas'

  const [transacoes, setTransacoes] = useState([]);
  const [metas, setMetas] = useState([]);

  const [carregando, setCarregando] = useState(true);
  const [atualizando, setAtualizando] = useState(false);
  const [erro, setErro] = useState(null);

  // controle dos modais de adicionar
  const [modalTransacao, setModalTransacao] = useState(false);
  const [modalMeta, setModalMeta] = useState(false);

  // campos do formulário de transação
  const [txDescricao, setTxDescricao] = useState('');
  const [txValor, setTxValor] = useState('');
  const [txTipo, setTxTipo] = useState('despesa'); // 'receita' ou 'despesa'

  // campos do formulário de meta
  const [metaDescricao, setMetaDescricao] = useState('');
  const [metaValor, setMetaValor] = useState('');

  // ═══════════════════════════════════════════════════
  // BUSCAR DADOS
  // ═══════════════════════════════════════════════════

  const buscarDados = useCallback(async () => {
    try {
      setErro(null);
      const [resTransacoes, resMetas] = await Promise.all([
        apiFetch('backend/routes/api/transacoes'),
        apiFetch('backend/routes/api/metas'),
      ]);
      setTransacoes(resTransacoes.transacoes ?? []);
      setMetas(resMetas.metas ?? []);
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
  // ADICIONAR TRANSAÇÃO
  // ═══════════════════════════════════════════════════

  const adicionarTransacao = async () => {
    if (!txDescricao || !txValor) {
      Alert.alert('Atenção', 'Preencha descrição e valor.');
      return;
    }

    try {
      await apiFetch(`/api/transacoes/${txTipo}`, {
        method: 'POST',
        body: JSON.stringify({
          descricao: txDescricao,
          valor: parseFloat(txValor),
        }),
      });

      setTxDescricao('');
      setTxValor('');
      setTxTipo('despesa');
      setModalTransacao(false);
      buscarDados();
    } catch (e) {
      Alert.alert('Erro', e.message);
    }
  };

  // ═══════════════════════════════════════════════════
  // DELETAR TRANSAÇÃO
  // ═══════════════════════════════════════════════════

  const deletarTransacao = (id) => {
    Alert.alert(
      'Confirmar',
      'Deseja mover essa transação para a lixeira?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Descartar',
          style: 'destructive',
          onPress: async () => {
            try {
              await apiFetch(`/api/transacoes/${id}/descartar`, { method: 'POST' });
              buscarDados();
            } catch (e) {
              Alert.alert('Erro', e.message);
            }
          },
        },
      ]
    );
  };

  // ═══════════════════════════════════════════════════
  // ADICIONAR META
  // ═══════════════════════════════════════════════════

  const adicionarMeta = async () => {
    if (!metaDescricao || !metaValor) {
      Alert.alert('Atenção', 'Preencha descrição e valor alvo.');
      return;
    }

    try {
      await apiFetch('/api/metas', {
        method: 'POST',
        body: JSON.stringify({
          descricao: metaDescricao,
          valor_alvo: parseFloat(metaValor),
        }),
      });

      setMetaDescricao('');
      setMetaValor('');
      setModalMeta(false);
      buscarDados();
    } catch (e) {
      Alert.alert('Erro', e.message);
    }
  };

  // ═══════════════════════════════════════════════════
  // DELETAR META
  // ═══════════════════════════════════════════════════

  const deletarMeta = (id) => {
    Alert.alert(
      'Confirmar',
      'Deseja deletar essa meta?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Deletar',
          style: 'destructive',
          onPress: async () => {
            try {
              await apiFetch(`/api/metas/${id}/deletar`, { method: 'POST' });
              buscarDados();
            } catch (e) {
              Alert.alert('Erro', e.message);
            }
          },
        },
      ]
    );
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
    <View style={styles.container}>

      {/* Seletor de aba */}
      <View style={styles.seletor}>
        <TouchableOpacity
          style={[styles.aba, abaSelecionada === 'transacoes' && styles.abaSelecionada]}
          onPress={() => setAbaSelecionada('transacoes')}
        >
          <Text style={[styles.abaTexto, abaSelecionada === 'transacoes' && styles.abaTextoSelecionado]}>
            Transações
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.aba, abaSelecionada === 'metas' && styles.abaSelecionada]}
          onPress={() => setAbaSelecionada('metas')}
        >
          <Text style={[styles.abaTexto, abaSelecionada === 'metas' && styles.abaTextoSelecionado]}>
            Metas
          </Text>
        </TouchableOpacity>
      </View>

      {/* Lista */}
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={atualizando} onRefresh={aoAtualizar} tintColor="#6200ee" />
        }
      >
        {/* ── TRANSAÇÕES ── */}
        {abaSelecionada === 'transacoes' && (
          <View style={styles.lista}>
            {transacoes.length === 0 && (
              <Text style={styles.vazio}>Nenhuma transação ainda.</Text>
            )}
            {transacoes.map((t) => (
              <View key={t.id} style={styles.cartao}>
                <View style={styles.cartaoEsquerda}>
                  <Text style={styles.cartaoDescricao}>{t.descricao}</Text>
                  <Text style={styles.cartaoCategoria}>{t.categoria} · {t.data}</Text>
                </View>
                <View style={styles.cartaoDireita}>
                  <Text style={[
                    styles.cartaoValor,
                    t.tipo === 'receita' ? styles.receita : styles.despesa,
                  ]}>
                    {t.tipo === 'receita' ? '+' : '-'} R$ {Number(t.valor).toFixed(2)}
                  </Text>
                  <TouchableOpacity onPress={() => deletarTransacao(t.id)}>
                    <Text style={styles.botaoDeletar}>🗑</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* ── METAS ── */}
        {abaSelecionada === 'metas' && (
          <View style={styles.lista}>
            {metas.length === 0 && (
              <Text style={styles.vazio}>Nenhuma meta ainda.</Text>
            )}
            {metas.map((m) => (
              <View key={m.id} style={styles.cartao}>
                <View style={styles.cartaoConteudo}>
                  <View style={styles.cartaoTopo}>
                    <Text style={styles.cartaoDescricao}>{m.descricao}</Text>
                    <TouchableOpacity onPress={() => deletarMeta(m.id)}>
                      <Text style={styles.botaoDeletar}>🗑</Text>
                    </TouchableOpacity>
                  </View>
                  <Text style={styles.cartaoCategoria}>
                    R$ {Number(m.valor_acumulado).toFixed(2)} de R$ {Number(m.valor_alvo).toFixed(2)}
                  </Text>
                  {/* Barra de progresso */}
                  <View style={styles.barraFundo}>
                    <View style={[styles.barraProgresso, { width: `${Math.min(m.progresso, 100)}%` }]} />
                  </View>
                  <Text style={styles.progressoTexto}>{m.progresso}%</Text>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Botão flutuante de adicionar */}
      <TouchableOpacity
        style={styles.fab}
        onPress={() => abaSelecionada === 'transacoes' ? setModalTransacao(true) : setModalMeta(true)}
      >
        <Text style={styles.fabTexto}>+</Text>
      </TouchableOpacity>

      {/* ── MODAL TRANSAÇÃO ── */}
      <Modal visible={modalTransacao} transparent animationType="slide">
        <View style={styles.modalFundo}>
          <View style={styles.modalCaixa}>
            <Text style={styles.modalTitulo}>Nova Transação</Text>

            {/* Tipo */}
            <View style={styles.seletorTipo}>
              <TouchableOpacity
                style={[styles.tipoBotao, txTipo === 'despesa' && styles.tipoBotaoSelecionado]}
                onPress={() => setTxTipo('despesa')}
              >
                <Text style={styles.tipoBotaoTexto}>📉 Despesa</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.tipoBotao, txTipo === 'receita' && styles.tipoBotaoSelecionado]}
                onPress={() => setTxTipo('receita')}
              >
                <Text style={styles.tipoBotaoTexto}>📈 Receita</Text>
              </TouchableOpacity>
            </View>

            <TextInput
              style={styles.input}
              placeholder="Descrição"
              value={txDescricao}
              onChangeText={setTxDescricao}
            />
            <TextInput
              style={styles.input}
              placeholder="Valor (ex: 150.00)"
              keyboardType="numeric"
              value={txValor}
              onChangeText={setTxValor}
            />

            <View style={styles.modalBotoes}>
              <TouchableOpacity style={styles.botaoCancelar} onPress={() => setModalTransacao(false)}>
                <Text style={styles.botaoCancelarTexto}>Cancelar</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.botaoConfirmar} onPress={adicionarTransacao}>
                <Text style={styles.botaoConfirmarTexto}>Adicionar</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* ── MODAL META ── */}
      <Modal visible={modalMeta} transparent animationType="slide">
        <View style={styles.modalFundo}>
          <View style={styles.modalCaixa}>
            <Text style={styles.modalTitulo}>Nova Meta</Text>

            <TextInput
              style={styles.input}
              placeholder="Descrição (ex: Viagem)"
              value={metaDescricao}
              onChangeText={setMetaDescricao}
            />
            <TextInput
              style={styles.input}
              placeholder="Valor alvo (ex: 2000.00)"
              keyboardType="numeric"
              value={metaValor}
              onChangeText={setMetaValor}
            />

            <View style={styles.modalBotoes}>
              <TouchableOpacity style={styles.botaoCancelar} onPress={() => setModalMeta(false)}>
                <Text style={styles.botaoCancelarTexto}>Cancelar</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.botaoConfirmar} onPress={adicionarMeta}>
                <Text style={styles.botaoConfirmarTexto}>Adicionar</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  centro: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 16 },
  erroTexto: { color: '#c62828', fontSize: 15, textAlign: 'center', paddingHorizontal: 32 },
  botaoTentar: { backgroundColor: '#6200ee', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
  botaoTentarTexto: { color: '#fff', fontWeight: 'bold' },

  seletor: { flexDirection: 'row', backgroundColor: '#fff', elevation: 2 },
  aba: { flex: 1, paddingVertical: 14, alignItems: 'center' },
  abaSelecionada: { borderBottomWidth: 2, borderBottomColor: '#6200ee' },
  abaTexto: { fontSize: 15, color: '#888' },
  abaTextoSelecionado: { color: '#6200ee', fontWeight: 'bold' },

  lista: { padding: 16, gap: 12 },
  vazio: { textAlign: 'center', color: '#aaa', marginTop: 40, fontSize: 15 },

  cartao: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cartaoConteudo: { flex: 1 },
  cartaoTopo: { flexDirection: 'row', justifyContent: 'space-between' },
  cartaoEsquerda: { flex: 1 },
  cartaoDireita: { alignItems: 'flex-end', gap: 8 },
  cartaoDescricao: { fontSize: 15, fontWeight: 'bold', color: '#333' },
  cartaoCategoria: { fontSize: 12, color: '#aaa', marginTop: 4 },
  cartaoValor: { fontSize: 16, fontWeight: 'bold' },
  receita: { color: '#2e7d32' },
  despesa: { color: '#c62828' },
  botaoDeletar: { fontSize: 18 },

  barraFundo: { height: 6, backgroundColor: '#eee', borderRadius: 4, marginTop: 8 },
  barraProgresso: { height: 6, backgroundColor: '#6200ee', borderRadius: 4 },
  progressoTexto: { fontSize: 11, color: '#888', marginTop: 4 },

  fab: {
    position: 'absolute',
    right: 20,
    bottom: 24,
    backgroundColor: '#6200ee',
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 6,
  },
  fabTexto: { color: '#fff', fontSize: 28, lineHeight: 32 },

  modalFundo: { flex: 1, backgroundColor: '#00000066', justifyContent: 'flex-end' },
  modalCaixa: { backgroundColor: '#fff', borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24, gap: 12 },
  modalTitulo: { fontSize: 18, fontWeight: 'bold', color: '#333', marginBottom: 4 },

  seletorTipo: { flexDirection: 'row', gap: 10 },
  tipoBotao: { flex: 1, padding: 10, borderRadius: 8, borderWidth: 1, borderColor: '#ddd', alignItems: 'center' },
  tipoBotaoSelecionado: { borderColor: '#6200ee', backgroundColor: '#f3e5ff' },
  tipoBotaoTexto: { fontSize: 14 },

  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 10,
    padding: 14,
    fontSize: 15,
    color: '#333',
  },

  modalBotoes: { flexDirection: 'row', gap: 10, marginTop: 4 },
  botaoCancelar: { flex: 1, padding: 14, borderRadius: 10, borderWidth: 1, borderColor: '#ddd', alignItems: 'center' },
  botaoCancelarTexto: { color: '#888', fontWeight: 'bold' },
  botaoConfirmar: { flex: 1, padding: 14, borderRadius: 10, backgroundColor: '#6200ee', alignItems: 'center' },
  botaoConfirmarTexto: { color: '#fff', fontWeight: 'bold' },
});