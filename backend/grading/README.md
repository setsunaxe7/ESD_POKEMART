**to do**
processing logic for grading, external and so on
dockerfile and containerise

**how to start**
cd rabbitmq
docker-compose up -d
docker-compose ls
<!-- check whether up ^^ -->
python amqp_setup.py
cd ..

*microservice*
python grader.py
python delivery.py
python external_grader.py
python notify.py

*for testing*
python tester.py

**how to shut down**
cd rabbitmq
docker-compose down -v

**grader.py**
1. first consume from rabbitmq, binding key 
*.create d
*.update d

2. then do processing wtv

3. then publish to rabbitmq, routing key
*.grader d
*.notify d
*.delivery


**external_grader.py**
1. first consume from rabbit mq, binding key
*.grader d

2. processing wtv

3. then publish to rabbitmq, routing key
*.update d

**tester.py**
just a python file with flask to take in post request wtv

header json

then rabbitmq, routing key 
*.create d

just to simulate like websocket cus frontend not up yet.