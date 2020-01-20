from environs import Env

env = Env()
env.read_env()

ENV = env("FLASK_ENV", default="production")
DEBUG = ENV == "development"

AUTH0_DOMAIN = env("AUTH0_DOMAIN")
ALGORITHMS = env.list("ALGORITHMS")
API_AUDIENCE = env("API_AUDIENCE")
