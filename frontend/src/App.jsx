import { BrowserRouter, Routes, Route } from "react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const headerClassName = "text-center text-4xl font-extrabold py-4";

const queryClient = new QueryClient();

function NotFound() {
  return <h1 className={headerClassName}>404: Not Found</h1>;
}

function Home() {
  return <h1 className={headerClassName}>Pony Express</h1>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
