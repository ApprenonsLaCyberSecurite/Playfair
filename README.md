# Playfair
Cryptanalyse de Playfair avec un algorithme génétique

Ici vous trouverez les ressources nécessaires pour reproduire ce qui est fait dans la vidéo Youtube disponible ici : https://www.youtube.com/@ApprenonsLaCyberSecurite

1/ Créez votre base et la table `quadgramme` :<br>
```sql
CREATE TABLE IF NOT EXISTS `quadgramme` (
  `quadgramme` varchar(4) COLLATE utf8mb4_unicode_ci NOT NULL,
  `occurrences` int NOT NULL,
  `frequence` float NOT NULL,
  `score` float NOT NULL,
  PRIMARY KEY (`quadgramme`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```
2/ Récupérer le corpus de textes `corpus.zip` et dézippez le dans votre répertoire de travail.<br>
3/ lancer le script python `compteurQuadgramme.py` pour populer la base avec les scores des quadgrammes<br>
4/ lancer le script python `cryptanalysePlayfair_v2.py` pour déchiffrer le texte<br>

$$\\color{red}\\textit{N'oubliez pas de changer le host, le login, le mot de passe et le nom de la base de donnée dans chacun des scripts python avec votre paramétrage avant de les lancer}$$
