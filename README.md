# courier-management-backend 

 Setting up virtual environemnt (For Windows)
 
 In the root directory of the repo run the following commands:
 
 py -3 -m venv venv
 
 venv\Scripts\activate

# Start up local Kafka broker:

While in the kafka folder write the following lines in the terminal in the given order:
- '''bin/zookeeper-server-start.sh config/zookeeper.properties'''
- '''bin/kafka-server-start.sh config/server.properties'''