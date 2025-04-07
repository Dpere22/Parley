import { useState } from "react";
import PropTypes from "prop-types"
import { AuthContext } from "../context";

const tokenKey = "chats_access_token";

export default function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem(tokenKey));
    const loggedIn = !!token;
    const headers = { Authorization: `Bearer ${token}` };
    const login = (token) => {
        setToken(token);
        localStorage.setItem(tokenKey, token);
    };
    const logout = () => {
        setToken(null);
        localStorage.removeItem(tokenKey);
    };

    return(
        <AuthContext.Provider value={{headers, loggedIn, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
}

AuthProvider.propTypes = {
    children: PropTypes.node,
};