FROM continuumio/miniconda3
ARG path=/app
ARG PROJECT='project'
ARG STORAGE='/storage/'
WORKDIR $path/$PROJECT
RUN mkdir -m 777 $STORAGE
COPY req.yml ./
RUN conda env create -f req.yml
RUN echo "source activate $PROJECT" > ~/.bashrc
ENV PATH /opt/conda/envs/$PROJECT/bin:$PATH
COPY . .