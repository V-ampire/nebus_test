import uvicorn

from bootstrap.config.app import AppConfig


def main():
    app_config = AppConfig()

    server_config = dict(
        port=4000,
        host='0.0.0.0',
        lifespan='on'
    )
    if app_config.debug:
        server_config['reload'] = True
        server_config['log_level'] = 'info'

    uvicorn.run('app_instance:app', **server_config)


if __name__ == "__main__":
    main()
