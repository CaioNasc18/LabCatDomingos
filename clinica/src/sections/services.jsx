import ServiceCard from '../components/ServiceCard';
import { services } from '../data/services';

function Services() {
  return (
    <section className="services section" id="servicos">
      <div className="section-label">
        <span>03</span>
        <p>O que fazemos</p>
      </div>

      <div className="services-content">
        <div className="section-heading">
          <p className="eyebrow">Serviços</p>
          <h2>Soluções personalizadas para cada indicação clínica.</h2>
        </div>

        <div className="service-list">
          {services.map((service) => (
            <ServiceCard key={service.number} {...service} />
          ))}
        </div>
      </div>
    </section>
  );
}

export default Services;