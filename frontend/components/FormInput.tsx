interface FormInputProps {
  label: string
  id: string
  type?: string
  value: string
  onChange: (value: string) => void
}

export default function FormInput({ label, id, type = "text", value, onChange }: FormInputProps) {
  return (
    <label htmlFor={id} className="block text-sm font-medium text-slate-200">
      {label}
      <input
        id={id}
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-2 w-full rounded-3xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20"
      />
    </label>
  )
}
