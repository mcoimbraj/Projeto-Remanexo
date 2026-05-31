import { Tabs } from "expo-router";

export default function AbasLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#6200ee",
        tabBarStyle: { backgroundColor: "#fff" },
        headerShown: false, // ← headerShown, não showHeader
      }}
    >
      <Tabs.Screen name="home" options={{ title: "Home" }} />
      <Tabs.Screen name="Info" options={{ title: "Finanças" }} />
      <Tabs.Screen name="Perfil" options={{ title: "Perfil" }} />
    </Tabs>
  );
}