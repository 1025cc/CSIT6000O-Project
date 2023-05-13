# Build stage
FROM node:14 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
RUN npm run build

# Run stage
FROM node:14
WORKDIR /app
COPY --from=build /app/build ./build
RUN npm install -g http-server
EXPOSE 8888
CMD ["http-server", "build", "-p", "8888"]