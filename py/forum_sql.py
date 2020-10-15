import MySQLdb as mysql
import sys

class database():
    def __init__(self, config):
        self.db = mysql.connect(config[0], config[1], config[2], config[3], charset=config[4])
        self.cursor = self.db.cursor()

    
    def execute(self, sql):
        print("准备执行sql代码:", sql)
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            self.db.commit()
            print("执行sql完成:", result)
            return result
        except:
            self.db.rollback()
            print("执行错误: {}".format(sys.exc_info()))
            return False


    def execute_m(self, sqls:list):
        print("准备执行sqls代码:", sqls)
        result = []
        for sql in sqls:
            try:
                self.cursor.execute(sql)
                temp = self.cursor.fetchall()
                result.append(temp)
            except:
                self.db.rollback()
                print("执行错误: {}".format(sys.exc_info()))
                return False
        self.db.commit()
        print("执行sql完成:", result)
        return result


    def __del__(self):
        self.cursor.close()
        self.db.close()
        print("SQL进程结束")


