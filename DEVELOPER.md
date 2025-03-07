# Dynamic Hedger API Monitoring

## Prérequis:
- Installer Docker
- Python
- Un IDE: VSCode
- Lire le fichier [README.md](README.md) pour comprendre la logique du projet.

## Organisation du projet :

- Le dossier [.github](.github) contient le pipeline pour l'intégration continue.
- Le dossier [app](app) contient tous les fichiers relatifs à notre application API.
- Le dossier [datas](datas) contient les données utilisées pour l'entraînement et le test du modèle LSTM.
- Le dossier [logs](logs) est un dossier serveur-BDD où sont sauvegardées les prédictions et performances du modèle.
- Le dossier [grafana](grafana) contient les configurations du tandem Grafana.
- Le dossier [prometheus](prometheus) contient les configurations du tandem Prometheus.
- Le dossier [monitoring](monitoring) contient quelques images de l'évolution des métriques de couverture financière affichées sur Prometheus (graphiques) et sur Grafana (tableaux de bord).

## Quelques commandes utiles :

### Créer une image Docker de l'application API Dynamic Hedger
Dans un terminal, se placer dans le dossier du projet :
```
docker build -t dynamic-hedger-api:latest .
```

### Démarrer tous les services de l'application dans un conteneur Docker
```
docker-compose up -d
```

### Mode développement
En mode développement, il est préférable de démarrer l'application via VSCode ou PyCharm, ce qui permet un meilleur débogage si besoin.

**(Attention !)** Il faudra commenter le service FastAPI dans le `docker-compose.yml` qui lance directement l'application dans Docker, afin de libérer le port 5000.

### Installer Prometheus et Grafana via Docker (si besoin)
```
docker pull prom/prometheus
```
```
docker pull grafana/grafana
```

### Démarrer le tandem Prometheus/Grafana
```
docker-compose up
```

### Arrêter le tandem Prometheus/Grafana
```
docker-compose down -v
```

### Supprimer toutes les images et volumes entre deux compilations
```
docker-compose down
```

Tout est configuré pour fonctionner avec l'application démarrée en mode développement, c'est-à-dire via PyCharm ou VSCode.

