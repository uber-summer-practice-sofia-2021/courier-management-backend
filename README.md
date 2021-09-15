# courier-management-backend 

 Setting up virtual environemnt (For Windows)
 
 In the root directory of the repo run the following commands:
 
 py -3 -m venv venv
 
 venv\Scripts\activate

# Start up Kafka with Docker:

- Use ```docker-compose up -d``` to start services in the docker-compose.yml file
- To consume messages from kafka type ```docker exec -it courier-server python consumer.py``` in a separate terminal to start up the consumer who will start printing the incoming messages