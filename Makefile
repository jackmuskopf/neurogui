PORT=5000

build:
	docker build -t neurogui .

run:
	docker run -it --env-file .env -e PORT=${PORT} --rm -p 5000:${PORT} neurogui