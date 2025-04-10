This Project was created with poetry using python 3.11

To install the project use:
- poetry install

structure:
- the projcect contains two branches "webcrawler_v1" and "webcrawler_v2" 
- the directory "deutscher_blog_webcrawler" contains a "main.py" which can be used as the programm starting point in both branches
- the directory "data" contains all collected data, on github are smaller samples of collected data to point out how the data would look like

DOCKER PIPELINE
1. docker build -t schniffelus/blog_crawler-image .
2. docker push schniffelus/blog_crawler-image
3. docker pull schniffelus/blog_crawler-image
4. docker run --volume ./output:/app/data -d schniffelus/blog_crawler-image
5. docker ps
6. docker logs <ID>
7. docker stop <ID>

Or using docker compose file:
1. docker compose pull
2. docker compose up -d
3. docker compose down
