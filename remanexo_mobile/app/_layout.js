import { Stack, useRouter, useSegments } from "expo-router";
import { useEffect, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { View, ActivityIndicator } from "react-native";

export default function Layout() {

  const router = useRouter();
  const segments = useSegments();

  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  // 🔐 checar login ao iniciar app
  useEffect(() => {
    checkUser();
  }, []);

  async function checkUser() {
    const data = await AsyncStorage.getItem("user");

    setUser(data ? JSON.parse(data) : null);
    setLoading(false);
  }

  // 🔁 redirecionamento automático
  useEffect(() => {

    if (loading) return;

    const inAuthGroup = segments[0] === "(auth)";

    // ❌ não logado → manda login
    if (!user && !inAuthGroup) {
      router.replace("/login");
    }

    // ✅ logado → manda home
    if (user && inAuthGroup) {
      router.replace("/home");
    }

  }, [user, loading]);

  if (loading) {
    return (
      <View style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center"
      }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <Stack screenOptions={{ headerShown: false }} />
  );
}