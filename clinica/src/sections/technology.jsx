const technologies = [
  'Scanners 3D',
  'Design CAD/CAM',
  'Fresagem de precisão',
  'Impressão 3D',
  'Fornos cerâmicos',
  'Controlo de qualidade',
];

function Technology() {
  return (
    <section className="technology section" id="tecnologia">
      <div className="section-label">
        <span>02</span>
        <p>Tecnologia</p>
      </div>

      <div className="technology-content">
        <div className="technology-copy">
          <p className="eyebrow">Laboratório digital integrado</p>
          <h2>Mais precisão. Mais controlo. Menos distância.</h2>
          <p>
            A produção interna aproxima técnico e médico dentista, acelera
            ajustes e permite acompanhar todas as decisões do caso. Tecnologia
            não substitui o olhar humano — amplifica-o.
          </p>
        </div>

        <div className="technology-gallery">
          <figure className="technology-image technology-image--wide">
            <img
              src="/assets/dental-digital-lab.jpg"
              alt="Análise de um scan dentário digital num tablet"
            />
            <figcaption>Planeamento digital / Foto: Quang Tri Nguyen</figcaption>
          </figure>
          <figure className="technology-image technology-image--detail">
            <img
              src="/assets/dental-craft.jpg"
              alt="Técnico a trabalhar manualmente numa prótese dentária"
            />
            <figcaption>Acabamento artesanal / Foto: Adrian Sulyok</figcaption>
          </figure>
        </div>

        <div className="technology-list" aria-label="Tecnologias disponíveis">
          {technologies.map((technology, index) => (
            <div key={technology}>
              <span>{String(index + 1).padStart(2, '0')}</span>
              <p>{technology}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Technology;