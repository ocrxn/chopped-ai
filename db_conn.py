import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from config import *
import bcrypt

load_dotenv()

class Connection:
    def __init__(self):
        self.username = None
        self.password = None

    def connect_db(self):
        return psycopg2.connect(DB_URL)

    def update_status(self,query,username):
        try:
            conn = self.connect_db()
            exe = conn.cursor()

            exe.execute(query,(username,))
            conn.commit()
        except psycopg2.Error as error:
            print(f"update_status error has occurred: {error}")
        except Exception as e:
            print(f"update_status exception has occurred: {e}")
        finally:
            exe.close()
            conn.close()
        
    def create_user(self, username, email, password):
        try:
            conn = self.connect_db()
            exe = conn.cursor()

            hashed_pass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            exe.execute("INSERT INTO users (username,email,password) VALUES (%s,%s,%s)", (username, email,hashed_pass))
            conn.commit()
        except psycopg2.Error as error:
            print(f"An error has occurred. {error}")
            return False
        except Exception as e:
            print(f"Create User Exception has occurred: {e}")
            return False
        finally:
            exe.close()
            conn.close()
        return True
    

    def confirm_user(self, username, password):
        try:
            conn = self.connect_db()
            exe = conn.cursor()
            exe.execute("SELECT password FROM users WHERE username=%s", (username,))
            result = exe.fetchone()

            #Return False if user not found
            if result is None:
                return False
            
            hashed_pass = bytes(result[0])
            if bcrypt.checkpw(password.encode('utf-8'), hashed_pass):
                return True
            return False        
        except psycopg2.Error as error:
            print("An error has occurred: {error}")
        except Exception as e:
            print(f"Confirm User Exception has occurred: {e}")
        finally:
            exe.close()
            conn.close()
    
    def delete_user(self, username):
        try:
            conn = self.connect_db()
            exe = conn.cursor()
            exe.execute("DELETE FROM users WHERE username=%s", (username,))
            conn.commit()
            if exe.rowcount > 0:
                return True
            return False

        except psycopg2.Error as error:
            print("An error has occurred: {error}")
        except Exception as e:
            print(f"Confirm User Exception has occurred: {e}")
        finally:
            exe.close()
            conn.close()
    
    def query_db(self, query):
        try:
            conn = self.connect_db()
            exe = conn.cursor()

            
            exe.execute(query)
            conn.commit()
        except psycopg2.Error as error:
            print(f"An:1 error has occurred: {error}")
        except Exception as e:
            print(f"Exception has occurred: {e}")
        finally:
            print("Query successfully completed.")
            exe.close()
            conn.close()



c = Connection()
if __name__ == "__main__":
    c.query_db(query = """
TRUNCATE TABLE public.users RESTART IDENTITY CASCADE;
""")