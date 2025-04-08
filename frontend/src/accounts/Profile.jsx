import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {Navigate, useNavigate} from "react-router";
import { useAuth } from "../hooks";
import { useAccount } from "../queries";
import Form from "../components/Form";
import FormInput from "../components/FormInput";
import FormButton from "../components/FormButton";
import api from "../api";
import ChatList from "../ChatList.jsx";




function UpdateForm() {
    const queryClient = useQueryClient();
    const { account } = useAccount();
    const { headers } = useAuth();
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [errorMsg, setErrorMsg] = useState(null);
    const [successMsg, setSuccessMsg] = useState(null);

    useEffect(() => {
        setUsername(account.username);
    }, [account]);

    useEffect(() => {
        setEmail(account.email);
    }, [account]);

    const mutation = useMutation({
        mutationFn: () => api.put("/accounts/me", headers, { username, email }),
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

    const handleSubmit = (e) => {
        e.preventDefault();
        mutation.mutate();
    };

    return (
        <section>
            <Form onSubmit={handleSubmit}>
                <h1 className="text-xl font-bold text-center">update account</h1>
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
                <FormButton text="update account" />
                {errorMsg && <Error message={errorMsg} />}
                {successMsg && <Success message={successMsg} />}
            </Form>
        </section>
    );
}

function UpdatePasswordForm(){
    const [new_password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [old_password, setOldPassword] = useState("");
    const [disabled, setDisabled] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");
    const [successMsg, setSuccessMsg] = useState("");
    const { headers } = useAuth();

    const mutation = useMutation({
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

    const handleSubmit = (e) => {
        e.preventDefault();
        if(new_password !== confirmPassword){
            setErrorMsg("Passwords do not match");
            return;
        }
        mutation.mutate();
    };

    const buttonDisabled = !new_password || !confirmPassword || disabled;

    return (
        <Form onSubmit={handleSubmit}>
            <h1 className="text-xl font-bold text-center">update password</h1>
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
            <FormButton text="update password" disabled={buttonDisabled} />
        </Form>
    )
}

function AccountButtons(){
    return(
        <div className="flex flex-col border border-black rounded space-y-4 w-96 mx-auto p-4">
            <h1 className="text-xl font-bold text-center">account</h1>
            <LogoutButton />
            <DeleteAccountButton />
        </div>
    )
}


function LogoutButton() {
    const queryClient2 = useQueryClient();
    const { logout } = useAuth();
    const navigate = useNavigate();
    const handleLogout = () =>{
        logout();
        queryClient2.invalidateQueries().then(() => navigate('/login'));
    };

    return (
        <div>
        <button
            onClick={handleLogout}
            className="cursor-pointer border border-black rounded p-2 hover:bg-red-400 w-full"
        >
            logout
        </button>
        </div>
    );
}

function DeleteAccountButton() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const { headers, logout } = useAuth();
    const [errorMsg, setErrorMsg] = useState("");
    const mutation = useMutation({
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
            onClick={mutation.mutate}
            className="cursor-pointer border border-red-600 rounded p-2 hover:bg-red-800 w-full"
        >
            delete account
        </button>
        {errorMsg && <Error message={errorMsg} />}
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

function Error({ message }) {
    return <p className="text-xs text-amber-700">{message}</p>;
}

function Success({ message }) {
    return <p className="text-xs text-lime-600">{message}</p>;
}

export default function Profile() {
    const { loggedIn } = useAuth();

    if (!loggedIn) {
        return <Navigate to="/" />;
    }

    return (
        <div className={"flex"}>
            <div className={"w-1/4 border-r border-gray-300"}>
                <ChatList />
            </div>
            <div className={"w-3/4 pr-4 pl-4 pt-4 pb-8 bg-white"}>
                <Account />
            </div>
        </div>
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
