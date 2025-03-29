import {useChatAccounts, useMessages} from "./queries.js"
import PropTypes from "prop-types"
import {useEffect, useRef} from "react";

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

export default function MessageList({chat_id}){
    const { messageList } = useMessages(chat_id);
    const { accounts } = useChatAccounts(chat_id);
    const containerRef = useRef(null);
    useEffect(() => {
        if(containerRef.current){
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [messageList]);


    const usernameMap = accounts.reduce((acc, account) => {
        acc[account.id] = account.username;
        return acc;
    }, {});

    return (
        <ul ref={containerRef} className={"h-screen overflow-y-scroll"}>
            {messageList.map((message) => (
                <MessageItem key={message.id} msg={message} usernameMap={usernameMap} />
            ))}
        </ul>
    );
}
