import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

# абстрактная база, основа для будущих моделей
SqlAlchemyBase = dec.declarative_base()

# сессия подключения к базе
__factory = None


# инициализация подключения
# db_file - путь до базы данны
def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    # строка подключения (тип базы данных, путь до базы данных и параметры подключения)
    # (для того, чтобы в последующем Sqlalchemy выбрала правильный движок работы с БД)
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    # создаём движок для работы с БД
    engine = sa.create_engine(conn_str, echo=False)

    #  создаем фабрику подключений к нашей базе данных
    __factory = orm.sessionmaker(bind=engine)

    # импортируем модели
    from . import __all_models

    # объявляем БД
    SqlAlchemyBase.metadata.create_all(engine)


# получение сессии подключения к нашей базе данных
def create_session() -> Session:
    global __factory
    return __factory()
