# Use Node.js as base
FROM node:22.13.1

ARG NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt

COPY cert/zscaler.crt /usr/local/share/ca-certificates/
RUN cat /usr/local/share/ca-certificates/zscaler.crt >>/etc/ssl/certs/ca-certificates.crt

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the app
COPY . .

# Expose backend port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
