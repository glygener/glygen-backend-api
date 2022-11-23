FROM python:3.6.8

WORKDIR /app

ENV FLASK_APP=glygen

ENV FLASK_ENV=production

COPY ./ts-1.0.2.tar.gz .

COPY ./ncbi-blast-2.6.0+-x64-linux.tar.gz .

COPY ./job_submitters.tar.gz .

RUN /bin/tar xvf ts-1.0.2.tar.gz

RUN /bin/tar xvf ncbi-blast-2.6.0+-x64-linux.tar.gz

RUN /bin/tar xvf job_submitters.tar.gz

WORKDIR /app/ts-1.0.2

RUN make 

RUN make install

WORKDIR /app

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./glygen-1.0-py3-none-any.whl .

RUN pip3 install glygen-1.0-py3-none-any.whl

RUN mkdir -p /data/shared/glygen

RUN mkdir -p /usr/local/var/glygen-instance

COPY ./config.glygen_tst.py /usr/local/var/glygen-instance/config.prd.py

COPY . .

ENTRYPOINT FLASK_APP=glygen gunicorn -b :80 'glygen:create_app()'
