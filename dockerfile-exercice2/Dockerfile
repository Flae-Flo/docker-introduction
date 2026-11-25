# Construction

FROM node:24.22.3-alpine3.24 AS build

WORKDIR /app

COPY . /app


RUN npm ci \
    && npm run build 

# Étape 2 : Exécution de l'application

FROM nginxinc/nginx-unprivileged:1.30-alpine

# Mettre à jour les paquets système

USER root

RUN apk upgrade --no-cache

# Revenir à un utilisateur non privilégié

USER 101

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080