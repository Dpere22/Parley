export default function Form({ onSubmit, children, ...options }) {
    const className = [
        "flex flex-col",
        "border border-lime-700 rounded",
        "space-y-4 w-96 mx-auto p-4",
    ].join(" ");
    return (
        <form className={className} onSubmit={onSubmit}>
            {children}
        </form>
    );
}
