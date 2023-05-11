# Build stage
FROM node:14 as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Run stage
FROM node:14
WORKDIR /app
COPY --from=build /app/build ./build
RUN npm install -g http-server
EXPOSE 8888
CMD ["http-server", "build", "-p", "8888"]
