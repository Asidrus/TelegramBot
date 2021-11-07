FROM continuumio/miniconda3
WORKDIR /home/tester/telegrambot
EXPOSE $PORT
RUN mkdir -m 777 /temp
COPY req.yml ./
RUN conda env create -f req.yml
RUN echo "source activate telegrambot" > ~/.bashrc
ENV PATH /opt/conda/envs/telegrambot/bin:$PATH
COPY . .

#RUN pip3 install aiogram asyncio asyncpg matplotlib

