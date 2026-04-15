// Recursive component — calls itself for nested objects and arrays.
// This means it works for any JSON depth without any changes.

// Entry point — decides what to render based on the type of `value`
export default function JsonRenderer({ data }) {
    return (
        <div className="flex flex-col gap-3">
            {Object.entries(data).map(([key, value]) => (
                <JsonField key={key} fieldKey={key} value={value} />
            ))}
        </div>
    )
}

// Renders one key-value pair — delegates to the right sub-renderer
function JsonField({ fieldKey, value }) {

    const label = "text-xs font-bold uppercase tracking-widest text-gray-400 mb-1"
    const keyLabel = humanize(fieldKey)

    // Array — render as a list or as a set of sub-cards
    if (Array.isArray(value)) {
        return (
            <div>
                <p className={label}>{keyLabel}</p>
                <ArrayValue items={value} />
            </div>
        )
    }

    // Nested object — render as an indented sub-card
    if (typeof value === 'object' && value !== null) {
        return (
            <div>
                <p className={label}>{keyLabel}</p>
                <ObjectValue data={value} />
            </div>
        )
    }

    // Primitive (string, number, boolean, null) — simple row
    return (
        <div>
            <p className={label}>{keyLabel}</p>
            <PrimitiveValue value={value} />
        </div>
    )
}

// ── Primitive ─────────────────────────────────────────────────────────────────

function PrimitiveValue({ value }) {

    // Booleans get a colored badge instead of "true"/"false" text
    if (typeof value === 'boolean') {
        return (
            <span className={[
                "inline-block px-2 py-0.5",
                "text-xs font-bold uppercase tracking-widest",
                "border border-black rounded-none",
                value ? "bg-green-400 text-black" : "bg-red-400 text-white",
            ].join(" ")}>
                {value ? "Yes" : "No"}
            </span>
        )
    }

    // null or undefined
    if (value === null || value === undefined) {
        return <span className="text-sm text-gray-400 italic">—</span>
    }

    // String or number
    return (
        <span className="text-sm font-medium text-navy wrap-break-word">
            {String(value)}
        </span>
    )
}

// ── Object ────────────────────────────────────────────────────────────────────

// Renders a nested object as an indented card — calls JsonRenderer recursively
function ObjectValue({ data }) {
    return (
        <div className={[
            "border-2 border-black rounded-none",
            "p-4 mt-1",
            // Left border accent to visually signal nesting depth
            "border-l-4 border-l-navy",
        ].join(" ")}>
            {/* Recursion: JsonRenderer calls JsonField which calls ObjectValue
                which calls JsonRenderer — this handles any depth */}
            <JsonRenderer data={data} />
        </div>
    )
}

// ── Array ─────────────────────────────────────────────────────────────────────

function ArrayValue({ items }) {

    if (items.length === 0) {
        return <span className="text-sm text-gray-400 italic">Empty</span>
    }

    const firstItem = items[0]

    // Array of objects → each item gets its own sub-card with an index label
    if (typeof firstItem === 'object' && firstItem !== null && !Array.isArray(firstItem)) {
        return (
            <div className="flex flex-col gap-3 mt-1">
                {items.map((item, index) => (
                    <div
                        key={index}
                        className={[
                            "border-2 border-black rounded-none p-4",
                            "border-l-4 border-l-accent",
                        ].join(" ")}
                    >
                        <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">
                            Item {index + 1}
                        </p>
                        <JsonRenderer data={item} />
                    </div>
                ))}
            </div>
        )
    }

    // Array of primitives → compact inline tags
    return (
        <div className="flex flex-wrap gap-2 mt-1">
            {items.map((item, index) => (
                <span
                    key={index}
                    className="px-2 py-1 text-sm font-medium border border-black bg-gray-50"
                >
                    {String(item)}
                </span>
            ))}
        </div>
    )
}

// ── Utility ───────────────────────────────────────────────────────────────────

// Converts snake_case or camelCase keys into readable labels
// "openocd_config_path" → "Openocd Config Path"
// "mainDevice" → "Main Device"
function humanize(key) {
    return key
        .replace(/_/g, ' ')                        // snake_case → spaces
        .replace(/([A-Z])/g, ' $1')                // camelCase → spaces
        .replace(/\b\w/g, c => c.toUpperCase())    // capitalize each word
        .trim()
}