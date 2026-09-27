/**
 * Wire types, mirroring the pydantic models in `backend/models.py`.
 *
 * If these drift far enough to become a maintenance burden, generate them from
 * the OpenAPI document FastAPI already serves rather than widening them by hand.
 */

export interface Metadata {
  count: number;
}

export interface Account {
  id: number;
  username: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface Chat {
  id: number;
  name: string;
  owner_id: number;
}

export interface Message {
  id: number;
  text: string;
  /** null once the author leaves the chat or deletes their account */
  account_id: number | null;
  chat_id: number;
  created_at: string;
}

export interface ChatMembership {
  chat_id: number;
  account_id: number;
}

export interface AccessToken {
  access_token: string;
  token_type: string;
}

export interface Accounts {
  metadata: Metadata;
  accounts: Account[];
}

export interface Chats {
  metadata: Metadata;
  chats: Chat[];
}

export interface ChatMessages {
  metadata: Metadata;
  messages: Message[];
}

export interface ChatAccounts {
  metadata: Metadata;
  accounts: Account[];
}

/** The body shape produced by `Err` in `backend/exceptions.py`. */
export interface ApiErrorBody {
  error: string;
  message: string;
}
