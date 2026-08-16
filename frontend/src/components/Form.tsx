import type { FormEventHandler, ReactNode } from "react";

interface FormProps {
    onSubmit: FormEventHandler<HTMLFormElement>;
    children: ReactNode;
}

export default function Form({ onSubmit, children }: FormProps) {
    const className = [
        "parchment parchment-curl",
        "flex flex-col space-y-4 w-96 mx-auto p-6",
        "border-2 border-oak-dark rounded-sm shadow-2xl",
    ].join(" ");
    return (
        <form className={className} onSubmit={onSubmit}>
            {children}
        </form>
    );
}
