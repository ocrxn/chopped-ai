import psycopg2
import os
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from config import DATABASE_URL
import bcrypt
import logging

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

class Connection:
    def __init__(self):
        self.username = None
        self.password = None

    def connect_db(self):
        if not DATABASE_URL:
            logging.error("[connect_db] DATABASE_URL is not set. Failed to connect to database.")
            return
        return psycopg2.connect(DATABASE_URL)

    def update_status(self,query,username):
        try:
            conn = self.connect_db()
            exe = conn.cursor()

            exe.execute(query,(username,))
            conn.commit()
        except psycopg2.Error as error:
            logging.error(f"[update_status] Error has occurred: {error}")
            return
        except Exception as e:
            logging.error(f"[update_status] Exception has occurred: {e}")
            return
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
            logging.error(f"[create_user] Error has occurred: {error}")
            return False
        except Exception as e:
            logging.error(f"[create_user] Exception has occurred: {e}")
            return False
        finally:
            exe.close()
            conn.close()
        return True
    

    def confirm_user(self, username, password):
        conn = None
        exe = None
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
            logging.error(f"[confirm_user] An error has occurred: {error}")
            return
        except Exception as e:
            logging.error(f"[confirm_user] Exception has occurred: {e}")
            return
        finally:
            if exe: exe.close()
            if conn: conn.close()
    
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
            logging.error(f"[delete_user] An error has occurred: {error}")
        except Exception as e:
            logging.error(f"[delete_user] Exception has occurred: {e}")
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
            logging.error(f"[query_db] An error has occurred: {error}")
        except Exception as e:
            logging.error(f"[query_db] Exception has occurred: {e}")
        finally:
            logging.info("[query_db] Query successfully completed")
            exe.close()
            conn.close()



c = Connection()
if __name__ == "__main__":
    c.query_db(query = """
TRUNCATE TABLE public.users RESTART IDENTITY CASCADE;
""")