function ServiceCard({ number, title, text, tags }) {
  return (
    <article className="service-card">
      <div className="service-number">{number}</div>
      <div>
        <h3>{title}</h3>
        <p>{text}</p>
        <ul>
          {tags.map((tag) => (
            <li key={tag}>{tag}</li>
          ))}
        </ul>
      </div>
      <span className="service-arrow" aria-hidden="true">↗</span>
    </article>
  );
}

export default ServiceCard;