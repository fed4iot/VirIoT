FROM nginx:latest
COPY ./nginx.conf   /etc/nginx/nginx.conf
COPY ./data /data
RUN dd if=/dev/urandom of=/data/dummy.img bs=1024000 count=100
EXPOSE 8081