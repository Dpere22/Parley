import { useState, type FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link, Navigate } from "react-router";
import { useAuth } from "../hooks";
import api, { type ApiError } from "../api";
import Form from "../components/Form";
import FormInput from "../components/FormInput";
import FormButton from "../components/FormButton";
import type { AccessToken, User } from "../types";

function Error({ message }: { message: string }) {
    return <p className="text-amber-800 text-sm">{message}</p>;
}

function RegistrationForm() {
    const { loggedIn, login } = useAuth();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [email, setEmail] = useState("");
    const [passwordValidate, setPasswordValidate] = useState("");
    const [disabled, setDisabled] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");

    // Registering does not return a token, so a successful sign up logs in straight after.
    const tokenMutation = useMutation<AccessToken, ApiError>({
        mutationFn: () => api.postForm<AccessToken>("/auth/token", {}, { username, password }),
        onMutate: () => setDisabled(true),
        onSuccess: (data) => login(data.access_token),
        onError: (error) => {
            setDisabled(false);
            setErrorMsg(error.message);
        },
    });

    const registerMutation = useMutation<User, ApiError>({
        mutationFn: () => api.postForm<User>("/auth/registration", {}, { username, email, password }),
        onMutate: () => setDisabled(true),
        onSuccess: () => tokenMutation.mutate(),
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
        if (password !== passwordValidate) {
            setErrorMsg("Passwords do not match");
            return;
        }
        registerMutation.mutate();
    };

    const buttonDisabled = !username || !password || !email || !passwordValidate || disabled;

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
                id="email"
                type="text"
                name="email"
                text="email"
                value={email}
                setValue={setEmail}
            />
            <FormInput
                id="password"
                type="password"
                name="password"
                text="password"
                value={password}
                setValue={setPassword}
            />
            <FormInput
                id="passwordValidate"
                type="password"
                name="passwordValidate"
                text="confirm password"
                value={passwordValidate}
                setValue={setPasswordValidate}
            />
            {errorMsg && <Error message={errorMsg} />}
            <FormButton text="Register" disabled={buttonDisabled} />
            <Link to="/login" className={"text-pink-600 underline"}>Login</Link>
        </Form>
    );
}

export default function RegisterPage() {
    return (
        <div>
            <h1 className={"text-center font-extrabold text-4xl pb-4 pt-4"}>Pony Express</h1>
            <RegistrationForm />
        </div>
    );
}
