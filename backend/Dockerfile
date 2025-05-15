FROM node:22.14.0

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN npm install --global corepack@latest
RUN corepack enable pnpm
RUN pnpm install

COPY . .

VOLUME [ "/app/data" ]

CMD ["node", "server.js"]
