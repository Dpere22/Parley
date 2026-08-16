import { useState, type FormEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import { useAuth } from "../hooks";
import { useAccount } from "../queries";
import api, { type ApiError } from "../api";
import type { Chat } from "../types";

export default function CreateChat() {
    const [name, setName] = useState("");
    const [errorMsg, setErrorMsg] = useState("");
    const { headers } = useAuth();
    const { account } = useAccount();
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    const mutation = useMutation<Chat, ApiError>({
        mutationFn: () => api.post<Chat>("/chats/", headers, { name, owner_id: account.id }),
        onSuccess: (chat) => {
            setName("");
            setErrorMsg("");
            // creating a chat also makes you a member of it
            queryClient.invalidateQueries({ queryKey: ["my-chats"] });
            queryClient.invalidateQueries({ queryKey: ["chats"] });
            navigate(`/chats/${chat.id}`);
        },
        onError: (error) => setErrorMsg(error.message),
    });

    const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!name.trim()) return;
        mutation.mutate();
    };

    return (
        <form onSubmit={handleSubmit} className="border border-black rounded p-4 space-y-2">
            <h2 className="text-lg font-bold">create a chat</h2>
            <div className="flex gap-2">
                <label htmlFor="chatName" className="sr-only">chat name</label>
                <input
                    id="chatName"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="chat name"
                    autoComplete="off"
                    className="border border-gray-400 px-2 py-1 rounded flex-1"
                />
                <button
                    type="submit"
                    disabled={!name.trim()}
                    className={`px-4 py-1 rounded border border-black ${
                        name.trim()
                            ? "bg-pink-300 text-white hover:bg-pink-400 cursor-pointer"
                            : "bg-gray-200 text-gray-500 cursor-not-allowed"
                    }`}
                >
                    Create
                </button>
            </div>
            {errorMsg && <p className="text-sm text-amber-700">{errorMsg}</p>}
        </form>
    );
}
