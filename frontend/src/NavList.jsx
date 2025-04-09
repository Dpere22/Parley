import {NavLink, useNavigate} from "react-router"
import {useAccount, useChats} from "./queries.js"
import PropTypes from "prop-types"
import {useAuth} from "./hooks.js";

ChatItem.propTypes = {
    id: PropTypes.number,
    name: PropTypes.string,
};

function ChatItem({id, name}){
    return (
        <NavLink
            to={`/chats/${id}`}
            className={({ isActive }) =>
                `block p-4 border-b last:border-none ${
                    isActive ? 'bg-pink-300 text-white' : 'bg-white text-black hover:bg-gray-100'
                }`
            }
        >
            {name}
        </NavLink>
    );
}


export default function NavList(){
    const { chats } = useChats();
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
                <NavLink to={'/chats'} className={"text-xl text-white"}>Pony Express</NavLink>
            </div>
            <h1 className={"bg-gray-400 text-center text-xl font-bold pt-2 pb-2 border-b border-b-black"}>{account.username}</h1>
            <ul>
                <li>
                    <NavLink to={`/settings`} className={({ isActive }) =>
                        `block p-4 border-b last:border-none ${
                            isActive ? 'bg-pink-300 text-white' : 'bg-white text-black hover:bg-gray-100'
                        }`
                    }>
                        Settings
                    </NavLink>
                </li>
                <li>
                    <button
                        onClick={handleLogout}
                        className="block w-full p-4 border-b last:border-none text-left bg-white text-black hover:bg-gray-100"
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
        </div>
    )
}