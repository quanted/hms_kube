FROM continuumio/miniconda3:4.10.3p0-alpine as base

ENV GDAL_VERSION=3.4.1
ENV CONDA_ENV_BASE=pyenv

RUN apk update
RUN apk upgrade
RUN apk add --no-cache geos gdal cmake git gfortran sqlite sqlite-dev
RUN pip install -U pip

WORKDIR /src/
RUN cd /src/ && git clone -b dev-kube https://github.com/quanted/hms_flask.git

RUN conda config --add channels conda-forge
RUN conda create -n $CONDA_ENV_BASE python=3.9.10 gdal=$GDAL_VERSION
RUN conda install -n $CONDA_ENV_BASE --file /src/hms_flask/requirements.txt
RUN conda install -n $CONDA_ENV_BASE uwsgi
RUN conda install --force-reinstall -n $CONDA_ENV_BASE fiona
RUN conda install --force-reinstall -n $CONDA_ENV_BASE geopandas

RUN conda run -n $CONDA_ENV_BASE --no-capture-output conda clean -acfy && \
    find /opt/conda -follow -type f -name '*.a' -delete && \
    find /opt/conda -follow -type f -name '*.pyc' -delete && \
    find /opt/conda -follow -type f -name '*.js.map' -delete

FROM continuumio/miniconda3:4.10.3p0-alpine as prime

ENV APP_USER=www-data
ENV CONDA_ENV=/home/www-data/pyenv
ENV CONDA_ENV_BASE=/opt/conda/envs/pyenv

RUN adduser -S $APP_USER -G $APP_USER

RUN apk update
RUN apk upgrade
RUN apk add --no-cache geos gdal cmake git gfortran sqlite sqlite-dev

COPY --from=base /src /src
RUN chmod 755 /src/hms_flask/start_flask.sh
WORKDIR /src/
EXPOSE 8080

COPY --from=base $CONDA_ENV_BASE $CONDA_ENV_BASE
ENV PYTHONPATH /src:/src/hms_flask/:$CONDA_ENV_BASE:$PYTHONPATH
ENV PATH /src:/src/hms_flask/:$CONDA_ENV_BASE:$PATH

RUN chown -R $APP_USER:$APP_USER /src
RUN chown $APP_USER:$APP_USER $CONDA_ENV_BASE
USER $APP_USER

CMD ["conda", "run", "-p", "$CONDA_ENV_BASE", "--no-capture-output", "dask-worker", "hms-dask-scheduler:8786"]
