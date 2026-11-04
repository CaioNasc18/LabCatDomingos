import { useState } from "react";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [remember, setRemember] = useState(false);

    function handleSubmit(e) {
        e.preventDefault();
        // TODO: ligar ao backend / API de autenticação
        console.log({ email, password, remember });
    }

    return (
        <main className="login">
            {/* Lado esquerdo: marca */}
            <section className="login__brand" aria-hidden="true">
                <a className="logo" href="/">
                    LABO<span className="logo__dot"></span>
                </a>

                <p className="brand__word">
                    Pre<em>cisão</em>
                    <br />
                    em cada
                    <br />
                    caso.
                </p>

                <p className="brand__foot">
                    © 2026 LABO · Laboratório de prótese dentária
                </p>
            </section>

            {/* Lado direito: formulário */}
            <section className="login__panel">
                <div className="login__inner">
                    <p className="eyebrow">
                        <span className="eyebrow__bar"></span>Área reservada
                    </p>

                    <h1 className="title">
                        Acesso
                        <br />
                        profissional
                    </h1>

                    <p className="lead">
                        Entre para gerir casos, ficheiros, aprovações e comunicação com o
                        laboratório.
                    </p>

                    <form className="form" onSubmit={handleSubmit}>
                        <div className="field">
                            <label htmlFor="email">Email profissional</label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                placeholder="nome@clinica.pt"
                                autoComplete="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        <div className="field">
                            <label htmlFor="password">Palavra-passe</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                placeholder="••••••••"
                                autoComplete="current-password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        <div className="row">
                            <label className="check">
                                <input
                                    type="checkbox"
                                    name="remember"
                                    checked={remember}
                                    onChange={(e) => setRemember(e.target.checked)}
                                />
                                <span>Manter sessão</span>
                            </label>
                            <a className="link" href="#">
                                Recuperar acesso
                            </a>
                        </div>

                        <button className="btn" type="submit">
                            <span>Entrar no backoffice</span>
                            <span className="btn__arrow">↗</span>
                        </button>
                    </form>

                    <p className="signup">
                        Ainda não tem acesso?{" "}
                        <a className="link link--light" href="#">
                            Pedir credenciais
                        </a>
                    </p>
                </div>
            </section>
        </main>
    );
}