docker run -d -it -p 27017:27017 -v $PWD:/data/db --name=mongo mongo:3.2.7 mongod --dbpath /data/db --logpath /data/db/mongo.log
