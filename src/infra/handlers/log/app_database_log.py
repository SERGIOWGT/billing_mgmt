from datetime import datetime
import logging
import mysql.connector
from .db_config import db_config

# Configuração do logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# Crie um manipulador personalizado para salvar logs no banco de dados
class ApplicationDatabaseLogHandler():
    def __init__(self, log_name):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s:%(levelname)s:%(message)s",
            datefmt="%Y-%m-%d %I:%M:%S%p",
        )
        self.log = logging.getLogger(log_name)
        self.db_config = db_config
        
    def _emit(self, levelname, msg):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO logs_robot_qd (level, message) VALUES (%s, %s)",
                           (levelname, msg))
            conn.commit()
        except Exception as e:
            print(f"Erro ao inserir registro no banco de dados: {str(e)}")


    def save_message(self, msg: str, execution: bool = False, error: bool = False):
        if error:
            self.log.error(msg)
            self._emit('error', msg)
        elif execution:
            self.log.info(msg)
            self._emit('execution', msg)
        else:
            self.log.info(msg)
            self._emit('info', msg)
            
    def save_message_qd30(self, tipo_alerta, num_processados, num_erros, num_sem_alojamentos, link_qd28, link_exports):
        str_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        apiURL = 'https://hook.us1.make.com/gq4047iq6xvncq1mm630dy24ivbr21c7'

        jsonData = {
            "DATA_ALERTA": str_now,
            "TIPO_ALERTA": tipo_alerta,
            "QT_FICHEIROS_PROCESSADOS": num_processados,
            "QT_FICHEIROS_ERRO": num_erros,
            "QT_ficheiros sem alojamento": num_sem_alojamentos,
            "LINK_QD28": link_qd28,
            "LINK_EXEC": link_exports
        }

        try:
            _ = requests.post(apiURL, json=jsonData, timeout=10000)
        except Exception:
            ...