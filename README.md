# **Projet Allocine**

Web scraping d'informations de films à partir du site allocine.fr, nous y ajouterons les informations (synopsis et affiche de films) obtenues par requêtage de l'API publique OMDB.<br>

Après agrégation et nettoyage des données, les données sont stockées dans une base **MySQL** pour les données structurées (liste d'acteurs, réalisateurs, compositeurs, catégories, pays du film) et dans une base **MongoDB** pour les données non-structurées (textuelles comme le synopsis et les affiches de films).<br>

Réalisation d'une API pour exposer la base de données ainsi et offrir des outils de requêtes du type :
- Afficher la liste de films dans lesquels 2 acteurs ont joué,
- Afficher la liste de films réalisés par X dans lesquels l'acteur Y a joué,
- Afficher la liste de films dans lesquels a joué l'acteur X et dont la musique a été composée par Y,
- Filtrer par catégorie de films, année de production.

L'API offre la possibilité de combiner tous ces filtres.

<img src="https://github.com/Franck-LF/projectBlock1/blob/main/images/diag.png" alt="Drawing" style="width: 500px;"/>

---

## **Modules python à installer**

Le fichier **requirements.txt** contient la liste des modules python nécessaires à l'exécution des scripts.

---

## **Script d'extraction des données**

Fichier extractData.py<br>
<code>python ./extractData.py</code>

- web scraping des informations concernant les films sortis le mercredi de la semaine courante,
- requêtage de l'API OMDB pour collecter des informations supplémentaires (synopsis et affiche d'un film),
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

- Ajout dans la base MySQL des données structurées (films, acteurs, réalisateurs, compositeurs, catégories),
- Ajout dans la base MongoDB des données non-structurées (synopsis et url de l'affiche du film).

**Attention**<br>
Il faut déjà avoir construit la base de données MySQL, cela peut se faire à l'aide du fichier **movies.sql** et la commande : <code>C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" < movies.sql -u root -p</code>

---

## **Script de l'API**

Fichier api.py<br>
<code>uvicorn api:app --reload</code>

- Simule un serveur local pour lancer l'API,
- L'API expose la base de données,
- La documentation (http://127.0.0.1:8000/docs) explique comment formuler des requêtes.

---

