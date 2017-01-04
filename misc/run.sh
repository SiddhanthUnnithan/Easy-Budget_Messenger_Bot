# convenience script to run docker container with application

docker run -d -it -p 80:5000 -v $PWD:/App --name=mcga-flask mcga-flask python app.py
