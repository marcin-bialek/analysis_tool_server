# QDAMono server

A server for QDAMono enabling its collaboration features.

## Prerequisities

- Python ^3.11
- [Poetry](https://python-poetry.org/) - dependency management
- MongoDB database

## Preparation

Prepare environment and install dependencies.
```shell
> poetry install
```

Create `.env` file with necessary environment variables (generate QDAM_AUTH_KEY yourself and protect it):
```
QDAM_AUTH_KEY = yAyARFNxXSnUt5BkrhDSRvt9sdF2NQQP
QDAM_DB_URL = mongodb://localhost:27017
```

Run the server in the environment.
```shell
> poetry run server
```

Optionally enter the environment and run the server directly.
```shell
> poetry shell
> python ./qdamono_server/runner.py
```

## License

[QDAMono is licensed under MIT license](LICENSE)
