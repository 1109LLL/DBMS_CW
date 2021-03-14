Containerize This: PHP/Apache/MySQL
===================================
### Manual
After pulling, cd into directory with `docker-compose.yml` file
1) docker-compose build
2) docker-compose up
3) Access website via `localhost:8000`
4) docker-compose down


### Intro
The main focus of this project is to build a system that makes use of the MovieLens data provided by Grouplens, enabling marketing professionals to analyse how
audiences have responded to films that have been released, and to help them understand the market for films that they are planning. This system consist of both a frontend and backend component, allowing easy access for the users. Furthermore, the entire application is containerised using docker to ensure that it is portable, flexible, lightweight and can be run on machines with different operating systems that has access to Docker.


```
/DBCW/
├── django
│   ├── Dockerfile
│   └── movieapp
│       └── templates/movieapp
│           └── index.html
├── mysql
│   └── Dockerfile
├── redis
└── docker-compose.yml
    
```