FROM node:20-alpine AS builder

WORKDIR /app

# Copy workspace configuration and lockfile
COPY package*.json ./

# Copy shared and all apps package definitions to ensure workspace awareness
COPY shared/package*.json ./shared/
COPY apps/web-server/package*.json ./apps/web-server/

# Install all dependencies (hoisted to root)
RUN npm install

# Copy source code for shared and web-server
COPY shared ./shared
COPY apps/web-server ./apps/web-server

# Build the web-server
WORKDIR /app/apps/web-server
RUN npm run build

# Final production stage
FROM node:20-alpine

WORKDIR /app

# Copy built node_modules (contains symlinks)
COPY --from=builder /app/node_modules ./node_modules

# Copy compiled artifacts for web-server and shared
COPY --from=builder /app/apps/web-server/dist ./dist

# Reconstruct the shared package where the symlink points
# node_modules/@monorepo/shared -> /app/shared
WORKDIR /app/shared
COPY --from=builder /app/shared/package*.json ./
COPY --from=builder /app/apps/web-server/dist/shared/ ./

# Back to app root
WORKDIR /app
COPY --from=builder /app/apps/web-server/package*.json ./

COPY .env .

EXPOSE 3001

CMD ["npm", "start"]
