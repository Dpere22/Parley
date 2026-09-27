import type { ApiErrorBody } from "./types";

export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, { error, message }: ApiErrorBody) {
    super(message);
    this.status = status;
    this.code = error;
  }
}

/**
 * Every error code the API uses to mean "your token will not do".
 * Mirrors the exceptions in `backend/exceptions.py`.
 */
const authErrorCodes = new Set([
  "authentication_required",
  "expired_access_token",
  "invalid_access_token",
]);

/** True when the server rejected the request because of the token, not the request. */
export const isAuthError = (error: unknown): boolean =>
  error instanceof ApiError && authErrorCodes.has(error.code);

/** Auth headers as produced by `useAuth()`. */
export type ApiHeaders = Record<string, string>;

/** Form-encoded bodies, for the endpoints that take `Form()` rather than JSON. */
export type FormData = Record<string, string>;

const baseUrl = "http://localhost:8000";

interface ValidationDetail {
  loc?: (string | number)[];
  msg?: string;
}

/** Turn FastAPI's validation detail into one readable line, e.g. "password: too short". */
const describeValidationError = (detail: unknown): string => {
  if (!Array.isArray(detail) || detail.length === 0) {
    return typeof detail === "string" ? detail : "That request was not valid.";
  }
  const [first] = detail as ValidationDetail[];
  const message = first?.msg ?? "That request was not valid.";
  // loc looks like ["body", "password"]; the last entry is the field itself
  const field = first?.loc?.at(-1);
  return typeof field === "string" && field !== "body" ? `${field}: ${message}` : message;
};

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (response.ok) {
    return (response.status === 204 ? {} : await response.json()) as T;
  }
  const error = await response.json();
  if (error.detail) {
    // FastAPI's own validation errors are shaped differently from our `Err` model:
    // a list of {loc, msg, type}. Surface the first as a sentence rather than
    // dumping the raw JSON at the user.
    throw new ApiError(response.status, {
      error: "validation",
      message: describeValidationError(error.detail),
    });
  }
  throw new ApiError(response.status, error as ApiErrorBody);
};

const get = async <T>(url: string, headers: ApiHeaders): Promise<T> => {
  const response = await fetch(baseUrl + url, { headers });
  return await handleResponse<T>(response);
};

const put = async <T>(url: string, headers: ApiHeaders, data: unknown): Promise<T> => {
  const response = await fetch(baseUrl + url, {
    headers: {
      ...headers,
      "Content-Type": "application/json",
    },
    method: "PUT",
    body: JSON.stringify(data),
  });
  return await handleResponse<T>(response);
};

const post = async <T>(url: string, headers: ApiHeaders, data: unknown): Promise<T> => {
  const response = await fetch(baseUrl + url, {
    headers: {
      ...headers,
      "Content-Type": "application/json",
    },
    method: "POST",
    body: JSON.stringify(data),
  });
  return await handleResponse<T>(response);
};

const del = async <T>(url: string, headers: ApiHeaders): Promise<T> => {
  const response = await fetch(baseUrl + url, {
    headers,
    method: "DELETE",
  });
  return await handleResponse<T>(response);
};

const putForm = async <T>(url: string, headers: ApiHeaders, data: FormData): Promise<T> => {
  const response = await fetch(baseUrl + url, {
    headers: {
      ...headers,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    method: "PUT",
    body: new URLSearchParams(data),
  });
  return await handleResponse<T>(response);
};

const postForm = async <T>(url: string, headers: ApiHeaders, data: FormData): Promise<T> => {
  const response = await fetch(baseUrl + url, {
    headers: {
      ...headers,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    method: "POST",
    body: new URLSearchParams(data),
  });
  return await handleResponse<T>(response);
};

export default { get, post, postForm, put, putForm, del };
