export default function SectionHead({
  eyebrow, title, lead,
}: { eyebrow?: string; title: string; lead?: string }) {
  return (
    <div className="sec-head">
      {eyebrow && <span className="eyebrow">{eyebrow}</span>}
      <h2 className="mt">{title}</h2>
      {lead && <p className="lead mt">{lead}</p>}
    </div>
  );
}
