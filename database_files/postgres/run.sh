docker run -d -it -p 5432:5432 -v $PWD/pgdata:/data/pgdata -e POSTGRES_USER=mcga -e POSTGRES_PASSWORD=Welcome1 -e PGDATA=/data/pgdata --name=postgres postgres
