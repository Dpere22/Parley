import { useCallback, useMemo, useState, type ReactNode } from "react";
import { AuthContext } from "../context";
import type { ApiHeaders } from "../api";
import { isTokenExpired } from "../token";

const tokenKey = "chats_access_token";

interface AuthProviderProps {
    children: ReactNode;
}

/** Read the stored token, discarding one that has already expired. */
function readStoredToken(): string | null {
    const stored = localStorage.getItem(tokenKey);
    if (isTokenExpired(stored)) {
        localStorage.removeItem(tokenKey);
        return null;
    }
    return stored;
}

export default function AuthProvider({ children }: AuthProviderProps) {
    // The expiry check runs only here, on what was already in storage. Tokens arriving
    // from login() are trusted as issued, so a client whose clock runs fast cannot end
    // up rejecting its own fresh token and looping back to the login page.
    const [token, setToken] = useState<string | null>(readStoredToken);
    const loggedIn = token !== null;

    // Sending "Bearer null" would be worse than sending nothing at all.
    const headers = useMemo<ApiHeaders>(() => {
        const built: ApiHeaders = {};
        if (token !== null) {
            built.Authorization = `Bearer ${token}`;
        }
        return built;
    }, [token]);

    const login = useCallback((token: string) => {
        setToken(token);
        localStorage.setItem(tokenKey, token);
    }, []);

    const logout = useCallback(() => {
        setToken(null);
        localStorage.removeItem(tokenKey);
    }, []);

    // Stable identity, so consumers depending on logout in an effect do not re-run every render.
    const value = useMemo(
        () => ({ headers, loggedIn, login, logout }),
        [headers, loggedIn, login, logout],
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
