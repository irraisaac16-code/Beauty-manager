export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/85 backdrop-blur">
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
          <p className="text-lg font-bold tracking-wide">
            <span className="text-amber-300">Beauty</span>{" "}
            <span className="text-violet-300">Manager</span>
          </p>
          <a
            href="http://127.0.0.1:8000/connexion/"
            className="rounded-full border border-violet-300/40 px-4 py-2 text-sm font-medium text-violet-200 transition hover:bg-violet-500/10"
          >
            Se connecter
          </a>
        </div>
      </header>

      <main>
        <section className="mx-auto grid w-full max-w-6xl items-center gap-12 px-6 py-16 lg:grid-cols-2 lg:py-24">
          <div>
            <p className="mb-4 inline-flex rounded-full border border-emerald-300/30 bg-emerald-400/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-200">
              Plateforme SaaS pour salon de beautÃ©
            </p>
            <h1 className="text-4xl font-black leading-tight sm:text-5xl">
              Pilote ton salon avec une interface moderne, rapide et claire.
            </h1>
            <p className="mt-6 max-w-xl text-slate-300">
              GÃ¨re les rendez-vous, les paiements et tes Ã©quipes depuis un seul
              outil. PensÃ© pour accÃ©lÃ©rer la croissance de ton activitÃ©.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <a
                href="http://127.0.0.1:8000/connexion/"
                className="rounded-xl bg-violet-500 px-5 py-3 font-semibold text-white shadow-lg shadow-violet-500/30 transition hover:bg-violet-400"
              >
                Essayer maintenant
              </a>
              <a
                href="#fonctionnalites"
                className="rounded-xl border border-slate-600 px-5 py-3 font-semibold text-slate-200 transition hover:border-slate-400 hover:bg-slate-800/70"
              >
                Voir les fonctionnalitÃ©s
              </a>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-violet-500/20 via-sky-500/10 to-amber-400/10 p-6 shadow-2xl shadow-violet-900/20">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
                <p className="text-sm text-slate-400">RÃ©servations/mois</p>
                <p className="mt-1 text-2xl font-bold text-white">+1 240</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
                <p className="text-sm text-slate-400">Taux de prÃ©sence</p>
                <p className="mt-1 text-2xl font-bold text-emerald-300">96%</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 sm:col-span-2">
                <p className="text-sm text-slate-400">Paiements sÃ©curisÃ©s</p>
                <p className="mt-1 text-lg font-semibold text-white">
                  Mobile Money & espÃ¨ces avec suivi en temps rÃ©el
                </p>
              </div>
            </div>
          </div>
        </section>

        <section id="fonctionnalites" className="mx-auto w-full max-w-6xl px-6 pb-12">
          <h2 className="text-2xl font-bold sm:text-3xl">FonctionnalitÃ©s clÃ©s</h2>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {[
              {
                title: "Planning intelligent",
                text: "CrÃ©neaux optimisÃ©s, conflits Ã©vitÃ©s, visibilitÃ© totale sur l'agenda.",
              },
              {
                title: "Gestion des rÃ´les",
                text: "Admin, esthÃ©ticiennes et clients avec accÃ¨s et dashboards dÃ©diÃ©s.",
              },
              {
                title: "Suivi business",
                text: "Bilans hebdo, mensuels et annuels pour piloter la performance.",
              },
            ].map((item) => (
              <article
                key={item.title}
                className="rounded-2xl border border-white/10 bg-slate-900/60 p-5"
              >
                <h3 className="text-lg font-semibold text-violet-200">{item.title}</h3>
                <p className="mt-3 text-sm text-slate-300">{item.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="mx-auto w-full max-w-6xl px-6 pb-16">
          <div className="rounded-3xl border border-violet-300/30 bg-violet-500/10 p-8 text-center">
            <h2 className="text-2xl font-bold sm:text-3xl">
              PrÃªt Ã  moderniser ton salon ?
            </h2>
            <p className="mx-auto mt-3 max-w-2xl text-slate-300">
              Lance Beautix et transforme ta gestion quotidienne en
              expÃ©rience fluide, premium et rentable.
            </p>
            <a
              href="http://127.0.0.1:8000/connexion/"
              className="mt-6 inline-block rounded-xl bg-amber-300 px-5 py-3 font-bold text-slate-900 transition hover:bg-amber-200"
            >
              DÃ©marrer
            </a>
          </div>
        </section>
      </main>
    </div>
  );
}

