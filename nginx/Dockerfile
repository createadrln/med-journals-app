FROM nginx:alpine

# Remove default config and copy our custom config
RUN rm /etc/nginx/conf.d/default.conf
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy frontend build files
COPY dist /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
