sudo docker image rm telegrambot
sudo docker build . --tag telegrambot
sudo docker run --rm -t --net=host -i telegrambot python /home/telegrambot/main.py