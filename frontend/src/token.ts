/**
 * Minimal reading of our own access token.
 *
 * This is a convenience check so the app does not present itself as logged in while
 * holding a token the server will reject. It is not a security boundary - the payload
 * is read without verifying the signature, and the server remains the only authority
 * on whether a token is good.
 */

interface JwtPayload {
  exp?: number;
}

function decodePayload(token: string): JwtPayload | null {
  const segment = token.split(".")[1];
  if (segment === undefined) {
    return null;
  }
  try {
    // base64url -> base64, then restore the padding atob insists on
    const base64 = segment.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");
    return JSON.parse(atob(padded)) as JwtPayload;
  } catch {
    return null;
  }
}

/** True for a token that is past its expiry, malformed, or absent. */
export function isTokenExpired(token: string | null): boolean {
  if (token === null) {
    return true;
  }
  const payload = decodePayload(token);
  if (payload?.exp === undefined) {
    // unreadable: treat as expired rather than trusting it
    return true;
  }
  return payload.exp * 1000 <= Date.now();
}
