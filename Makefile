build:
	docker build . --tag autotest
remove:
	docker rmi -f telegrambot
run:
	docker run \
		-d \
		--rm \
		-p 1234:1234 \
		--name='telegrambot' \
		telegrambot \
		bash -c \
		"python main.py"
stop:
	docker stop telegrambot