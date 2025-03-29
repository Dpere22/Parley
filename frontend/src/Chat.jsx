import {useChatAccounts, useMessages} from "./queries.js"
import PropTypes from "prop-types"

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
    const username = usernameMap[msg.account_id] || 'unknown';
    const text = msg.text
    return (
        <li>
            <p>{username}</p>
            <p>{text}</p>
        </li>
    )
}

export default function MessageList({chat_id}){
    const { messageList } = useMessages(chat_id);
    const { accounts } = useChatAccounts(chat_id);

    const usernameMap = accounts.reduce((acc, account) => {
        acc[account.id] = account.username;
        return acc;
    }, {});

    return (
        <ul className={"max-h-96 overflow-y-scroll"}>
            {messageList.map((message) => (
                <MessageItem key={message.id} msg={message} usernameMap={usernameMap} />
            ))}
        </ul>
    );
}
