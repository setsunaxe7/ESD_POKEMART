FROM node:18

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY middleware.js .

CMD ["node", "middleware.js"]