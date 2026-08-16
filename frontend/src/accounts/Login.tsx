import { useState, type FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link, Navigate } from "react-router";
import Form from "../components/Form";
import FormInput from "../components/FormInput";
import FormButton from "../components/FormButton";
import { useAuth } from "../hooks";
import api, { type ApiError } from "../api";
import type { AccessToken } from "../types";

function Error({ message }: { message: string }) {
    return <p className="text-amber-800 text-sm">{message}</p>;
}

export default function LoginPage() {
    return (
        <div className={"pt-4"}>
            <h1 className={"text-center font-extrabold text-4xl pb-2"}>Pony Express</h1>
            <div className={"pt-4"}>
                <Login />
            </div>
        </div>
    );
}

function Login() {
    const { loggedIn, login } = useAuth();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [disabled, setDisabled] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");

    const mutation = useMutation<AccessToken, ApiError>({
        mutationFn: () => api.postForm<AccessToken>("/auth/token", {}, { username, password }),
        onMutate: () => setDisabled(true),
        onSuccess: (data) => login(data.access_token),
        onError: (error) => {
            setDisabled(false);
            setErrorMsg(error.message);
        },
    });

    if (loggedIn) {
        return <Navigate to="/" />;
    }

    const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        mutation.mutate();
    };

    const buttonDisabled = !username || !password || disabled;

    return (
        <Form onSubmit={handleSubmit}>
            <FormInput
                id="username"
                type="text"
                name="username"
                text="username"
                value={username}
                setValue={setUsername}
            />
            <FormInput
                id="password"
                type="password"
                name="password"
                text="password"
                value={password}
                setValue={setPassword}
            />
            {errorMsg && <Error message={errorMsg} />}
            <FormButton text="login" disabled={buttonDisabled} />
            <Link to="/register" className={"text-pink-600 underline"}>Register</Link>
        </Form>
    );
}
