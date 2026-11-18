import { useState } from 'react';
import Mark from '../Mark/Mark';
import styles from './Navbar.module.css';

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => setMenuOpen(false);

  return (
    <header className={styles.header}>
      <Mark />

      <nav
        className={menuOpen ? `${styles.nav} ${styles.navOpen}` : styles.nav}
        aria-label="Navegação principal"
      >
        <a href="#laboratorio" onClick={closeMenu}>Laboratório</a>
        <a href="#tecnologia" onClick={closeMenu}>Tecnologia</a>
        <a href="#servicos" onClick={closeMenu}>Serviços</a>
        <a href="#app" onClick={closeMenu}>App</a>
        <a href="#contactos" onClick={closeMenu}>Contactos</a>
      </nav>

      <button className={styles.cta} type="button">
        Área reservada <span>↗</span>
      </button>

      <button
        className={styles.menuButton}
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