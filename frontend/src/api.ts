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

/** Auth headers as produced by `useAuth()`. */
export type ApiHeaders = Record<string, string>;

/** Form-encoded bodies, for the endpoints that take `Form()` rather than JSON. */
export type FormData = Record<string, string>;

const baseUrl = "http://localhost:8000";

const handleResponse = async <T>(response: Response): Promise<T> => {
    if (response.ok) {
        return (response.status === 204 ? {} : await response.json()) as T;
    }
    const error = await response.json();
    if (error.detail) {
        // FastAPI's own validation errors are shaped differently from our `Err` model.
        throw new ApiError(response.status, {
            error: "validation",
            message: JSON.stringify(error.detail),
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
