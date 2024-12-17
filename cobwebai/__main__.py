import uvicorn

from cobwebai.settings import settings


def main() -> None:
    """Entrypoint of the application."""
    uvicorn.run(
        "cobwebai.app:get_app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.value.lower(),
        factory=True,
        forwarded_allow_ips="*",
        proxy_headers=True,
        # ssl_keyfile=settings.ssl_keyfile,
        # ssl_certfile=settings.ssl_certfile,
    )


if __name__ == "__main__":
    main()
