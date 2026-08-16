import type { FormEventHandler, ReactNode } from "react";

interface FormProps {
    onSubmit: FormEventHandler<HTMLFormElement>;
    children: ReactNode;
}

export default function Form({ onSubmit, children }: FormProps) {
    const className = [
        "flex flex-col",
        "border border-black rounded",
        "space-y-4 w-96 mx-auto p-4",
    ].join(" ");
    return (
        <form className={className} onSubmit={onSubmit}>
            {children}
        </form>
    );
}
