FROM node AS builder

COPY ./package.json /app/package.json
COPY ./package-lock.json /app/package-lock.json
COPY ./ionic.config.json /app/ionic.config.json
COPY ./tsconfig.json /app/tsconfig.json

WORKDIR /app

RUN npm install -g @ionic/cli
RUN npm install

COPY ./build-app.sh /app/build-app.sh
COPY ./public /app/public
COPY ./src /app/src

RUN ./build-app.sh

FROM nginx:latest

ENV API_HOST=127.0.0.1
ENV API_PORT=8080

COPY ./nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /app/build /usr/share/nginx/html
