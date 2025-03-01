FROM node:22.13.1

# ARG NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt

# COPY cert/zscaler.crt /usr/local/share/ca-certificates/
# RUN cat /usr/local/share/ca-certificates/zscaler.crt >>/etc/ssl/certs/ca-certificates.crt

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

VOLUME [ "/app/data" ]

CMD ["node", "server.js"]
