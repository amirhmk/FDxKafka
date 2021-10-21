FROM busybox
WORKDIR /usr/app
ADD ./keep-busy.sh ./keep-busy.sh
RUN chmod +x keep-busy.sh
CMD ["/usr/app/keep-busy.sh"]
