# MCP App minimale : Django DRF + FastMCP + React

Une todo-list qui s'affiche **dans la conversation** (Claude, VS Code…) et sur
laquelle on peut cliquer, avec un graphique de suivi (semaine / mois).

```
learn_mcp/
├── backend/                  Django + DRF + FastMCP (un seul process)
│   ├── config/asgi.py        aiguille /mcp -> FastMCP, le reste -> Django
│   ├── todos/models.py       modèle Todo (+ created_at / done_at)
│   ├── todos/serializers.py  serializer DRF, partagé par l'API REST ET les tools MCP
│   ├── todos/stats.py        regroupement par jour (semaine) ou par semaine (mois)
│   ├── todos/views.py        API REST classique  (/api/todos/, /api/todos/stats/)
│   ├── todos/mcp_server.py   ⭐ le serveur MCP : 1 ressource UI + 4 tools
│   ├── todos/management/commands/seed_todos.py   données factices
│   ├── run_stdio.py          point d'entrée pour Claude Desktop (stdio)
│   └── try_client.py         client MCP en Python pour voir ce que voit l'hôte
└── frontend/                 l'UI React
    ├── src/main.tsx          ⭐ connexion à l'hôte + choix de la vue selon le résultat
    ├── src/TodoList.tsx      vue liste
    ├── src/StatsView.tsx     vue graphique (Recharts)
    └── vite.config.ts        build en UN SEUL fichier : dist/mcp-app.html
```

## Le principe en 30 secondes

Une MCP App, c'est **deux primitives MCP classiques reliées entre elles** :

| Primitive | Ici | Rôle |
|---|---|---|
| **Ressource** | `ui://todos/app.html` | le HTML (React buildé), MIME `text/html;profile=mcp-app` |
| **Tool** | `show_todos` | porte `_meta.ui.resourceUri = "ui://todos/app.html"` |

```
 Utilisateur : "montre mes tâches"
        │
        ▼
 LLM ── tools/call show_todos ──────────────► Serveur MCP (Django)
        │                                      renvoie {"todos": [...]}
        ▼
 Hôte (Claude) voit _meta.ui.resourceUri
        ├── resources/read ui://todos/app.html ► renvoie le HTML React
        ├── affiche le HTML dans une iframe sandboxée
        └── pousse le résultat du tool dans l'iframe  (app.ontoolresult)
        
 Clic dans l'UI ── app.callServerTool("toggle_todo") ──► Hôte ──► Serveur
                    (postMessage)                         relaie   (Django ORM)
```

L'iframe ne parle **jamais** directement à ton serveur : tout passe par l'hôte
via `postMessage`. Pas besoin d'API, de CORS ni d'auth côté UI.

### Les 4 tools

| Tool | Visible par | Rôle | Renvoie |
|---|---|---|---|
| `show_todos` | LLM + UI | ouvre l'UI sur la liste | `{"todos": [...]}` |
| `show_stats` | LLM + UI | ouvre l'UI sur le graphique (`period`, `offset`) | `{"stats": {...}}` |
| `add_todo` | LLM + UI | ajoute une tâche | `{"todos": [...]}` |
| `toggle_todo` | UI seulement | `visibility=["app"]` : caché au LLM | `{"todos": [...]}` |

`show_todos` et `show_stats` pointent vers **la même ressource UI**. L'app React
regarde le `structuredContent` reçu : s'il contient `todos`, elle affiche la
liste ; s'il contient `stats`, le graphique. Les boutons « Semaine / Mois » et
« ‹ › » ne font que rappeler `show_stats` avec d'autres arguments.

### Historique et statistiques

- Chaque tâche a `created_at` et `done_at`. `done_at` est rempli quand on la
  coche et effacé quand on la décoche (`Todo.set_done`), via MCP comme via REST.
- `todos/stats.py` compte chaque tâche **dans la période où elle a été créée**,
  puis la classe « effectuée » ou « à faire » selon son état actuel.
  Semaine = du lundi au dimanche, une barre par jour. Mois = une barre par
  semaine, coupée aux bords du mois.
- Le texte du résultat contient aussi ces chiffres : tu peux demander à Claude
  « combien de tâches ai-je terminées le mois dernier ? ».

## Lancer

```bash
cd frontend && npm install && npm run build
```

```bash
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/python manage.py migrate
```

Données factices (~250 tâches sur 10 semaines, **supprime les tâches existantes**) :

```bash
cd backend && .venv/bin/python manage.py seed_todos
```

```bash
cd backend && .venv/bin/uvicorn config.asgi:application --port 8765
```

- Serveur MCP : `http://localhost:8765/mcp`
- API REST : `http://localhost:8765/api/todos/` et `http://localhost:8765/api/todos/stats/?period=month`

> Après chaque modif de `src/main.tsx`, relance `npm run build` (ou `npm run dev`
> qui rebuild en continu). Le serveur relit le fichier à chaque requête.

## Tester

**1. Voir ce que voit un hôte** (le `_meta` des tools, la ressource) :

```bash
cd backend && .venv/bin/python try_client.py
```

**2. Voir l'UI en local** avec l'hôte de test officiel
[basic-host](https://github.com/modelcontextprotocol/ext-apps/tree/main/examples/basic-host)
(cloner le repo `ext-apps`, puis dans `examples/basic-host`) :

```bash
npm install && SERVERS='["http://localhost:8765/mcp"]' npm run start
```

puis ouvrir http://localhost:8080. (C'est pour lui que `asgi.py` active le CORS :
il tourne dans le navigateur.)

**3. Dans Claude Desktop, en local (le plus simple)** : Claude Desktop lance
lui-même [run_stdio.py](backend/run_stdio.py) et lui parle via stdin/stdout
(pas d'uvicorn, pas de tunnel). Ajouter dans
`~/Library/Application Support/Claude/claude_desktop_config.json` :

```json
"mcpServers": {
  "todos": {
    "command": "/Users/scrip/Playground/learn_mcp/backend/.venv/bin/python",
    "args": ["/Users/scrip/Playground/learn_mcp/backend/run_stdio.py"]
  }
}
```

Quitter complètement Claude Desktop (⌘Q), le relancer, et dans l'onglet **Chat**
demander « montre-moi mes tâches ». Même code, même base SQLite : seul le
transport change (stdio au lieu de HTTP).

**4. Dans Claude (web ou Desktop) via HTTP** : Claude doit pouvoir joindre ton serveur en HTTPS, par exemple
via un tunnel :

```bash
cloudflared tunnel --url http://localhost:8765
```

puis Paramètres → Connecteurs → *Ajouter un connecteur personnalisé* avec
`https://<xxx>.trycloudflare.com/mcp`, et demander « montre-moi mes tâches ».

## Points à retenir

- **Côté Python** tout tient dans `app=AppConfig(resource_uri=...)` sur le tool et
  `@mcp.resource("ui://...")` qui renvoie le HTML. FastMCP met le bon MIME type.
- **Côté React** : `useApp()` établit la connexion, `app.ontoolresult` reçoit les
  données initiales, `app.callServerTool()` rappelle le serveur.
- **Un seul fichier HTML** : l'hôte charge une ressource, pas un site. D'où
  `vite-plugin-singlefile`. Pour charger des scripts externes il faudrait déclarer
  des domaines CSP (`AppConfig(csp=ResourceCSP(...))` sur la ressource).
- **Django + FastMCP** : les tools sync sont exécutés dans un thread par FastMCP,
  donc l'ORM Django marche tel quel. Le serializer DRF sert de validation commune
  à l'API REST et aux tools.
- ⚠️ Aucune auth ici : à ajouter avant d'exposer quoi que ce soit.
