run:
	docker run --gpus all --env-file .env -it testlangchain
build:
	docker build -t testlangchain .