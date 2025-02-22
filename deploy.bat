@echo off
docker-compose build
docker tag emoji_sorter-emoji-sorter us-docker.pkg.dev/bright-arc-451620-t3/docker-repo/emoji_sorter:latest
docker push us-docker.pkg.dev/bright-arc-451620-t3/docker-repo/emoji_sorter:latest
gcloud run deploy discord-emoji-sorter --image us-docker.pkg.dev/bright-arc-451620-t3/docker-repo/emoji_sorter:latest --platform managed --region us-central1 --allow-unauthenticated