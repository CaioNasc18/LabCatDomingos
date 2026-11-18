const metrics = [
  { label: 'Desenho e planeamento', value: 'CAD', caption: 'Precisão digital' },
  { label: 'Produção avançada', value: '3D', caption: 'Fresagem + impressão' },
  { label: 'Verificação final', value: 'QC', caption: 'Controlo de qualidade' },
];

function Metrics() {
  return (
    <section className="metrics" aria-label="Indicadores do laboratório">
      {metrics.map((metric) => (
        <article key={metric.value}>
          <small>{metric.label}</small>
          <strong>{metric.value}</strong>
          <span>{metric.caption}</span>
        </article>
      ))}
    </section>
  );
}

export default Metrics;