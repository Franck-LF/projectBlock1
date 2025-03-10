# **Projet Allocine**

Projet de webscrapping des informations de films à partir du site allocine.fr, seront ajoutées les informations (synopsis et affiche de films) obtenues par requêtage de l'API publique OMDB.
Après agrégation et nettoyage des données, les données sont stockées dans une base **MySQL** pour les données structurées (liste d'acteurs, réalisateurs, compositeurs, catégories, pays du film) et dans une base **MongoDB** pour les données non-structurées (textuelles comme le synopsis et les affiches de films).
Réalisation d'une API pour exposer la base de données ainsi construite, la documentation OpenAPI permet de faire des requêtes du type :
- Afficher la liste de films dans lesquels 2 acteurs ont joué,
- Afficher la liste de films réalisé par X dans lequel l'acteur Y à joué,
Des filtres identiques avec les compositeurs de musique de films, catégories de films, année de production, tous ces filtres pouvant être combinés ensemble.

![diag](https://github.com/Franck-LF/projectBlock1/blob/main/diag.png)

---

## **Script d'extraction des données**

extractData.py
<code>python ./extractData.py</code>

- web scraping des données
- requêtage de l'API OMDB pour collecter des informations (synopsis et affiche de films)
- écritude des données dans des fichiers csv

---

## **Script d'agrégation et nettoyage des données**

cleanData.py
<code>python ./cleanData.py</code>

- Ajout des données de requêtage d'OMDB aux données
- Formatage et normalisation des données
- écritude des données dans des fichiers csv

---

## **Script de mise en base des données**

insertData.py
<code>python ./insertData.py</code>

- Ajout des données dans la base MySQL
- Ajout des données dans la base MongoDB


---

