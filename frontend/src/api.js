class ApiError extends Error{
    constructor(status, {error, message}) {
        super(message);
        this.status = status;
        this.code = error;
    }
}



const baseUrl = "http://localhost:8000";

const handleResponse = async (response) => {
    if (response.ok){
        return response.status === 204 ? {} : await response.json();
    } else{
        const error = await response.json();
        if(error.detail){
            throw new ApiError(response.status, {
                error: "validation",
                message: JSON.stringify(error.detail)
            });
        } else{
            throw new ApiError(response.status, error);
        }
    }
};

const get = async (url, headers) => {
    const response = await fetch(baseUrl + url, {headers});
    return await handleResponse(response);
}

const post = async (url, headers, data) => {
    const response = await fetch(baseUrl + url, {
        headers,
        method: "POST",
        body: JSON.stringify(data)
    });
    return await handleResponse(response);
};

const form = async(url, headers, data) => {
    const response = await fetch(baseUrl + url, {
        headers: {
            ...headers,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method: "POST",
        body: new URLSearchParams(data)
    });
    return await handleResponse(response);
};

export default {get, post, form}