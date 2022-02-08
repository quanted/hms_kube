FROM continuumio/miniconda3:4.10.3

RUN apt-get update --allow-releaseinfo-change -y
RUN apt-get upgrade --fix-missing -y
RUN apt-get install --no-install-recommends git build-essential python3-dev libpq-dev -y --fix-missing && \
    pip install -U pip

WORKDIR /src/

RUN cd /src/ && git clone -b dev-kube https://github.com/quanted/hms_flask.git

RUN conda create --name pyenv python=3.9
RUN conda config --add channels conda-forge
RUN conda run -n pyenv --no-capture-output conda install --file /src/hms_flask/requirements.txt
RUN conda run -n pyenv --no-capture-output python --version

ENV PATH "/src:/src/hms_flask:${PATH}"
ENV PYTHONPATH "/src:/src/hms_flask:${PYTHONPATH}"

CMD ["conda", "run", "-n", "pyenv", "--no-capture-output", "dask-worker", "hms-dask-scheduler:8786"]