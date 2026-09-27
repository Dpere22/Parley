import { createContext } from 'react';
import type { ApiHeaders } from './api';

export interface AuthContextValue {
  /** Authorization header for the logged in user, spread into api calls. */
  headers: ApiHeaders;
  loggedIn: boolean;
  login: (token: string) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);
