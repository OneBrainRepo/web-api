from webapi import main
import uvicorn
import os

PORT = os.getenv("PORT", 8080)

if __name__ == "__main__":
    uvicorn.run("webapi.main:app",port=PORT,log_level="info")