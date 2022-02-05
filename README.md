# demo_carte

## Contexte

À partir des données de l'INSEE et du ministère de l'éducation sur les nombres de naissances en France et les établissements scolaires, 
identifier des zones (regroupement de communes) en manque d'établissements scolaires. On se base sur le ratio nombre de naissances / nombre d'écoles.

## Principaux packages

* geopandas
* folium
* scipy

## Démonstration

#### Etapes

* Récupération des données des naissances, écoles et GeoJSON des communes
* Nettoyage des données (gestion des champs vides...)
* Aggrégation des communes pour recréer la carte des académies
* Affectation des communes sans école en les reliant à la commune la plus proche possédant une école
* Création de la carte
* 

#### Folium & Jupyter

![Alt Text](https://github.com/vesran/demo_carte/blob/main/demo.gif)

#### Streamlit & Folium

![](C:\Users\Light\Desktop\code\geo\imgs\streamlit.png)

Features de la carte :

* Visualisation des académies et le rapport naissance / écoles (nuances rouges)
* Affichage de la commune principale pour chaque académie (Académie de Aix-Marseille -> Marseille)
* Mise en relief des communes ayant une insuffisance d'écoles face au nombre de naissances (points rouge)
* Mise en relief des communes ayant un faible nombre de naissances face au nombre d'écoles (points bleu)
