import { Tabs } from "expo-router";

export default function AbasLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#6200ee",
        tabBarStyle: { backgroundColor: "#fff" },
      }}
    >
      <Tabs.Screen
        name="home"
        options= {{showHeader: false, title: "Home" }}
      />
      <Tabs.Screen
        name="financeiro"
        options={{ showHeader: false, title: "Financeiro" }}
      />
      <Tabs.Screen
        name="perfil"
        options={{ title: "Perfil" }}
      />
    </Tabs>
  );
}