# In frontend/Dockerfile (FINAL CORRECTED VERSION)

# --- Stage 1: Build the React App ---
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
# --- NEW LINE TO FORCE CONTEXT UPDATE ---
ARG CACHE_BUSTER
COPY . .
RUN npm run build

# --- Stage 2: Serve with Nginx ---
FROM nginx:1.25-alpine
# Copy built static files from Stage 1
COPY --from=builder /app/build /usr/share/nginx/html
# Copy Nginx config to handle React routing
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
# Nginx starts automatically