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

const queryClient = new QueryClient();

function NotFound() {
  return (
    <div className="hall min-h-screen flex flex-col items-center justify-center px-4">
      <h1 className="font-script text-6xl text-gilt-light">404</h1>
      <hr className="rule-gilt w-72 my-6" />
      <p className="heading text-lg text-parchment/80 text-center">
        No such road exists in this realm
      </p>
    </div>
  );
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
    <div className={"flex hall min-h-screen"}>
      <div className={"w-1/4 min-w-0 border-r-2 border-oak-dark"}>
        <NavList />
      </div>
      <div className={"w-3/4 min-w-0 flex flex-col items-center justify-center px-6"}>
        <h1 className="font-script text-5xl text-gilt-light text-center">Parley</h1>
        <hr className="rule-gilt w-80 my-6" />
        <p className="heading text-sm uppercase tracking-widest text-parchment/70 text-center">
          Choose a council, or seek one in the Great Hall
        </p>
      </div>
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
