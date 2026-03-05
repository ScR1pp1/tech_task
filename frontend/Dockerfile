FROM --platform=linux/amd64 node:20-alpine

WORKDIR /app

# Устанавливаем build-зависимости
RUN apk add --no-cache python3 make g++ musl-dev gcc

# Копируем package.json
COPY package.json ./

# Устанавливаем зависимости
RUN npm install --no-fund --no-audit

# Принудительно создаем папку и копируем библиотеку в правильное место
RUN mkdir -p /app/node_modules/@oxc-parser/binding-linux-x64-musl && \
    npm install @oxc-parser/binding-linux-x64-musl --no-save && \
    cp -r /app/node_modules/@oxc-parser/binding-linux-x64-musl /app/node_modules/@oxc-parser/ || true

# Копируем остальной код
COPY . .

ARG NUXT_PUBLIC_API_BASE=http://localhost:8000
ARG NUXT_PUBLIC_API_KEY=dev-secret-key
ENV NUXT_PUBLIC_API_BASE=$NUXT_PUBLIC_API_BASE
ENV NUXT_PUBLIC_API_KEY=$NUXT_PUBLIC_API_KEY

# Проверяем что библиотека установлена
RUN ls -la /app/node_modules/@oxc-parser/ || true

CMD ["npm", "run", "dev"]