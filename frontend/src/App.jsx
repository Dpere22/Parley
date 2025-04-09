import {BrowserRouter, Routes, Route} from "react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import NavList from "./NavList.jsx";
import AuthProvider from "./providers/AuthProvider.jsx";
import {useAuth} from "./hooks.js";
import Profile from "./accounts/Profile.jsx";
import RegisterPage from "./accounts/RegisterPage.jsx";
import { Navigate } from "react-router"
import LoginPage from "./accounts/Login.jsx";
import Chat from "./Chat.jsx";

const headerClassName = "text-center text-4xl font-extrabold py-4";

const queryClient = new QueryClient();

function NotFound() {
  return <h1 className={headerClassName}>404: Not Found</h1>;
}

function Home() {
    const {loggedIn} = useAuth();

    if(!loggedIn){
        return <LoginPage />;
    }

    else{
        return <Navigate to={"/chats"} />
    }

}

function Chats(){
    const { loggedIn } = useAuth();

    if (!loggedIn) {
        return <Navigate to="/" />;
    }
    return (
        <div className = {"w-1/4"}>
            <NavList />
        </div>
    )
}


function App() {
  return (
    <QueryClientProvider client={queryClient}>
        <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
            <Route path={"/login"} element={<LoginPage />}/>
            <Route path={"/register"} element={<RegisterPage />}/>
            <Route path={"/settings"} element={<Profile />}/>
          <Route path="*" element={<NotFound />} />
            <Route path={"/chats"} element={<Chats />} />
            <Route path={"/chats/:id"} element={<Chat />} />
        </Routes>
      </BrowserRouter>
        </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
