import MySQLdb as mysql
import sys

class database():
    def __init__(self, config):
        self.db = mysql.connect(config[0], config[1], config[2], config[3], charset=config[4])
        self.cursor = self.db.cursor()


    def select(self, sql, m):
        print("准备执行查询sql指令: {}".format(sql))
        try:
            self.cursor.execute(sql)
            # m为0 -> 获取单条信息
            if m == 0:
                result = self.cursor.fetchone()
            # m为1 -> 获取多条信息
            if m == 1:
                result = self.cursor.fetchall()
            print(result)
            return result

        except:
            print("执行错误: {}".format(sys.exc_info()))


    def insert(self, sql):
        print("准备执行插入sql指令: {}".format(sql))
        try:
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except:
            print("执行错误: {}".format(sys.exc_info()))
            self.db.rollback()
            return False


    def update(self, sql):
        print("准备执行更新sql指令:{}".format(sql))
        try:
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except:
            print("执行错误: {}".format(sys.exc_info()))
            self.db.rollback()
            return False   


    def delete(self, sql):
        print("准备执行删除sql指令:{}".format(sql))
        try:
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except:
            print("执行错误: {}".format(sys.exc_info()))
            self.db.rollback()
            return False


    def __del__(self):
        self.cursor.close()
        self.db.close()
        print("进程结束")

