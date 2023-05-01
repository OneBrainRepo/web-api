from webapi import main
import uvicorn

if __name__ == "__main__":
    uvicorn.run("webapi.main:app",port=8080,log_level="info")