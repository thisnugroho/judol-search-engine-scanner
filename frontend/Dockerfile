FROM oven/bun:1.1.30-alpine AS build

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . ./

ARG VITE_ENABLE_CAPTCHA
ARG VITE_RECAPTCHA_SITE_KEY
ENV VITE_ENABLE_CAPTCHA=true
ENV VITE_RECAPTCHA_SITE_KEY=6LdGEGAsAAAAAO98T4jMehRosP89mRMcx0DIlssq

RUN bun run build

FROM nginx:alpine

ARG APP_UID=1008
ARG APP_GID=1009

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx /run \
  && chown -R ${APP_UID}:${APP_GID} /var/cache/nginx /var/run /var/log/nginx /run /usr/share/nginx/html

EXPOSE 8080

USER ${APP_UID}:${APP_GID}

CMD ["nginx", "-g", "daemon off;"]
