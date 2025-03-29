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
                    isActive ? 'bg-purple-600 text-white' : 'bg-white text-black hover:bg-gray-100'
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
        <ul>
            {chats.map((chat) => (
                <ChatItem key={chat.id} {...chat} />
            ))}
        </ul>
    )
}