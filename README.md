DOCKER PIPELINE
1. docker build -t schniffelus/blog_crawler-image .
2. docker push schniffelus/blog_crawler-image
3. docker pull schniffelus/blog_crawler-image
4. docker run --volume ./output:/app/data -d schniffelus/blog_crawler-image
5. docker ps
6. docker logs <ID>
7. docker stop <ID>

Alternativ mit docker compose file:
1. docker compose pull
2. docker compose up -d
3. docker compose down