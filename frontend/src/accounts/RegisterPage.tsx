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
    return <p className="text-crimson-light text-sm italic">{message}</p>;
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
            <h2 className="heading text-xl text-center text-ink">Petition for a Seal</h2>
            <hr className="rule-gilt" />
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
            <FormButton text="Petition" disabled={buttonDisabled} />
            <Link to="/login" className={"heading text-xs uppercase text-center text-ink-soft hover:text-crimson underline decoration-gilt underline-offset-4"}>
                Already sealed? Enter here
            </Link>
        </Form>
    );
}

export default function RegisterPage() {
    return (
        <div className={"hall min-h-screen flex flex-col items-center justify-center py-12 px-4"}>
            <h1 className={"font-script text-6xl text-gilt-light text-center drop-shadow-lg"}>
                Parley
            </h1>
            <p className="heading text-xs uppercase tracking-[0.4em] text-parchment/60 mt-3 mb-2 text-center">
                Where counsel is taken
            </p>
            <hr className="rule-gilt w-72 my-6" />
            <RegistrationForm />
        </div>
    );
}
