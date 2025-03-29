import { NavLink } from "react-router"
import {useChats} from "./queries.js"
import PropTypes from "prop-types"

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


export default function ChatList(){
    const { chats } = useChats();

    return (
        <div>
            <div className={"flex justify-center bg-pink-800 pb-2"}>
                <NavLink to={'/chats'} className={"text-xl text-white"}>Pony Express</NavLink>
            </div>
            <ul>
                {chats.map((chat) => (
                    <ChatItem key={chat.id} {...chat} />
                ))}
            </ul>
        </div>
    )
}