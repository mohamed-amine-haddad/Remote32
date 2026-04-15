import clsx from 'clsx'


export default function StatusBadge({ status }) {

    const base = [
        "inline-block",
        "px-2 py-1",
        "text-xs font-bold uppercase tracking-widest",
        "border border-black rounded-none",
    ].join(" ")

    // Each status gets a distinct background — never rely on color alone,
    // so the text label is always present too (accessibility)
    const variants = {
        free:     "bg-green-400 text-black",
        occupied: "bg-red-400 text-white",
        reserved: "bg-accent text-navy",
    }

    const label = {
        free:     "Available",
        occupied: "In use",
        reserved: "Reserved",
    }

    return (
        <span className={clsx(base, variants[status])}>
            {label[status]}
        </span>
    )
}