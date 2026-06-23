# syntax=docker/dockerfile:1
FROM node:20-alpine

WORKDIR /app

# Install dependencies first for better layer caching
COPY package.json ./
RUN npm install

# Copy the server and static frontend
COPY server.js ./
COPY src ./src

EXPOSE 3000

CMD ["npm", "start"]
