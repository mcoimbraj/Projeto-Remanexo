import { useEffect, useState } from "react";
import { View, ActivityIndicator } from "react-native";

import AsyncStorage from "@react-native-async-storage/async-storage";

import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import Login from "./screens/Login";
import Home from "./screens/Home";

const Stack = createNativeStackNavigator();

export default function App() {

  const [loading, setLoading] = useState(true);
  const [userToken, setUserToken] = useState(null);

  useEffect(() => {
    checkLogin();
  }, []);

  async function checkLogin() {

    try {

      const token = await AsyncStorage.getItem("token");

      setUserToken(token);

    } catch (err) {

      console.log(err);

      setUserToken(null);
    }

    setLoading(false);
  }

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
    <NavigationContainer>

      <Stack.Navigator>

        {userToken ? (

          // 🔥 usuário logado
          <Stack.Screen
            name="Home"
            component={Home}
            options={{ headerShown: false }}
          />

        ) : (

          // 🔥 usuário NÃO logado
          <Stack.Screen
            name="Login"
            component={Login}
            options={{ headerShown: false }}
          />

        )}

      </Stack.Navigator>

    </NavigationContainer>
  );
}