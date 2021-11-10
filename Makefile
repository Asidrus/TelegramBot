build:
	docker build . --tag telegrambot
remove:
	docker rmi -f telegrambot
run:
	docker run \
		-d \
		--rm \
		--net=host \
		--name='telegrambot' \
		telegrambot \
		bash -c \
		"python main.py"
stop:
	docker stop telegrambot