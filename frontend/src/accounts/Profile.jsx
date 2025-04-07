import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Navigate } from "react-router";
import { useAuth } from "../hooks";
import { useAccount } from "../queries";
import Form from "../components/Form";
import FormInput from "../components/FormInput";
import FormButton from "../components/FormButton";
import api from "../api";

function UpdateForm() {
    const queryClient = useQueryClient();
    const { account } = useAccount();
    const { headers } = useAuth();
    const [username, setUsername] = useState("");
    const [errorMsg, setErrorMsg] = useState(null);
    const [successMsg, setSuccessMsg] = useState(null);

    useEffect(() => {
        setUsername(account.username);
    }, [account]);

    const mutation = useMutation({
        mutationFn: () => api.put("/accounts/me", headers, { username }),
        onSuccess: (data) => {
            queryClient.setQueryData(["account"], data);
            setErrorMsg(null);
            setSuccessMsg("username updated!!");
        },
        onError: (error) => {
            setErrorMsg(error.message);
            setSuccessMsg(null);
        },
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        mutation.mutate();
    };

    return (
        <section className="border border-violet-700 rounded p-4">
            <h1 className="text-xl font-bold text-center">update account</h1>
            <Form onSubmit={handleSubmit}>
                <FormInput
                    id="username"
                    type="text"
                    text="username"
                    name="username"
                    value={username}
                    setValue={setUsername}
                />
                <FormButton text="update username" />
                {errorMsg && <Error message={errorMsg} />}
                {successMsg && <Success message={successMsg} />}
            </Form>
        </section>
    );
}

function LogoutButton() {
    const { logout } = useAuth();

    return (
        <button
            onClick={logout}
            className="cursor-pointer border border-lime-700 rounded p-2"
        >
            logout
        </button>
    );
}

function Account() {
    return (
        <section className="justify-self-center space-y-4">
            <UpdateForm />
            <LogoutButton />
        </section>
    );
}

function Error({ message }) {
    return <p className="text-xs text-amber-700">{message}</p>;
}

function Success({ message }) {
    return <p className="text-xs text-lime-600">{message}</p>;
}

export default function Profile() {
    const { loggedIn } = useAuth();
    //const { account } = useAccount();

    if (!loggedIn) {
        return <Navigate to="/" />;
    }

    return (
            <Account />
    );
}

Account.propTypes = {
    username: PropTypes.string,
};

Error.propTypes = {
    message: PropTypes.string,
};

Success.propTypes = {
    message: PropTypes.string,
};
