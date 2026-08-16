import type { ButtonHTMLAttributes } from "react";

interface FormButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    text: string;
}

export default function FormButton({ text, disabled, ...options }: FormButtonProps) {
    const className =
        "btn-seal px-4 py-2 uppercase text-sm" +
        (disabled ? "" : " cursor-pointer");

    return (
        <button type="submit" className={className} disabled={disabled} {...options}>
            {text}
        </button>
    );
}
