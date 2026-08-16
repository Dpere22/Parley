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
        <form
            onSubmit={handleSubmit}
            className="parchment parchment-curl border-2 border-oak-dark rounded-sm shadow-xl p-5 space-y-3"
        >
            <h2 className="heading text-lg text-center">Call a New Council</h2>
            <hr className="rule-gilt" />
            <div className="flex gap-3">
                <label htmlFor="chatName" className="sr-only">chat name</label>
                <input
                    id="chatName"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="name thy council..."
                    autoComplete="off"
                    className="field-ink px-3 py-2 flex-1"
                />
                <button
                    type="submit"
                    disabled={!name.trim()}
                    className={`btn-seal px-5 py-2 text-sm uppercase ${name.trim() ? "cursor-pointer" : ""}`}
                >
                    Proclaim
                </button>
            </div>
            {errorMsg && <p className="text-sm text-crimson-light italic">{errorMsg}</p>}
        </form>
    );
}
