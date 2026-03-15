.PHONY: dev build down clean logs

# Start the app for local development
dev:
	docker compose up

# Rebuild the containers (run this if you install new packages)
build:
	docker compose up --build

# Stop everything
down:
	docker compose down

# Stop everything and wipe the volumes/databases (Factory Reset)
clean:
	docker compose down -v
	rm -rf backend/data/*

# View the logs of both frontend and backend
logs:
	docker compose logs -f