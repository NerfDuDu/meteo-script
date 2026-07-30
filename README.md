# meteo-script

## 1.Entrée
Lancez le script ```projet_meteo.py``` puis, comme demandé, entrez le nom d'une ville.

## 2.Requête API
Ensuite, par une première requête API sur __openmeteo.com__ et le paramètre __geocoding__, on récupère la latitude et la longitude de la ville en question ainsi que son pays.

Puis, une deuxième requête API nous permet d'avoir la température ainsi que le taux d'humidité dans la ville.

## 3. IA locale
De même, ces données sont envoyées à une IA (ici j'ai installé une IA locale gemma 4:e4b) qui nous envoie une petite phrase par rapport aux données.

## 4.Data Frame
Avec cela nous pouvons faire un data frame avec __Pandas__ pour afficher ces données.

## 5.Base de données
Enfin, ce data frame est stocké dans une base de données __SQLite__ qui est automatiquement créée si elle n'existe pas.

On peut aussi lire le contenu de la base de données avec le script ```lire_bdd.py```.
