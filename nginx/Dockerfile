FROM alpine:3.21.3

RUN apk add --no-cache nginx=1.26.3-r0 && mkdir -p /run/nginx

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD [ "nginx", "-g", "daemon off;" ]

