import { BrowserRouter, Routes, Route, Navigate } from "react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import NavList from "./NavList";
import AuthProvider from "./providers/AuthProvider";
import { useAuth } from "./hooks";
import Profile from "./accounts/Profile";
import RegisterPage from "./accounts/RegisterPage";
import LoginPage from "./accounts/Login";
import Chat from "./Chat";
import BrowseChats from "./chats/BrowseChats";

const headerClassName = "text-center text-4xl font-extrabold py-4";

const queryClient = new QueryClient();

function NotFound() {
    return <h1 className={headerClassName}>404: Not Found</h1>;
}

/** Sends anonymous visitors to the login page instead of rendering the route. */
function RequireAuth({ children }: { children: ReactNode }) {
    const { loggedIn } = useAuth();

    if (!loggedIn) {
        return <Navigate to="/" />;
    }
    return <>{children}</>;
}

function Home() {
    const { loggedIn } = useAuth();

    if (!loggedIn) {
        return <LoginPage />;
    }
    return <Navigate to={"/chats"} />;
}

function Chats() {
    return (
        <div className={"w-1/4"}>
            <NavList />
        </div>
    );
}

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <BrowserRouter>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path={"/login"} element={<LoginPage />} />
                        <Route path={"/register"} element={<RegisterPage />} />
                        <Route path={"/settings"} element={<RequireAuth><Profile /></RequireAuth>} />
                        <Route path={"/chats"} element={<RequireAuth><Chats /></RequireAuth>} />
                        <Route path={"/chats/browse"} element={<RequireAuth><BrowseChats /></RequireAuth>} />
                        <Route path={"/chats/:id"} element={<RequireAuth><Chat /></RequireAuth>} />
                        <Route path="*" element={<NotFound />} />
                    </Routes>
                </BrowserRouter>
            </AuthProvider>
        </QueryClientProvider>
    );
}

export default App;
