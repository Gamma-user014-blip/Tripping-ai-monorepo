FROM node:20-alpine AS builder

WORKDIR /app

# Copy workspace configuration and lockfile
COPY package*.json ./

# Copy shared and web-client package definitions
COPY shared/package*.json ./shared/
COPY apps/web-client/package*.json ./apps/web-client/

# Install all dependencies (hoisted to root)
RUN npm install

# Copy source code
COPY shared ./shared
COPY apps/web-client ./apps/web-client

# Build the web-client
WORKDIR /app/apps/web-client
# We can pass build args if needed, e.g., NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_API_URL="http://localhost:3001"
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# Final production stage
FROM node:20-alpine

WORKDIR /app

# Copy node_modules
COPY --from=builder /app/node_modules ./node_modules

# Copy web-client built files
WORKDIR /app/apps/web-client
COPY --from=builder /app/apps/web-client/.next ./.next
COPY --from=builder /app/apps/web-client/package*.json ./

EXPOSE 3000

CMD ["npm", "start"]
