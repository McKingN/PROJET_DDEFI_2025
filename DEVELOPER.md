# Facial emotion recognition API Monitoring

Prérequis:
- Installer docker
- Python
- Un IDE: Vscode
- Lire le fichier [README.md](README.md) pour connaitre la logique du projet.


Organisation du projet :

- Le dossier [.github](.github) contient le pipeline pour l'intégration continue.

- Le dossier [app](app) contient tous les fichiers relatives à notr application API.

- Le dossier [datas](datas) contient les données utilisées dans le cadre de l'entrainement et du test de notre modèle.

- Le dossier [uploaded_images](uploaded_images) est un dossier server-bdd qui où on sauvegarde les images prises ou téléversées afin de les traiter par le model.

- Le dossier [grafana](grafana) contient les configurations du tendem grafana.

- Le dossier [prometheus](prometheus) contient les configurations du tendem prometheus.

- Le dossier [monitoring](monitoring) contient quelques images de l'évolution de nos métriques sur prometheus(graph) et sur grafana(dashboard) quand nous avons déployé.

Quelques commandes utiles :

Pour créer une image docker de l'application api Facial emotion recognition api, dans un terminal, se placer dans le dossier du projet

```
docker build -t facial-emotion-recognition-api:latest .
```

Pour démarrer tous les services de l'application dans un conteneur docker:

```
docker-compose up -d
```

En mode dev, le plus simple c'est de démarrer l'application via vscode ou pycharm, cela nous permet de debugger plus facilement si besoin.

(Attention ! Il faudra commenter le service fastapi du docker-compose qui lançait directement l'application dans docker pour que le port 5000 soit libéré.)

Si vous ne les avez pas, pour installer le tendem prometheus/grafana via docker:

```
docker pull prom/prometheus
```
```
docker pull grafana/grafana
```

Pour démarrer le tendem prometheus/grafana:

```
docker compose up 
```
Pour arrêter le tendem prometheus/grafana:

```
docker-compose down -v
```

Pour supprimer tous les images et volumes entre deux compilations, effacer l'option -v

```
docker-compose down
```


Tout est configuré pour fonctionner avec l'application démarrée en mode dev, c'est à dire démrée avec Pycharm ou vscode.
