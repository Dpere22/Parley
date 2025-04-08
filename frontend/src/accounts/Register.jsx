import {useAuth} from "../hooks.js";
import {useState} from "react";
import {useMutation} from "@tanstack/react-query";
import api from "../api.js";
import {Link, Navigate} from "react-router";
import Form from "../components/Form.jsx";
import FormInput from "../components/FormInput.jsx";
import FormButton from "../components/FormButton.jsx";
import PropTypes from "prop-types";
import Login from "./Login.jsx";

function Error({ message }) {
    return <p className="text-amber-800 text-sm">{message}</p>;
}

Error.propTypes = {
    message: PropTypes.string,
};

export default function Register() {
    const { loggedIn, login } = useAuth();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [email, setEmail] = useState("");
    const [passwordValidate, setPasswordValidate] = useState("");
    const [disabled, setDisabled] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");

    const mutation = useMutation({
        mutationFn: () => api.postForm("/auth/registration", {}, { username, email, password }),
        onMutate: () => setDisabled(true),
        onSuccess: () => mutation2.mutate(),
        onError: (error) => {
            setDisabled(false);
            setErrorMsg(error.message);
        },
    });

    const mutation2 = useMutation({
        mutationFn: () => api.postForm("/auth/token", {}, { username, password }),
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
    const handleSubmit = (e) => {
        e.preventDefault();
        if(password !== passwordValidate){
            setErrorMsg("Passwords do not match");
            return;
        }
        mutation.mutate();
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
            <Link to="/login">Login</Link>
        </Form>
    );
}