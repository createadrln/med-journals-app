# Use Node.js as base
FROM node:18

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
