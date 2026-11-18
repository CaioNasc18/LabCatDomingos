import { useState } from "react";
import "../index.css";


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
                <p className="brand__word">
                  <em> Todos os casos.</em>
                    <br />
                    Um lugar só.
                    <br/>
                </p>
            </section>

            {/* Lado direito: formulário */}
            <section className="login__panel">
                <div className="login__inner">

                    <h1 className="title">
                        Área
                        <br />
                        Reservada
                    </h1>


                    <form className="form" onSubmit={handleSubmit}>
                        <div className="field">
                            <label htmlFor="email">E-mail</label>
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
                                <span>Lembrar-me</span>
                            </label>
                            <a className="link" href="#">
                                Esqueceu a palavra-passe?
                            </a>
                        </div>

                        <button className="btn" type="submit">
                            <span>Entrar</span>
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