import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Hero from '../sections/Hero';
import Intro from '../sections/Intro';
import Metrics from '../sections/metrics';
import Technology from '../sections/technology';
import Services from '../sections/services';
import servicecard from '../components/ServiceCard';

function Home() {
  return (
    <main>
      <Navbar />
      <Hero />
      <Intro />
      <Metrics />
      <Technology />
      <Services />
      <Footer />
    </main>
  );
}

export default Home;