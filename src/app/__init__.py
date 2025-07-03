import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get('/hello')
def read_root():
    return {'Hello': 'World'}

def main():
    uvicorn.run(app=app, host='localhost', port=8000)

if __name__ == '__main__':
    main()
