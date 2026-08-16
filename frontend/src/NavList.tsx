import { NavLink, useNavigate } from "react-router";
import { useAccount, useMyChats } from "./queries";
import { useAuth } from "./hooks";
import type { Chat } from "./types";

const linkClassName = ({ isActive }: { isActive: boolean }) =>
    `block p-4 border-b last:border-none ${
        isActive ? 'bg-pink-300 text-white' : 'bg-white text-black hover:bg-gray-100'
    }`;

function ChatItem({ id, name }: Chat) {
    return (
        <NavLink to={`/chats/${id}`} className={linkClassName}>
            {name}
        </NavLink>
    );
}

export default function NavList() {
    const { chats } = useMyChats();
    const { account } = useAccount();
    const navigate = useNavigate();
    const { logout } = useAuth();

    const handleLogout = () => {
        logout(); // clear token, auth state, etc.
        navigate("/login"); // redirect after logout
    };

    return (
        <div>
            <div className={"flex justify-center bg-pink-800 pb-3 pt-3"}>
                <NavLink to={'/chats'} className={"text-xl text-white font-bold"}>Pony Express</NavLink>
            </div>
            <h1 className={"bg-gray-400 text-center text-xl font-bold pt-2 pb-2 border-b border-b-black"}>{account.username}</h1>
            <ul>
                <li>
                    <NavLink to={`/settings`} className={linkClassName}>
                        Settings
                    </NavLink>
                </li>
                <li>
                    <button
                        onClick={handleLogout}
                        className="block w-full p-4 border-b last:border-none text-left bg-white text-black hover:bg-gray-100 cursor-pointer"
                    >
                        Logout
                    </button>
                </li>
            </ul>
            <h1 className={"bg-gray-400 text-center text-xl font-bold pt-2 pb-2 border-b border-b-black"}>Chats</h1>
            <ul>
                {chats.map((chat) => (
                    <ChatItem key={chat.id} {...chat} />
                ))}
            </ul>
            <NavLink to={'/chats/browse'} className={linkClassName}>
                Browse chats
            </NavLink>
        </div>
    );
}
