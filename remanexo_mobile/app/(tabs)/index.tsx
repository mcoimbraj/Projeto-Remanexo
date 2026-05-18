import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '@react-navigation/native';
import GradientBackground from '@/components/ui/GradientBackground';
import Card from '@/components/cards';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    opacity: 0.7,
    marginBottom: 8,
  },
  value: {
    fontSize: 20,
    fontWeight: 'bold',
  },
});

export default function App() {
  const { colors } = useTheme();

  return (
    <GradientBackground>
      <View style={styles.container}>
        
        {/* HEADER */}
        <Text style={[styles.title, { color: colors.text }]}>
          💰 Dashboard
        </Text>

        {/* SALDO */}
        <Card>
          <Text style={styles.label}>Saldo Total</Text>
          <Text style={styles.value}>R$ 12.450,00</Text>
        </Card>

        {/* RECEITAS */}
        <Card>
          <Text style={styles.label}>Receitas</Text>
          <Text style={[styles.value, { color: '#22c55e' }]}>
            + R$ 5.200,00
          </Text>
        </Card>

        {/* DESPESAS */}
        <Card>
          <Text style={styles.label}>Despesas</Text>
          <Text style={[styles.value, { color: '#ef4444' }]}>
            - R$ 2.100,00
          </Text>
        </Card>

        {/* RESUMO */}
        <Card>
          <Text style={styles.label}>Resumo do mês</Text>
          <Text style={{ color: colors.text }}>
            Você economizou mais do que gastou 👍
          </Text>
        </Card>

      </View>
    </GradientBackground>
  );
}