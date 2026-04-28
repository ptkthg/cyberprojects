FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund || true
COPY . .
EXPOSE 3000
CMD ["npm","run","dev","--","-H","0.0.0.0","-p","3000"]
