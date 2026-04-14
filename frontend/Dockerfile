# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

# Build args for env vars
ARG NEXT_PUBLIC_BASE_API_URL=http://localhost:8000/api
ARG NEXT_PUBLIC_BASE_DATA_DRAGON_URL=https://ddragon.leagueoflegends.com/cdn/14.20.1/data/en_US/

ENV NEXT_PUBLIC_BASE_API_URL=$NEXT_PUBLIC_BASE_API_URL
ENV NEXT_PUBLIC_BASE_DATA_DRAGON_URL=$NEXT_PUBLIC_BASE_DATA_DRAGON_URL

COPY . .
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]