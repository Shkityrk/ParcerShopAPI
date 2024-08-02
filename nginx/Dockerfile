FROM nginx:1.23.3-alpine

RUN rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/
COPY parser_shop_api.crt /etc/nginx
COPY parser_shop_api.key /etc/nginx

CMD ["nginx", "-g", "daemon off;"]
