## Run and Test the app

```sh
streamlit run app.py
```

## Requirements (refer requirements.txt)

- streamlit
- transformers < 5.0
- fastapi
- uvicorn
- torch
- sse-starlette


## API Version

Refer `main.py`

### Run FastAPI server

```sh
uvicorn main:app
```


### Run Frontend

```sh
streamlit run frontend_streamlit.py
```