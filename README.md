# Facial emotion recognition APP 

Prérequis:
- Installer docker
- Python 3.11.4
- Un IDE: Vscode

NB : Consultez le fichier [DEVELOPER.md](DEVELOPER.md) pour comprendre l'architecture du projet.

Après exécution(ci-dessous), accéder à la page d'acceuil de l'application via [localhost:5000](localhost:5000)  (ou votre ip locale).
La documentation Swagger est accessible via cette adresse également [(localhost:5000)](http://localhost:5000). Nous y avons expliqué l'utilité de chaque endpoint.

Commandes d'exécution :

Pour créer une image docker de l'application api Facial emotion recognition api, dans un terminal, se placer dans le dossier du projet

```
docker build -t facial-emotion-recognition-api:latest .
```

Pour démarrer l'application et les tendems(prometheus/grafana) associés dans un conteneur docker:

```
docker-compose up -d
```
Pour arrêter le tendem prometheus/grafana:

```
docker-compose down -v
```

Pour supprimer tous les images et volumes entre deux compilations, effacer l'option -v

```
docker-compose down
```

Accéder à la page de monitoring Grafana via localhost:3000 (ou votre ip locale).

```
Utiliser identifiant : admin, mot de passe : grafana pour l'authentification.
```
Voici ci-dessous quelques images de l'évolution des métriques scrapées sur grafana.
![](monitoring/grafana/Angry_visuel.png)
![](monitoring/grafana/Courbe_Fearful_visuel.png)
![](monitoring/grafana/Courbe_surprised_visuel.png)
![](monitoring/grafana/Fearful_visuel.png)
![](monitoring/grafana/Fearful_visuel.png)
![](monitoring/grafana/Happy_visuel.png)
![](monitoring/grafana/Histogram_Happy_visuel.png)
![](monitoring/grafana/Histogram_Sad_visuel.png)
![](monitoring/grafana/model_precision.png)
![](monitoring/grafana/model_recall.png)
![](monitoring/grafana/Neutral_visuel.png)
![](monitoring/grafana/Sad_visuel.png)
![](monitoring/grafana/Surprised_visuel.png)

Accéder à la page de monitoring Prometheus via localhost:9090 (ou votre ip locale).
Voici ci-dessous quelques images de la présentation en Graphe sur Prometheus.
![](monitoring/prometheus/Capture_prom1.png)
![](monitoring/prometheus/Capture_prom2.png)
![](monitoring/prometheus/Capture_prom3.png)
