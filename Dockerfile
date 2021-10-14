FROM continuumio/miniconda3
RUN conda info
RUN conda create -n telegrambot python=3.8
RUN conda init bash
#RUN conda activate telegrambot
RUN pip3 install aiogram asyncio asyncpg matplotlib
RUN mkdir /home/telegrambot
RUN mkdir /temp
RUN chmod 777 /temp
COPY *.py /home/telegrambot/
