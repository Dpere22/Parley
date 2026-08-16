import type { ButtonHTMLAttributes } from "react";

interface FormButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    text: string;
}

export default function FormButton({ text, disabled, ...options }: FormButtonProps) {
    const className =
        "border border-black rounded px-4 py-2" +
        (disabled ? " bg-gray-400 italic" : " hover:bg-lime-600 cursor-pointer");

    return (
        <button type="submit" className={className} disabled={disabled} {...options}>
            {text}
        </button>
    );
}
