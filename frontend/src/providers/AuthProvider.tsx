import { useState, type ReactNode } from "react";
import { AuthContext } from "../context";

const tokenKey = "chats_access_token";

interface AuthProviderProps {
    children: ReactNode;
}

export default function AuthProvider({ children }: AuthProviderProps) {
    const [token, setToken] = useState<string | null>(() => localStorage.getItem(tokenKey));
    const loggedIn = !!token;
    const headers = { Authorization: `Bearer ${token}` };

    const login = (token: string) => {
        setToken(token);
        localStorage.setItem(tokenKey, token);
    };

    const logout = () => {
        setToken(null);
        localStorage.removeItem(tokenKey);
    };

    return (
        <AuthContext.Provider value={{ headers, loggedIn, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}
