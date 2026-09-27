import { useContext } from 'react';
import { AuthContext, type AuthContextValue } from './context';

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  // Throwing here means every caller gets a non-nullable value without checking.
  if (context === null) {
    throw new Error("useAuth must be used inside an AuthProvider");
  }
  return context;
};
