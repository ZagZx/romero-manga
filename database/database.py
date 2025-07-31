import sqlite3
from typing import Union, Any


# from werkzeug.security import check_password_hash, generate_password_hash
# from .query import insert, select

class Database:
    def __init__(self, db_path:str) -> None:
        '''
        Classe que faz a conexão com o banco de dados e executa os SQL

        Parâmetros:
            - db_path: Caminho e nome do arquivo onde o banco ficará armazenado
        '''
        self.db_path = db_path
        self._connection = None

    @property
    def connection(self) -> sqlite3.Connection:
        if not self._connection or not self.is_open():
            try: 
                self._connection = sqlite3.connect(self.db_path)
            except Exception as e:
                print(f'Erro ao obter conexão: {e}')
        return self._connection
    
    def is_open(self) -> bool: 
        '''Checa se a conexão está aberta'''
        try: # roda um comando e se ele funcionar, a conexão está aberta
            self._connection.execute('SELECT 1')
            return True
        except: # se der erro, está fechada
            return False


    # AJUSTAR RUN QUERY PRA SER UTILIZADO DENTRO DA CLASSE EM FUNÇÕES COMO add_user
    def run_query(self, sql_query:str, params:Union[tuple,list, Any] = None) -> list: # fazer doc depois
        result = None
        try:
            if params:
                if isinstance(params, (tuple, list)):
                    cursor = self.connection.execute(sql_query, params)
                else:
                    cursor = self.connection.execute(sql_query, (params,))

            else:
                cursor = self.connection.execute(sql_query)

            self.connection.commit()
            result = cursor.fetchall()
            self.connection.close()
        except Exception as e: # tirar quando entrar em produção
            print(f'Erro ao rodar query: {e}\nQuery: {sql_query}')
        
        return result

    def run_sql_file(self, sql_path:str): # fazer doc
        try:
            with open(sql_path) as fr:
                self.connection.executescript(fr.read())
                self.connection.close()
        except Exception as e:
            print(f'Erro ao rodar arquivo SQL: {e}')


if __name__ == '__main__':
    db = Database('./database/database.db')

    db.run_query("DELETE FROM sqlite_sequence WHERE name='users'") # tira os ids no autoincrement, só pra deixar bonito no sqlite viewer
    db.run_query("DELETE FROM users")
    # db.add_user('ZagZ', 'azevedodvictor@gmail.com', 'senhaBEMdificil')

    print(db.run_query('SELECT * FROM users'))

    # print(db.run_query(select('users', 'id')))