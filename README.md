# Credentials

   <p>`admin/admin` - Administrator<br>
   `user/user` - Regular user<br>
   `user2/user2` - Regular user</p>

# API

[Swagger API documentation](https://app.swaggerhub.com/apis/fancydancing/WebAuction/1.0.0)

# Project structure

### Frontend sources (Angular)
   <p>`angular_src` - sources for frontend<br>
   `angular_dist` - compiled and webpacked frontend files</p>

### Backend sources (Django)
   <p>`web_auction` - Django project settings<br>
   `auction` - Django application</p>

### Docker files
   <p>`Dockerfile` - setups Django service<br>
   `docker-compose.yml` - runs Django and PostgreSQL<br>
   `entrypoint.sh` - runs Django migrations before Django starts</p>


# Local machine deployment
1. Install [Docker](www.docker.com).

2. Before cloning git repository, set git config option `core.autocrlf=false`.

3. Move to project folder:
```bash
$ cd <your_git_clone_folder_path>/web_auction
```

4. Check ip address for web service:
```bash
$ docker-machine ip default
```

5. Build and run Docker container:
```bash
$ docker-compose build
$ docker-compose up
```

6. Open ip address (from step 4) in browser with port 8000. For example, in Windows: `192.168.99.100:8000`
