import { NavLink } from "react-router";
import { useAccount, useMyChats } from "./queries";
import type { Chat } from "./types";

const entryClassName = ({ isActive }: { isActive: boolean }) =>
  `block px-4 py-3 border-b border-oak-dark/40 transition-colors ${isActive
    ? "bg-oak-dark/70 text-parchment-light border-l-4 border-l-gilt"
    : "text-parchment/90 hover:bg-oak-dark/40 hover:text-parchment-light"
  }`;

function ChatItem({ id, name }: Chat) {
  return (
    <li>
      <NavLink to={`/chats/${id}`} className={entryClassName}>
        <span className="heading text-sm">{name}</span>
      </NavLink>
    </li>
  );
}

function SectionHeading({ children }: { children: string }) {
  return (
    <h2 className="heading text-xs uppercase tracking-widest text-gilt-light bg-oak-dark/60 border-y border-gilt/40 px-4 py-2">
      {children}
    </h2>
  );
}

export default function NavList() {
  const { chats } = useMyChats();
  const { account } = useAccount();

  return (
    <nav className="h-screen overflow-y-auto bg-oak/25">
      <div className="banner py-5 px-3 text-center">
        <NavLink to={"/chats"} className="block">
          <span className="carved font-script text-3xl text-gilt-light">
            Parley
          </span>
        </NavLink>
        <p className="carved heading text-[0.6rem] uppercase tracking-[0.3em] text-parchment/75 mt-1">
          Where counsel is taken
        </p>
      </div>

      <div className="px-4 py-3 text-center border-b border-oak-dark/40">
        <p className="heading text-[0.6rem] uppercase tracking-widest text-gilt">Bearing the seal of</p>
        <p className="heading text-lg text-parchment-light">{account.username}</p>
      </div>

      <ul>
        <li>
          <NavLink to={"/settings"} className={entryClassName}>
            <span className="heading text-sm">Chambers</span>
          </NavLink>
        </li>
        <li>
          <NavLink to={"/chats/browse"} className={entryClassName}>
            <span className="heading text-sm">The Great Hall</span>
          </NavLink>
        </li>
      </ul>

      <SectionHeading>Thy Councils</SectionHeading>
      <ul>
        {chats.map((chat) => (
          <ChatItem key={chat.id} {...chat} />
        ))}
      </ul>
    </nav>
  );
}
