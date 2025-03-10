# **Projet Allocine**

Projet de webscrapping des informations de films à partir du site allocine.fr, seront ajoutées les informations (synopsis et affiche de films) obtenues par requêtage de l'API publique OMDB.<br>
Après agrégation et nettoyage des données, les données sont stockées dans une base **MySQL** pour les données structurées (liste d'acteurs, réalisateurs, compositeurs, catégories, pays du film) et dans une base **MongoDB** pour les données non-structurées (textuelles comme le synopsis et les affiches de films).<br>
Réalisation d'une API pour exposer la base de données ainsi construite, la documentation OpenAPI permet de faire des requêtes du type :
- Afficher la liste de films dans lesquels 2 acteurs ont joué,
- Afficher la liste de films réalisé par X dans lequel l'acteur Y à joué,<br>
- Afficher la liste de films dans lesquels ont joué l'acteur X et dont la musique a été composée par Y.<br>

L'API offre la possibilité de combiner ces filtres avec des filtres classiques (filtre de catégorie de films, année de production).

<img src="https://github.com/Franck-LF/projectBlock1/blob/main/images/diag.png" alt="Drawing" style="width: 500px;"/>

---

## **Modules python à installer**

Le fichier **requirements.txt** contient la liste des modules python nécessaires à l'exécution des scripts.

---

## **Script d'extraction des données**

Fichier extractData.py<br>
<code>python ./extractData.py</code>

- web scraping des données,
- requêtage de l'API OMDB pour collecter des informations (synopsis et affiche d'un film),
- écritude des données dans des fichiers csv.

---

## **Script d'agrégation et nettoyage des données**

Fichier cleanData.py<br>
<code>python ./cleanData.py</code>

- Ajout des données de requêtage d'OMDB aux données déjà collectées sur Allociné,
- Formatage et normalisation des données,
- écriture des données dans des fichiers csv.

---

## **Script de mise en base des données**

Fichier insertData.py<br>
<code>python ./insertData.py</code>

- Ajout des données dans la base MySQL,
- Ajout des données dans la base MongoDB.

**Attention**<br>
Il faut déjà avoir construit la base de données MySQL, cela peut se faire à l'aide du fichier **movies.sql** et la commande : <code>C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" < movies.sql -u root -p</code>

---

## **Script de l'API**

Fichier api.py<br>
<code>uvicorn api:app –reload</code>

- Simule un serveur local pour lancer l'API,
- l'API expose la base de données.

---

