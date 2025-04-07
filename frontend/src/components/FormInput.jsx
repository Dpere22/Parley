export default function FormInput({
                                      id,
                                      type,
                                      value,
                                      setValue,
                                      name,
                                      text,
                                      ...options
                                  }) {
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
