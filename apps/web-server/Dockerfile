FROM node:20-alpine AS builder

WORKDIR /app

COPY apps/web-server/package*.json ./
RUN npm ci --only=production

COPY shared/ /app/shared/
COPY apps/web-server/tsconfig.json ./
COPY apps/web-server/src ./src

RUN npm install typescript @types/node @types/express @types/cookie-session @types/cors --save-dev
RUN npm run build

FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist

EXPOSE 3001

CMD ["npm", "start"]
