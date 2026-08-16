import type { InputHTMLAttributes } from "react";

interface FormInputProps
    extends Omit<InputHTMLAttributes<HTMLInputElement>, "value" | "onChange" | "name"> {
    id: string;
    type: string;
    value: string;
    setValue: (value: string) => void;
    name: string;
    text: string;
}

export default function FormInput({
                                      id,
                                      type,
                                      value,
                                      setValue,
                                      name,
                                      text,
                                      ...options
                                  }: FormInputProps) {
    const className =
        "border border-gray-400 px-4 py-2 rounded" +
        (options.disabled ? " bg-gray-400 text-gray-600" : "");

    return (
        <section className="flex flex-col">
            <label htmlFor={id} className="text-sm">
                {text}
            </label>
            <input
                id={id}
                name={name}
                type={type}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder={text}
                className={className}
                {...options}
            />
        </section>
    );
}
