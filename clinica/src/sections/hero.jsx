function Hero() {
  return (
    <section className="hero" id="inicio">
      {/* decorative vertical lines in the background */}
      <div className="hero-grid" aria-hidden="true">
        <span />
        <span />
        <span />
        <span />
        <span />
      </div>

      <div className="hero-kicker">
        <i />
        Laboratório de prótese dentária
        <span>PT · 2025</span>
      </div>

      <h1>
        Precisão digital.
        <br />
        <em>Forma natural.</em>
      </h1>

      <div className="hero-bottom">
        <p>
          Tecnologia avançada e mestria artesanal para criar soluções
          protéticas previsíveis, funcionais e naturalmente estéticas.
        </p>
        <a className="circle-link" href="#laboratorio" aria-label="Conhecer o laboratório">
          <span>↓</span>
        </a>
      </div>

      <div className="hero-index" aria-hidden="true">00—06</div>
    </section>
  );
}

export default Hero;