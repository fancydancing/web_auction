# Live demo
http://webauction.herokuapp.com/

### Credentials
   admin/admin - Administrator  
   user/user - Regular user  
   user2/user2 - Regular user  

# Project structure

### Frontend sources (Angular)
   angular_src - sources for frontend  
   angular_dist - compiled and webpacked frontend files  

### Backend sources (Django)
   web_auction - Django project settings  
   auction - Django application  

### Docker files
   Dockerfile - setups Django service  
   docker-compose.yml - runs Django and PostgreSQL  
   entrypoint.sh - runs Django migrations before Django starts  


# Local machine deployment
1. Install [Docker](www.docker.com).

2. Move to project folder:
```bash
$ cd <your_git_clone_folder_path>/web_auction
```

2. Check ip address for web service:
```bash
$ docker-machine ip default
```

3. Build and run Docker container:
```bash
$ docker-compose build
$ docker-compose up
```

4. Open ip address in browser with port 8000. For example, in Windows: 192.168.99.100:8000.

