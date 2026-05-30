import { View, Text, StyleSheet, ScrollView } from "react-native";

export default function Home() {
  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Remanexo</Text>
      <Text style={styles.subtitle}>
        Seu controle financeiro pessoal
      </Text>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Saldo Atual</Text>
        <Text style={styles.value}>R$ 0,00</Text>
      </View>

      <View style={styles.row}>
        <View style={styles.smallCard}>
          <Text style={styles.label}>Receitas</Text>
          <Text style={styles.income}>R$ 0,00</Text>
        </View>

        <View style={styles.smallCard}>
          <Text style={styles.label}>Despesas</Text>
          <Text style={styles.expense}>R$ 0,00</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Próximas Funções</Text>

        <Text style={styles.item}>• Cadastro de despesas</Text>
        <Text style={styles.item}>• Cadastro de receitas</Text>
        <Text style={styles.item}>• Metas financeiras</Text>
        <Text style={styles.item}>• Relatórios mensais</Text>
        <Text style={styles.item}>• Gráficos de gastos</Text>
        <Text style={styles.item}>• Exportação de dados</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Últimas Movimentações</Text>
        <Text style={styles.placeholder}>
          Nenhuma movimentação cadastrada.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F6FA",
    padding: 20,
  },

  title: {
    fontSize: 30,
    fontWeight: "bold",
    marginTop: 20,
  },

  subtitle: {
    color: "#666",
    marginBottom: 20,
  },

  card: {
    backgroundColor: "#FFF",
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
  },

  cardTitle: {
    color: "#666",
    marginBottom: 8,
  },

  value: {
    fontSize: 32,
    fontWeight: "bold",
  },

  row: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 15,
  },

  smallCard: {
    flex: 1,
    backgroundColor: "#FFF",
    padding: 15,
    borderRadius: 12,
  },

  label: {
    color: "#666",
  },

  income: {
    marginTop: 5,
    fontSize: 18,
    fontWeight: "bold",
  },

  expense: {
    marginTop: 5,
    fontSize: 18,
    fontWeight: "bold",
  },

  section: {
    backgroundColor: "#FFF",
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 10,
  },

  item: {
    marginBottom: 8,
  },

  placeholder: {
    color: "#888",
    fontStyle: "italic",
  },
});