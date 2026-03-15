FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Start the Next.js development server
CMD ["npm", "run", "dev"]