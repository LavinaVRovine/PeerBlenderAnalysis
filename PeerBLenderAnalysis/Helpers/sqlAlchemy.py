from sqlalchemy import create_engine
import pandas as pd

def get_smth(sql):
    engine =create_engine("mysql+mysqlconnector://root:Darthpic0@localhost/diplomkatest", echo=True, execution_options={'sqlite_raw_colnames':False})
    #days_of_week_logged = pd.read_sql_table("user",engine)
    nevim = pd.read_sql_query(sql, engine)
    return  nevim




'''
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


from sqlalchemy import Column, Integer, String
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
                        self.name, self.fullname, self.password)'''