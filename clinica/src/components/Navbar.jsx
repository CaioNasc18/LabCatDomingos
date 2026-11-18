import { useState } from 'react';
import { Link } from 'react-router-dom';
import Mark from './Mark';

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => setMenuOpen(false);

  return (
    <header className="site-header">
      <Mark />

      <nav
        className={menuOpen ? 'nav nav--open' : 'nav'}
        aria-label="Navegação principal"
      >
        <a href="#laboratorio" onClick={closeMenu}>Laboratório</a>
        <a href="#tecnologia" onClick={closeMenu}>Tecnologia</a>
        <a href="#servicos" onClick={closeMenu}>Serviços</a>
        <a href="#app" onClick={closeMenu}>App</a>
        <a href="#contactos" onClick={closeMenu}>Contactos</a>
      </nav>

      <Link className="header-cta" to="/area-reservada">
        Área reservada <span>↗</span>
      </Link>

      <button
        className="menu-button"
        type="button"
        aria-label={menuOpen ? 'Fechar menu' : 'Abrir menu'}
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((open) => !open)}
      >
        <span />
        <span />
      </button>
    </header>
  );
}

export default Navbar;