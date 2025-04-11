import {useAccount, useChatAccounts, useMessages} from "./queries.js"
import PropTypes from "prop-types"
import {useEffect, useMemo, useRef, useState} from "react";
import {useAuth} from "./hooks.js";
import {Navigate, useParams} from "react-router";
import NavList from "./NavList.jsx";
import {useMutation, useQueryClient} from "@tanstack/react-query";
import api from "./api.js";

MessageItem.propTypes = {
    msg: PropTypes.shape({
        id: PropTypes.number.isRequired,
        text: PropTypes.string.isRequired,
        account_id: PropTypes.number.isRequired,
        chat_id: PropTypes.number.isRequired,
        created_at: PropTypes.string.isRequired,
    }).isRequired,
    usernameMap: PropTypes.object.isRequired,  // Ensure usernameMap is passed as an object
};
function MessageItem({ msg, usernameMap }){
    const username = usernameMap[msg.account_id] || '[removed]';
    const text = msg.text
    const time = new Date(msg.created_at).toLocaleString();
    return (
        <li className={"py-4"}>
            <div className={"flex flex-col  border border-gray-600 p-2 rounded-lg"}>
                <div className={"flex justify-between"}>
                    <div className={"text-pink-950 text-sm"}>
                        {username}
                    </div>
                    <div className={"text-sm"}>
                        {time}
                    </div>
                </div>
                <div>
                    {text}
                </div>
            </div>
        </li>
    )
}

function MessageList({chat_id}){
    const { messageList } = useMessages(chat_id);
    const { account } = useAccount();
    const { accounts } = useChatAccounts(chat_id);
    const containerRef = useRef(null);
    const [sendEnabled, setSendEnabled] = useState(
        false
    )


    useEffect(() => {
        if(containerRef.current){
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [messageList]);

    const usernameMap = useMemo(() => {
        return accounts.reduce((acc, account) => {
            acc[account.id] = account.username;
            return acc;
        }, {});
    }, [accounts]);

    useEffect(() => {
        setSendEnabled(account?.id in usernameMap);
    }, [account?.id, usernameMap]);

    return (
        <div className={"pb-6 flex flex-col h-screen"}>
            <ul ref={containerRef} className={`overflow-y-scroll scroll-smooth h-9/10`}>
                {messageList.map((message) => (
                    <MessageItem key={message.id} msg={message} usernameMap={usernameMap} />
                ))}
            </ul>
            <div className={"h-1/10"}>
                <ChatForm sendEnabled={sendEnabled} chat_id={chat_id} account_id={account.id} />
            </div>
        </div>
    );
}

function ChatForm({ sendEnabled, chat_id, account_id }) {
    const [text, setMessage] = useState("");
    const {headers} = useAuth();
    const queryClient = useQueryClient();

    const mutation = useMutation({
        mutationFn: ({ text, account_id }) =>
            api.post(`/chats/${chat_id}/messages`, headers, { text, account_id }),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ["chats/chatId/messages", chat_id]}).then();
        },
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!text.trim()) return;
        mutation.mutate({text, account_id});
        setMessage("");
    };

    return (
        <form className="p-2" onSubmit={handleSubmit}>
            <label htmlFor="messageInput" className="sr-only">Message</label>
            <div className="flex gap-2">
                <input
                    id="messageInput"
                    onChange={(e) => setMessage(e.target.value)}
                    value={text}
                    placeholder={sendEnabled ? "Type a message..." : "You can't send messages"}
                    disabled={!sendEnabled}
                    autoComplete={"off"}
                    className={`border border-black px-2 py-1 rounded flex-1 ${
                        !sendEnabled ? "bg-gray-200 text-gray-500 cursor-not-allowed" : ""
                    }`}
                />
                <button
                    type="submit"
                    disabled={!sendEnabled || !text.trim()}
                    className={`px-4 py-1 rounded border border-black ${
                        sendEnabled && text.trim()
                            ? "bg-pink-300 text-white hover:bg-gray-800"
                            : "bg-gray-200 text-gray-500 cursor-not-allowed"
                    }`}
                >
                    Send
                </button>
            </div>
        </form>
    );
}

export default function Chat(){
    const { loggedIn } = useAuth();

    if (!loggedIn) {
        return <Navigate to="/" />;
    }
    const {id}= useParams();
    return (
        <div className={"flex"}>
            <div className={"w-1/4 border-r border-gray-300"}>
                <NavList />
            </div>
            <div className={"w-3/4 pr-4 pl-4 bg-white"}>
                <MessageList chat_id={id}/>
            </div>
        </div>
    );
}
