FROM oven/bun:1.1.30-alpine AS build

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . ./

ARG VITE_ENABLE_CAPTCHA
ARG VITE_RECAPTCHA_SITE_KEY
ENV VITE_ENABLE_CAPTCHA=${VITE_ENABLE_CAPTCHA}
ENV VITE_RECAPTCHA_SITE_KEY=${VITE_RECAPTCHA_SITE_KEY}

RUN bun run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
