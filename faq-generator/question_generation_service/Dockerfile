FROM python:3.8

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
        libatlas-base-dev gfortran nginx supervisor

RUN pip3 install uwsgi

COPY ./requirements.txt /project/requirements.txt

RUN /usr/local/bin/python -m pip install --upgrade pip \
        && pip3 install -r /project/requirements.txt

# RUN useradd --no-create-home nginx

# RUN rm /etc/nginx/sites-enabled/default
# RUN rm -r /root/.cache

# COPY server-conf/nginx.conf /etc/nginx/
# COPY server-conf/flask-site-nginx.conf /etc/nginx/conf.d/
# COPY server-conf/uwsgi.ini /etc/uwsgi/
# COPY server-conf/supervisord.conf /etc/supervisor/

COPY src /project/src
COPY articles /project/articles


RUN chown $(whoami):$(whoami) -R /root \
        # && chown -R $USER:$USER . \
        && chown root:root -R /project \
        && mkdir /project/transformers \
        && chmod -R 777 /project/transformers \
        && mkdir /project/cache \
        && chmod -R 777 /project/cache \
        && mkdir /project/models \
        && chmod -R 777 /project/models

# COPY models /project/models

# RUN mkdir -p /home/uwsgi \
#         && groupadd -r uwsgi && useradd -r -g uwsgi uwsgi \
#         && chown -R uwsgi:uwsgi /home/uwsgi \
#         && chmod -R og+rwx /home/uwsgi \
#         && mkdir /project/transformers \
#         && chown uwsgi:uwsgi -R /project \
#         && chmod 777 /project/transformers

# USER uwsgi

# WORKDIR /home/uwsgi

ENV HF_HOME=/project/cache
ENV TRANSFORMERS_CACHE=/project/transformers

WORKDIR /project

# CMD ["/usr/bin/supervisord"]

ENTRYPOINT [ "python" ] 
CMD ["-m", "src.server"]
