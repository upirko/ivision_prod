FROM tiangolo/node-frontend as build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install
COPY ./ ./

# RUN CI=true npm test
RUN npm run build

FROM nginx:1.15

COPY --from=build-stage /app/build/ /usr/share/nginx/html
COPY --from=build-stage /nginx.conf /etc/nginx/conf.d/default.conf