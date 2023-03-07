from pathlib import Path
from typing import Optional

import typer
import uvicorn


def run(
    url: str = typer.Argument("127.0.0.1", help="Host URL", envvar="QDAM_SERVER_URL"),
    port: int = typer.Argument(80, help="Host port", envvar="QDAM_SERVER_PORT"),
    reload: bool = typer.Option(True, help="Whether to reload on file changes"),
    ssl_certfile: Optional[Path] = typer.Option(
        None, help="SSL certificate location", envvar="QDAM_TLS_CERT_PATH", exists=True
    ),
    ssl_keyfile: Optional[Path] = typer.Option(
        None, help="SSL keyfile location", envvar="QDAM_TLS_KEY_PATH", exists=True
    ),
    ssl_keyfile_password: Optional[Path] = typer.Option(
        None, help="SSL keyfile password", envvar="QDAM_TLS_PASSPHRASE", exists=True
    ),
):
    path = Path(__file__).resolve().parent
    uvicorn.run(
        "qdamono_server.app:app",
        host=url,
        port=port,
        reload=reload,
        reload_dirs=[path],
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        ssl_keyfile_password=ssl_keyfile_password,
    )


def cli():
    typer.run(run)


if __name__ == "__main__":
    cli()
