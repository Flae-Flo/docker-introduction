# Persistance des données : volumes et Bind Mounts

À la fin du TP, vous devez savoir :

1. expliquer ce qui arrive aux fichiers présents dans la couche inscriptible d'un conteneur supprimé
2. créer, monter, inspecter et supprimer un volume nommé
3. vérifier la persistance des données malgré la suppression d'un conteneur
4. partager des données entre conteneurs
5. utiliser un Bind Mount pour servir des fichiers locaux avec Nginx
6. distinguer les usages des volumes nommés et des Bind Mounts
7. persister une base de données PostgreSQL lors de la recréation de son conteneur.

Ces exercices vous aideront à mieux comprendre la gestion des volumes dans Docker. Prenez le temps de tester et d'explorer chaque commande pour renforcer votre compréhension.

---

## Exercice 1 - Comprendre la perte des données sans volume

**Objectif :** identifier la limite de la couche inscriptible d'un conteneur.

### Manipulations

1. Créez un conteneur Alpine, écrivez un fichier puis affichez son contenu :

```sh
docker run --name tp-sans-volume alpine sh -c "echo Donnee-temporaire > /tmp/temoin.txt && cat /tmp/temoin.txt"
```

2. Supprimez le conteneur :

```sh
docker rm tp-sans-volume
```

3. Démarrez un **nouveau** conteneur à partir de la même image et vérifiez l'absence du fichier :

```sh
docker run --rm alpine sh -c "if test -f /tmp/temoin.txt; then echo PRESENT; else echo ABSENT; fi"
```

### Questions

- Quel résultat obtenez-vous dans le premier conteneur, puis dans le second ?
Voilà ce que j'obtiens lors de la création du premier conteneur : 
"docker run --name tp-sans-volume alpine sh -c "echo Donnee-temporaire > /tmp/temoin.txt && cat /tmp/temoin.txt"
Unable to find image 'alpine:latest' locally
latest: Pulling from library/alpine
881fc932939e: Pull complete
86ff264fe568: Download complete
c35a7d82b8fa: Download complete
Digest: sha256:f59abe656b692d901e184be3445e084786602108599d2a51d229c0f5a48c71bf
Status: Downloaded newer image for alpine:latest
Donnee-temporaire"
On voit qu'il y a bien "Donnee-temporaire" qui apparait 
Puis 
"docker run --rm alpine sh -c "if test -f /tmp/temoin.txt; then echo PRESENT; else echo ABSENT; fi"
ABSENT"

- Pourquoi utiliser la même image Alpine ne suffit-il pas à retrouver le fichier ?
Même si on utilise la même image Alpine, chaque conteneur possède son propre file system isolé. Le fichier temoin.txt est créé dans le premier conteneur mais pas dans l'image. Donc si on supprime le conteneur, on supprime tout ce qui est dedans donc tous les fichiers

- Dans quels cas la perte de ces données poserait-elle problème ?
Si jamais les documents sont importants, qu'on a besoin de garder ces données

**Résultat attendu :** `Donnee-temporaire`, puis `ABSENT`.

---

## Exercice 2 - Créer et inspecter un volume nommé

**Objectif :** apprendre à créer, lister et inspecter un volume géré par Docker.

```sh
docker volume create tp-volume
docker volume ls
docker volume inspect tp-volume
```

### Questions

- Quelle est la valeur de `Name` ?
La valeur de Name est "tp-volume", c'est le nom donné au volume lors de sa création

- À quoi correspondent `Driver`, `Mountpoint` et `Scope` ?
Driver correspond au pilote utilisé pour gérer le volume, ici "local"
Mountpoint correspond au chemin où sont stockées les données du volume
Scope correspond à la portée du volume, ici "local" donc propre à l'hôte Docker

- Sur Docker Desktop, pourquoi le chemin `Mountpoint` n'est-il pas nécessairement directement visible dans l'explorateur de fichiers Windows ou Finder ?
Parce que Docker Desktop utilise une machine virtuelle Linux. Donc le chemin correspond à un répertoire dans cette VM et non directement sur mon Windows ou si j'étais sur un mac

- Le volume est-il lié à un conteneur particulier ?
Non, le volume est indépendant du conteneur. On peut donc supprimer le conteneur sans perdre les données du volume et réutiliser le même volume dans un autre conteneur

**Résultat attendu :** un volume `tp-volume` existe, généralement avec le driver `local`.

---

## Exercice 3 - Vérifier la persistance avec un volume

**Objectif :** conserver un fichier après suppression et remplacement d'un conteneur.

1. Créez un conteneur utilisant le volume `tp-volume` et écrivez un fichier dedans :

```sh
docker run --name tp-ecrivain --mount type=volume,source=tp-volume,target=/data alpine sh -c "echo Donnee-persistante > /data/temoin.txt && cat /data/temoin.txt"
```

2. Supprimez ce conteneur :

```sh
docker rm tp-ecrivain
```

3. Montez le même volume dans un nouveau conteneur et relisez le fichier :

```sh
docker run --rm --mount type=volume,source=tp-volume,target=/data alpine cat /data/temoin.txt
```

4. Inspectez de nouveau le volume :

```sh
docker volume inspect tp-volume
```

### Questions

- Le fichier subsiste-t-il après suppression du premier conteneur ?
Oui, même après avoir supprimé le premier conteneur, on retrouve bien "Donnee-persistante" dans le second conteneur

- Quelle différence constatez-vous avec l'exercice 1 ?
Dans l'exercice 1, on ne retrouvait pas le fichier lors de la création du second conteneur. Là, grâce au volume, on retrouve bien le fichier même si ce n'est pas le même conteneur

- Quel composant porte la durée de vie du fichier : le conteneur ou le volume ?
C'est le volume, car le fichier est stocké dans celui-ci et non directement dans le file system du conteneur. Donc tant qu'on conserve le volume, on conserve les données même si on supprime le conteneur

**Résultat attendu :** `Donnee-persistante` est affiché depuis le second conteneur.

---

## Exercice 4 - Partager un volume entre deux conteneurs

**Objectif :** montrer que deux conteneurs peuvent accéder au même volume.

1. Créez un volume partagé :

```sh
docker volume create tp-partage
```

2. Démarrez un conteneur « écrivain » qui reste actif :

```sh
docker run -d --name tp-ecrivain-partage --mount type=volume,source=tp-partage,target=/data alpine sleep 3600
```

3. Depuis ce premier conteneur, écrivez un fichier :

```sh
docker exec tp-ecrivain-partage sh -c "echo Message-du-conteneur-A > /data/message.txt"
```

4. Démarrez un autre conteneur « lecteur » utilisant le même volume :

```sh
docker run --rm --mount type=volume,source=tp-partage,target=/data,readonly alpine cat /data/message.txt
```

5. Modifiez le contenu via le premier conteneur et relisez-le via le second :

```sh
docker exec tp-ecrivain-partage sh -c "echo Message-modifie > /data/message.txt"
docker run --rm --mount type=volume,source=tp-partage,target=/data,readonly alpine cat /data/message.txt
```

6. Supprimez le conteneur permanent :

```sh
docker rm -f tp-ecrivain-partage
```

### Questions

- Les deux conteneurs voient-ils les mêmes fichiers ?
Oui, on voit bien que le second conteneur affiche "Message-du-conteneur-A" puis "Message-modifie" après avoir modifié le fichier depuis le premier conteneur

- Pourquoi le montage du lecteur utilise-t-il `readonly` ?
Parce qu'on veut seulement que le second conteneur puisse lire les données du volume et non les modifier ou les supprimer

- Quels risques existeraient si deux applications modifiaient simultanément les mêmes fichiers ?
On risquerait d'écraser les modifications faites par l'autre application, de perdre des données ou de corrompre les fichiers

**Résultat attendu :** le lecteur affiche successivement `Message-du-conteneur-A` puis `Message-modifie`.

---

## Exercice 5 - Découvrir les Bind Mounts avec Nginx

**Objectif :** monter un dossier de l'ordinateur dans un conteneur et observer les modifications en direct.

### A. Préparer les fichiers

1. Créez dans votre éditeur un dossier `site-web` à l'emplacement de votre choix.
2. Ajoutez un fichier `index.html` contenant :

```html
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <title>TP Bind Mount</title>
  </head>
  <body>
    <h1>Version 1 — Bonjour Docker !</h1>
  </body>
</html>
```

3. Dans votre terminal, placez-vous **à l'intérieur du dossier `site-web`** avant de lancer Nginx. Vérifiez que `index.html` s'y trouve.

### B. Démarrer Nginx avec un Bind Mount

**Windows — PowerShell :**

```powershell
docker run -d --name tp-nginx-bind -p 8085:80 --mount "type=bind,source=$((Get-Location).Path),target=/usr/share/nginx/html,readonly" nginx:alpine
```

**macOS / Linux — zsh ou bash :**

```bash
docker run -d --name tp-nginx-bind -p 8085:80 --mount "type=bind,source=$(pwd),target=/usr/share/nginx/html,readonly" nginx:alpine
```

**Remarque :** si vous utilisez WSL sur Windows, lancez la commande macOS/Linux depuis le terminal WSL et travaillez dans un dossier accessible au moteur Docker. Si Docker Desktop vous demande d'autoriser le partage du répertoire, acceptez pour votre dossier de TP.

### C. Observer

1. Ouvrez `http://localhost:8085` dans votre navigateur.
2. Modifiez `index.html` : remplacez `Version 1` par `Version 2 — Fichier modifié sur mon ordinateur`.
3. Enregistrez et actualisez la page, **sans recréer le conteneur**.
4. Examinez le montage :

```sh
docker inspect tp-nginx-bind
```

5. Supprimez le conteneur :

```sh
docker rm -f tp-nginx-bind
```

6. Vérifiez que `index.html` reste présent dans le dossier local.

### Questions

- Pourquoi la page change-t-elle sans reconstruire une image ?
Parce qu'avec le Bind Mount, le conteneur utilise directement le fichier index.html présent sur mon ordi 
Donc quand je modifie le fichier en local et que j'actualise ma page, on voit directement les modifications sans avoir besoin de recréer le conteneur ou l'image.

- Dans `docker inspect`, quelle est la valeur du type de montage (`Type`) ?
La valeur de Type est "bind", on le retrouve dans la partie "Mounts" du résultat de la commande

- Que signifie `readonly` ?
Ça signifie que le conteneur a accès aux fichiers en lecture seule

- Les fichiers du dossier local sont-ils supprimés avec le conteneur ?
Non, le fichier index.html est toujours présent dans mon dossier site-web, stockés sur mon ordinateur et donc indépendants du conteneur

**Résultat attendu :** les modifications locales sont visibles après actualisation et le fichier reste sur l'hôte.

---

## Exercice 6 - Comparer Bind Mount et volume nommé

**Objectif :** observer deux modes de montage et savoir justifier un choix.

1. En restant dans le dossier `site-web`, lancez un conteneur Nginx **sans** Bind Mount :

```sh
docker run -d --name tp-nginx-sans-bind -p 8086:80 nginx:alpine
```

2. Comparez `http://localhost:8086` à la page personnalisée vue dans l'exercice 5.
3. Affichez le contenu HTML par défaut dans ce conteneur :

```sh
docker exec tp-nginx-sans-bind ls /usr/share/nginx/html
```

4. Supprimez le conteneur :

```sh
docker rm -f tp-nginx-sans-bind
```

5. Complétez ce tableau :

| Situation                                                    | Volume nommé, Bind Mount ou aucun montage ? | Justification |
| ------------------------------------------------------------ | ------------------------------------------- | ------------- |
| Faire persister des fichiers de base de données              | Volume nommé                                | Pour conserver les données même si on supprime le conteneur             |

| Voir instantanément les modifications d'un site HTML local   | Bind Mount                                  | Pour retrouver directement les modifications faites sur mon ordinateur               |

| Exécuter une application temporaire sans données à conserver | Aucun montage                               | On n'a pas besoin de conserver les données              |

| Conserver des données lors de la recréation d'un conteneur   | Volume nommé ou Bind Mount                  | Les données sont stockées indépendamment du conteneur               |

### Questions

- Quelle est la différence entre un chemin géré par Docker et un chemin explicitement choisi sur l'hôte ?
Avec un volume nommé, c'est Docker qui gère l'emplacement où sont stockées les données 
Avec un Bind Mount, c'est moi qui choisis directement le dossier sur mon ordinateur

- Un volume nommé et un Bind Mount permettent-ils tous les deux la persistance ?
Oui, dans les deux cas les données sont stockées indépendamment du conteneur 
Donc même si on supprime le conteneur, on conserve les données

- Pourquoi faut-il éviter de confondre « persistance » et « sauvegarde » ?
Parce que même si les données sont persistantes, elles peuvent être supprimées ou corrompues
Si on n'a pas fait de sauvegarde de ces données, on risque de ne pas pouvoir les récupérer

---

## Exercice 7 - Supprimer des volumes sans affecter d'autres projets

**Objectif :** distinguer suppression d'un conteneur et suppression des données d'un volume.

1. Créez un volume de test et écrivez-y une donnée :

```sh
docker volume create tp-nettoyage
docker run --rm --mount type=volume,source=tp-nettoyage,target=/data alpine sh -c "echo A-conserver > /data/important.txt"
```

2. Vérifiez que la donnée est présente :

```sh
docker run --rm --mount type=volume,source=tp-nettoyage,target=/data alpine cat /data/important.txt
```

3. Supprimez **uniquement** ce volume de test :

```sh
docker volume rm tp-nettoyage
```

4. Vérifiez qu'il n'existe plus :

```sh
docker volume inspect tp-nettoyage
```

Une erreur `no such volume` est ici le **résultat attendu**.

5. Recréez un volume avec ce nom et inspectez son contenu :

```sh
docker volume create tp-nettoyage
docker run --rm --mount type=volume,source=tp-nettoyage,target=/data alpine ls -la /data
```

### Questions

- Le fichier `important.txt` est-il encore présent après recréation du volume ?
Non, on voit bien que le dossier /data est vide après avoir recréé le volume 
Même si on utilise le même nom, c'est un nouveau volume qui ne contient pas les anciennes données

- Pourquoi `docker volume prune --all` peut-il être risqué ?
Parce que cette commande supprime tous les volumes qui ne sont utilisés par aucun conteneur. On risque donc de supprimer des volumes appartenant à d'autres projets et de perdre des données

- Que faut-il faire avant de supprimer le volume d'une application de production ?
Il faut vérifier que le volume n'est plus nécessaire à l'application et faire une sauvegarde des données avant de le supprimer pour pouvoir les récupérer si besoin

**Attention :** n'exécutez pas `docker volume prune --all` durant ce TP. La commande pourrait supprimer les volumes nommés inutilisés d'autres projets.

---

# Atelier - Garantir la persistance d'une base PostgreSQL

## Contexte

Une entreprise utilise PostgreSQL pour conserver les données de son application. Lors d'une maintenance, l'équipe doit remplacer le conteneur PostgreSQL sans perdre les enregistrements de la base.

Vous êtes chargé de préparer le stockage, de lancer la base, d'insérer des données, de remplacer le conteneur et de prouver que les données sont toujours présentes.

## Objectifs

- Déployer PostgreSQL dans un conteneur Linux.
- Monter un volume nommé à l'emplacement des données.
- Créer une table et y insérer des données.
- Supprimer puis recréer le conteneur.
- Retrouver les mêmes données après remplacement.
- Expliquer les limites de cette persistance et les besoins de sauvegarde.

## Contraintes techniques

- Utilisez l'image **`postgres:17`**.
- N'utilisez pas Docker Compose pour cet atelier.
- Utilisez un volume nommé **`tp-postgres-data`** monté à **`/var/lib/postgresql/data`**. Ce point de montage correspond à PostgreSQL 17 ; il diffère du comportement de certaines images PostgreSQL plus récentes.
- Nom du conteneur : **`tp-postgres`**.
- Base de données : **`tpdb`**.
- Utilisateur : **`tpuser`**.
- Mot de passe de laboratoire : **`TpDocker2026!`**, réservé à cet exercice (ne jamais réutiliser un mot de passe réel).
- N'exposez pas inutilement le port 5432 vers l'ordinateur : toutes les commandes SQL seront exécutées via `docker exec`.

## Missions à accomplir

### Mission 1 - Préparer le stockage

1. Créez le volume `tp-postgres-data`.
2. Inspectez-le et notez le driver utilisé.

### Mission 2 - Démarrer la base de données

1. Exécutez un conteneur PostgreSQL 17 nommé `tp-postgres`.
2. Configurez `POSTGRES_USER`, `POSTGRES_PASSWORD` et `POSTGRES_DB` avec les valeurs imposées.
3. Montez le volume nommé à `/var/lib/postgresql/data`.
4. Vérifiez que le conteneur est en cours d'exécution, puis que PostgreSQL accepte les connexions.

**Indication :** vous pouvez utiliser `docker logs tp-postgres` et `docker exec tp-postgres pg_isready -U tpuser -d tpdb`. Le service peut prendre quelques secondes pour s'initialiser.

### Mission 3 - Créer et alimenter une table

À l'aide de `psql`, créez la table :

```sql
CREATE TABLE apprenants (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    formation VARCHAR(100) NOT NULL
);
```

Insérez au moins trois lignes :

```sql
INSERT INTO apprenants (nom, formation)
VALUES
('Alice', 'Docker'),
('Bilal', 'DevOps'),
('Chloe', 'Cloud');
```

Vérifiez :

```sql
SELECT * FROM apprenants ORDER BY id;
```

**Indication multiplateforme :** depuis PowerShell, bash ou zsh, exécutez une instruction SQL avec :

```sh
docker exec tp-postgres psql -U tpuser -d tpdb -c "SELECT * FROM apprenants ORDER BY id;"
```

Pour ouvrir une session SQL interactive :

```sh
docker exec -it tp-postgres psql -U tpuser -d tpdb
```

Pour quitter `psql`, saisissez `\q`.

### Mission 4 - Simuler une maintenance

1. Supprimez le **conteneur** `tp-postgres` sans supprimer le volume.
2. Vérifiez que le volume nommé existe toujours.
3. Recréez le conteneur `tp-postgres` avec **la même image**, **les mêmes paramètres de base** et **le même volume**.
4. Attendez que PostgreSQL accepte les connexions.
5. Exécutez la requête `SELECT * FROM apprenants ORDER BY id;`.

**Critère de réussite :** les trois lignes initiales sont toujours présentes.

### Mission 5 - Analyser

Répondez :

1. Pourquoi les données sont-elles conservées alors que le conteneur a été supprimé ?
Parce que les données sont enregistrées dans un volume nommé géré par Docker et non dans la couche du conteneur 
On peut donc supprimer et recréer le conteneur sans perdre les données

2. Que se passerait-il si vous recréiez PostgreSQL avec un **nouveau volume vide** ?
PostgreSQL initialiserait une nouvelle bdd vide 

3. Pourquoi le volume ne remplace-t-il pas une sauvegarde ?
Parce que même si les données sont persistantes, le volume peut être supprimé accidentellement, les données peuvent être corrompues ou autre du genre

4. Quels risques présentent les modifications de version majeure de PostgreSQL ?
Il peut y avoir des problèmes de compatibilité entre les différentes versions majeures de PostgreSQL

5. Dans quel cas serait-il pertinent d'utiliser un Bind Mount à la place du volume nommé ?
Il serait pertinent d'utiliser un Bind Mount si on souhaite choisir précisément l'emplacement où sont stockées les données

---

## Nettoyage final

Après validation du TP, supprimez **uniquement** les ressources de cet exercice, si vous n'avez plus besoin de leurs données. **Attention : la suppression des volumes efface leurs données.**

```sh
docker rm -f tp-postgres
docker volume rm tp-volume tp-partage tp-nettoyage tp-postgres-data
```

Si `tp-postgres` n'existe déjà plus, le premier appel peut afficher une erreur sans empêcher la suppression ciblée des volumes. Vérifiez d'abord qu'aucun autre conteneur ne référence les volumes.

## Sources techniques

- Volumes Docker : https://docs.docker.com/engine/storage/volumes/
- Bind Mounts : https://docs.docker.com/engine/storage/bind-mounts/
- Nettoyage des volumes : https://docs.docker.com/reference/cli/docker/volume/prune/
- Image officielle PostgreSQL : https://hub.docker.com/_/postgres
