import { Link } from "react-router"
import {useChats} from "./queries.js"
import PropTypes from "prop-types"

ChatItem.propTypes = {
    id: PropTypes.number,
    name: PropTypes.string,
};

function ChatItem({id, name}){
    let link = <Link to={`/chats/${id}`}>{name}</Link>
    if (id === -1){
        link = <p>{name}</p>
    }

    return <li className="hover:bg-green-600"> {link} </li>
}


export default function ChatList(){
    const { chats } = useChats();

    return (
        <ul className= "max-h-96 overflow-y-scroll">
            {chats.map((chat) => (
                <ChatItem key={chat.id} {...chat} />
            ))}
        </ul>
    )
}