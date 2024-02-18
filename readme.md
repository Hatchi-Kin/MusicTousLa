# MusicTousLa

MusicTousLa est un bot Slack qui permet de selectionner au hasard la personne qui pourra proposer un morceau de musique à la fin de la prochaine réunion 'Tous là'.


## Utilisation

Pour intéragir avec le bot, il faut lui envoyer des commandes par mp.

Les commandes disponibles sont:
- `addme`: Pour s'ajouter à la liste des participants
- `removeme`: Pour se retirer de la liste des participants
- `randomdj`: Choisit au hasard le prochain DJ
- `isdj`: permet de voir qui est le DJ de la semaine
- `nextsong/<song_link>`: permet d'enregistrer l'URL du morceau choisit (ex, un lien youtube)
- `song`: permet de voir le morceau choisi par le DJ de la semaine
- `last`: permet de voir les 5 derniers morceaux choisis par les précedents DJs
- `participants`: permet de voir la liste des participants
- `help`: Pour afficher la liste des commandes


## manifest.yaml

```yaml
display_information:
  name: MusicTousLa
  description: Music
  background_color: "#2c4591"
features:
  bot_user:
    display_name: MusicTousLa
    always_online: false
oauth_config:
  scopes:
    bot:
      - app_mentions:read
      - chat:write
      - im:history
      - im:read
      - im:write
      - users:read
settings:
  event_subscriptions:
    bot_events:
      - app_mention
      - message.im
  interactivity:
    is_enabled: true
  org_deploy_enabled: false
  socket_mode_enabled: true
  token_rotation_enabled: false

```

## Docker

Pour faire tourner le bot dans un conteneur:

   ```
   docker compose up -d
   ```

## .venv

Pour faire tourner le bot en local dans un environement virtuel
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
```bash
python app.py
```