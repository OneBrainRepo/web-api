# web-api
Web API that responsible for Front end communication. Handles Users and chat parsing/history

Used Libraries : 

- https://sqlmodel.tiangolo.com/ | SQL Model , A wrapper for SQL Alchemy designed for FastAPI
- https://fastapi.tiangolo.com/ | FastAPI , Python module for Web API
- https://docs.pydantic.dev/latest/usage/types/#standard-library-types | Python Types

Notes :

Currently we are also using Document DB for conversation history.
Later on use similar schema for MongoDB or other NoSQL dbs

For generating JWT token key use this command

In the pipeline to add to the .env
`openssl rand -hex 32`


FIREBASE WOULD BE NEGLECTED, IT IS NOT SUITABLE FOR OUR USAGE PURPOSES[DONE]

We might need to add more user service such as create and update[DONE]
Also create demo_user under user services for demo only purpose[DONE]
Create_demo_user as a  service but no endpoint[DONE]

Routes under one folder, services in their seperate folder, guards under seperate folder(such as auth)[DONE]
Also create mongodb folder for mongo connection and remove firebase completely[DONE]
Slowly Start integrating chat history and other related stuff to the functions[DONE]

Final Steps 
- Check for all os.environ variables and update the .env.example file with required parameters
- Add deployment configurations
- Create Docker file for deployment
- Create docker-compose for both databases(PostgreSQL,MongoDB) and current container

## Things to do
- Edit message[Semi Done]
- Change title[Done]

# Ideal Scenario

Active conversation would be kept inside vector db
History would be kept inside the Document DB
This way current active conversation can be retrived quickly and faster

MONGODB ENDPOINTS HAS SOME ERROR, CHECK IT
ALSO DTOS HAS PROBLEMS AS WELL