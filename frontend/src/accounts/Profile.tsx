import { useEffect, useState, type FormEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import { useAuth } from "../hooks";
import { useAccount } from "../queries";
import Form from "../components/Form";
import FormInput from "../components/FormInput";
import FormButton from "../components/FormButton";
import api, { type ApiError } from "../api";
import NavList from "../NavList";
import type { User } from "../types";

function Error({ message }: { message: string }) {
    return <p className="text-xs text-crimson-light italic">{message}</p>;
}

function Success({ message }: { message: string }) {
    return <p className="text-xs text-moss italic">{message}</p>;
}

function UpdateForm() {
    const queryClient = useQueryClient();
    const { account } = useAccount();
    const { headers } = useAuth();
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [errorMsg, setErrorMsg] = useState<string | null>(null);
    const [successMsg, setSuccessMsg] = useState<string | null>(null);

    useEffect(() => {
        setUsername(account.username);
        setEmail(account.email);
    }, [account]);

    const mutation = useMutation<User, ApiError>({
        mutationFn: () => api.put<User>("/accounts/me", headers, { username, email }),
        onSuccess: (data) => {
            queryClient.setQueryData(["account"], data);
            setErrorMsg(null);
            setSuccessMsg("account updated!!");
        },
        onError: (error) => {
            setErrorMsg(error.message);
            setSuccessMsg(null);
        },
    });

    const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        mutation.mutate();
    };

    return (
        <section>
            <Form onSubmit={handleSubmit}>
                <h1 className="heading text-xl text-center">Amend Thy Title</h1>
                <hr className="rule-gilt" />
                <FormInput
                    id="username"
                    type="text"
                    text="username"
                    name="username"
                    value={username}
                    setValue={setUsername}
                />
                <FormInput
                    id="email"
                    type="email"
                    text="email"
                    name="email"
                    value={email}
                    setValue={setEmail}
                />
                <FormButton text="Set it down" />
                {errorMsg && <Error message={errorMsg} />}
                {successMsg && <Success message={successMsg} />}
            </Form>
        </section>
    );
}

function UpdatePasswordForm() {
    const [new_password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [old_password, setOldPassword] = useState("");
    const [disabled, setDisabled] = useState(false);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);
    const [successMsg, setSuccessMsg] = useState<string | null>(null);
    const { headers } = useAuth();

    const mutation = useMutation<unknown, ApiError>({
        mutationFn: () => api.putForm("/accounts/me/password", headers, { old_password, new_password }),
        onMutate: () => setDisabled(true),
        onSuccess: () => {
            setSuccessMsg("password updated!");
            setDisabled(false);
            setErrorMsg(null);
        },
        onError: (error) => {
            setDisabled(false);
            setErrorMsg(error.message);
            setSuccessMsg(null);
        },
    });

    const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (new_password !== confirmPassword) {
            setErrorMsg("Passwords do not match");
            return;
        }
        mutation.mutate();
    };

    const buttonDisabled = !new_password || !confirmPassword || disabled;

    return (
        <Form onSubmit={handleSubmit}>
            <h1 className="heading text-xl text-center">Change Thy Watchword</h1>
            <hr className="rule-gilt" />
            <FormInput
                id="old_password"
                type="password"
                name="old_password"
                text="current password"
                value={old_password}
                setValue={setOldPassword}
            />
            <FormInput
                id="new_password"
                type="password"
                name="new_password"
                text="new password"
                value={new_password}
                setValue={setPassword}
            />
            <FormInput
                id="confirmPassword"
                type="password"
                name="confirmPassword"
                text="confirm new password"
                value={confirmPassword}
                setValue={setConfirmPassword}
            />
            {errorMsg && <Error message={errorMsg} />}
            {successMsg && <Success message={successMsg} />}
            <FormButton text="Reforge it" disabled={buttonDisabled} />
        </Form>
    );
}

function LogoutButton() {
    const queryClient = useQueryClient();
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        queryClient.invalidateQueries().then(() => navigate('/login'));
    };

    return (
        <div>
            <button
                onClick={handleLogout}
                className="btn-iron cursor-pointer p-2 w-full text-sm uppercase"
            >
                Take leave
            </button>
        </div>
    );
}

function DeleteAccountButton() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const { headers, logout } = useAuth();
    const [errorMsg, setErrorMsg] = useState("");

    const mutation = useMutation<unknown, ApiError>({
        mutationFn: () => api.del("/accounts/me", headers),
        onSuccess: () => {
            logout();
            queryClient.invalidateQueries().then(() => navigate('/login'));
        },
        onError: (error) => {
            setErrorMsg(error.message);
        },
    });

    return (
        <div>
            <button
                onClick={() => mutation.mutate()}
                className="btn-seal cursor-pointer p-2 w-full text-sm uppercase"
            >
                Burn thy seal
            </button>
            {errorMsg && <Error message={errorMsg} />}
        </div>
    );
}

function AccountButtons() {
    return (
        <div className="parchment parchment-curl flex flex-col border-2 border-oak-dark rounded-sm shadow-2xl space-y-4 w-96 mx-auto p-6">
            <h1 className="heading text-xl text-center">Thy Standing</h1>
            <hr className="rule-gilt" />
            <LogoutButton />
            <DeleteAccountButton />
        </div>
    );
}

function Account() {
    return (
        <section className="justify-self-center space-y-4">
            <UpdateForm />
            <UpdatePasswordForm />
            <AccountButtons />
        </section>
    );
}

export default function Profile() {
    return (
        <div className={"flex hall min-h-screen"}>
            <div className={"w-1/4 min-w-0 border-r-2 border-oak-dark"}>
                <NavList />
            </div>
            <div className={"w-3/4 min-w-0 px-6 pt-8 pb-8 h-screen overflow-y-auto"}>
                <h1 className={"heading text-3xl text-center text-gilt-light pb-2"}>The Chambers</h1>
                <hr className="rule-gilt w-80 mx-auto mb-6" />
                <Account />
            </div>
        </div>
    );
}
