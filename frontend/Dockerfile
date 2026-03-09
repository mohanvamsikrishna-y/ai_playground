FROM node:20-alpine AS builder

WORKDIR /app

# Accept build args for Next.js public env vars
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy built application and dependencies
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/next.config.ts ./next.config.ts

EXPOSE 3000

ENV NODE_ENV=production

# Next.js respects PORT env var automatically, but we set it explicitly
# Cloud Run sets PORT env var, default to 3000 for local development
CMD sh -c "PORT=${PORT:-3000} npm start"
