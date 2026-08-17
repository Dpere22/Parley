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
    return (
        <section className="flex flex-col">
            <label htmlFor={id} className="heading text-xs uppercase text-ink-soft mb-1">
                {text}
            </label>
            <input
                id={id}
                name={name}
                type={type}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder={text}
                className="field-ink px-3 py-2"
                {...options}
            />
        </section>
    );
}
