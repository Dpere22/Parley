import {BrowserRouter, Routes, Route, useParams} from "react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ChatList from "./ChatList.jsx";
import MessageList from "./Chat.jsx";

const headerClassName = "text-center text-4xl font-extrabold py-4";

const queryClient = new QueryClient();

function NotFound() {
  return <h1 className={headerClassName}>404: Not Found</h1>;
}

function Home() {
  return (
      <div>
        <h1 className={headerClassName}>Pony Express</h1>
      </div>
  );
}

function Chats(){
    return (
        <ChatList />
    )
}

function Chat(){
    const {id}= useParams();
    return (
        <MessageList chat_id={id}/>
    )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="*" element={<NotFound />} />
            <Route path={"/chats/"} element={<Chats />} />
            <Route path={"/chats/:id"} element={<Chat />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
