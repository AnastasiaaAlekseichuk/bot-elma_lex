from dotenv import dotenv_values

env = dotenv_values()

TOKEN: str = env['TOKEN']
ELMA_URL: str = env['ELMA_URL']
ELMA_URL_ZADACHI: str = env['ELMA_URL_ZADACHI']
ELMA_URL_APP: str = env['ELMA_URL_APP']
ELMA_TOKEN: str = env['ELMA_TOKEN']
chat_id: str = env['chat_id']

# Configure if app start at production or test mode
# if env['PRODUCTION_MODE'] == 'True':
#     TOKEN = env['PRODTOKEN']
# else:
#     TOKEN = env['DEVTOKEN']

