"""
### database
对指定数据库进行配置与数据读写
"""
import re
import pymysql

class database():
    def __init__(self, host='localhost', user='root', passwd='000000', dbname='music_wav', port='3306'):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.port = port
        self.db = database.config_db(self)

    def config_db(self):
        try:
            db = pymysql.connect(host=self.host,
                                user=self.user,
                                passwd=self.passwd,
                                db=self.dbname,
                                port=int(self.port),
                                charset="utf8")
            return db
        except Exception as config_ex:
            print('config_ex: ', config_ex)

    def create_table(self, newtable):
        try:
            mycursor = self.db.cursor()
            sql = "show tables"
            mycursor.execute(sql)
            tables = [mycursor.fetchall()]
            tables_list = re.findall('(\'.*?\')', str(tables))
            # print(tables_list)
            tables_list = [re.sub("'", '', each)for each in tables_list]
            print(tables_list)
            if newtable in tables_list:
                print("table exists")
            else:
                print("table not exists")
                mycursor.execute("SHOW DATABASES")
                sql = """CREATE TABLE {} (
                         id INT (3) AUTO_INCREMENT PRIMARY KEY, 
                         name VARCHAR(255),
                         sites VARCHAR(255))""".format(newtable)
                mycursor.execute(sql)
            return self.db
        except Exception as creat_ex:
            print('creat_ex', creat_ex)

    def insert_data(self, name, site, table):
        try:
            mycursor = self.db.cursor()
            sql = "INSERT INTO {} (name, sites) VALUES (%s, %s)".format(table)
            val = (name, site)
            mycursor.execute(sql, val)
            self.db.commit()  # 数据表内容有更新
            print(mycursor.rowcount, "Success")
        except pymysql.Error as e:
            print("Fail to insert data: " + str(e))

    def read_data(self, field, table):
        mycursor = self.db.cursor()
        mycursor.execute("SELECT {} FROM {}".format(field, table))
        data = mycursor.fetchall()
        list = []
        for x in data:
            x = x[0]
            list.append(x)
        return list


