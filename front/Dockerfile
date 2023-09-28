FROM node:17.8-buster as build

WORKDIR /app
ADD front_page/ .

RUN npm install --build-from-resource
RUN npm run build


FROM node:17.8-buster as stage

WORKDIR /app

ADD app.js /app/app.js
COPY --from=build /app/dist /app/dist
COPY --from=build /app/node_modules /app/node_modules
COPY --from=build /app/package.json /app/package.json
COPY --from=build /app/package-lock.json /app/package-lock.json

RUN npm install
RUN npm install ovenplayer express connect-history-api-fallback
RUN npm install nodemon -g

EXPOSE 8080
ENV PORT 8080

CMD ["nodemon", "--ignore", "node_modules", "--ignore", "dist", "app.js"]