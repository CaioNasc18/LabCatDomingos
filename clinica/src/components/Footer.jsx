import Mark from './Mark';

function Footer() {
  return (
    <footer className="site-footer">
      <Mark />
      <p>Laboratório de prótese dentária</p>
      <span className="site-footer-copy">© {new Date().getFullYear()} LABO</span>
      <a className="site-footer-top" href="#inicio">Voltar ao topo ↑</a>
    </footer>
  );
}

export default Footer;