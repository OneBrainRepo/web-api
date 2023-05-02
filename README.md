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


FIREBASE WOULD BE NEGLECTED, IT IS NOT SUITABLE FOR OUR USAGE PURPOSES

We might need to add more user service such as create and update
Also create demo_user under user services for demo only purpose

Routes under one folder, services in their seperate folder, guards under seperate folder(such as auth)
Also create mongodb folder for mongo connection and remove firebase completely
