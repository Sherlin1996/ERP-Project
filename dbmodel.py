import pymysql
from flask_apispec import use_kwargs,marshal_with,doc,MethodResource
from datetime import datetime
from flask import jsonify,request
from schemadef import *
from statecode import *
import re
import random
import jieba.posseg as pseg
localtime=datetime.now().strftime("%Y-%m-%d %H:%M")
def connectsql():
    db = pymysql.connect(host="ec2-34-208-156-155.us-west-2.compute.amazonaws.com",port=3306,user='erp',passwd='erp')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return db,cursor


class Login(MethodResource):
    ##帳號登入
    @doc(description="帳號登入", tags=['Login'])
    @use_kwargs(LoginRequest, location="json")      
    def post(self, **kwargs):
        login_request = LoginRequest()
        try:
            db, cursor = connectsql()
            Class,Name,Password = kwargs.get('Class'),kwargs.get("Name"),kwargs.get("Password")
            sql = f'''SELECT * FROM personal_data.{Class}; '''
            cursor.execute(sql)
            getuser = cursor.fetchall()
            db.commit()
            db.close()
            for user in getuser:
                # print(user["Name"])
                # print(user["Password"])
                # print("===================")
                if  user["Name"] == Name and user["Password"]== Password:
                    user_data = login_request.load(user)
                    match = 1
                    # print(user_data)
                    # print("===============")
                    break
                else:
                    match = 0
            if match == 1:
                session = {"Access":user_data["Access"],"Class":user_data["Class"],"Name":user_data["Name"]}
                return jsonify(success(session))
            else:
                return jsonify(failure("帳號或密碼不符合您的資料"))
        except Exception as e:
            return {"error":str(e)}
    # 自動帶入 基本資料
    @doc(description="自動帶入基本資料", tags=['Login'])
    @use_kwargs(auto, location="query")
    def get(self,**kwargs):
        db,cursor = connectsql()
        Identity = {"Class":kwargs.get("Class"),"Name":kwargs.get("Name")}
        sql = f'''SELECT Class,Email,Id,Name FROM `personal_data`.{Identity["Class"]} WHERE `Name` = '{Identity["Name"]}'; '''
        cursor.execute(sql)
        data = cursor.fetchall()
        data = data[0]
        print(data)
        db.close()
        return jsonify(success(data))
##編輯完日誌登打後新增專案
class Diary_Log(MethodResource):
    ##編輯完日誌登打後新增專案
    @doc(description="編輯完日誌登打後新增專案", tags=['Diary_Log'])    
    def get(self,Class,Name):
        try:
            db,cursor = connectsql()
            # User = {"Class":kwargs["Class"],"Name":kwargs["Name"],"Time":kwargs["Time"]}
            getprojectname = '''SELECT `Class`,`Name`,`Project` FROM `diary_log`.`{}` WHERE `Name`='{}' && date(Time)=curdate();'''\
            .format(Class,Name)
            # cursor.execute(getprojectname,(User['Class'],User["Name"],User["Time"]))
            cursor.execute(getprojectname)
            project = cursor.fetchall()
            myproject = {}
            for num,pro in enumerate(project):
                projects = {}
                projects["Class"] = pro["Class"]
                projects["Name"] = pro["Name"]
                projects["Project"] = pro["Project"]
                myproject[num] = projects
            # print(project)
            db.commit()
            db.close()
            if myproject!={}:
                return jsonify(success(myproject))
            else:
                return jsonify(failure("get nothing"))
        except Exception as e:     
            return {"error":str(e)}
    ##登打時數、專案名稱、圖片網址、日誌內文
    ##sql要使用SET GLOBAL time_zone = '+8:00';
    @doc(description="日誌燈打", tags=['Diary_Log'])
    @marshal_with(diary_log_field,code=200)
    @use_kwargs(diary_log_field, location="json")
    def post(self,Class,Name,**kwargs):
        try:
            db,cursor = connectsql()
            inserdiarylog = {
            'Workinghours': kwargs.get('Workinghours'),
            'Project': kwargs.get('Project'),
            'Imgurl': kwargs.get('Imgurl'),
            'Content': kwargs.get('Content')
            }
            checkifnotexist = '''SELECT COUNT(Project) as ProjectCount FROM `diary_log`.`{}` WHERE Name="{}" AND Date(Time)=Curdate();'''\
            .format(Class,Name)
            print(checkifnotexist)
            cursor.execute(checkifnotexist)
            ProjectCount = cursor.fetchall()
            Check = ProjectCount[0]["ProjectCount"]
            print(Check)
            if Check == 0:
                insertcontent = '''INSERT INTO `diary_log`.`{}` (`Class`,`Name`,`Workinghours`,`Project`,`Imgurl`,`Content`,`Time`)\
                VALUES ('{}','{}','{}','{}','{}','{}',now());'''\
                .format(Class,Class,Name,inserdiarylog["Workinghours"],inserdiarylog["Project"],inserdiarylog["Imgurl"],inserdiarylog["Content"])
                result = cursor.execute(insertcontent)
                cursor.fetchall()
                db.commit()
                db.close()
                if result==1:
                    return jsonify(success({"status":'posted'}))
                else:
                    return jsonify(failure('nothing posted'))
            else:
                return jsonify(failure("You've been created today"))
        except Exception as e:
            return {"error":str(e)}
    ##使用者送出前修改日誌
    @doc(description="使用者送出前修改日誌", tags=['Diary_Log'])
    @marshal_with(diary_log_field)
    @use_kwargs(diary_log_field, location="json")
    def patch(self,Class,Name,**kwargs):
        print(kwargs)
        try:
            db,cursor = connectsql()
            changediarylog = {
            'Workinghours': kwargs.get('Workinghours'),
            'Project': kwargs.get('Project'),
            'Imgurl': kwargs.get('Imgurl'),
            'Content': kwargs.get('Content')
            }
            
            changecontent = '''UPDATE `diary_log`.`{}` SET\
            `Workinghours`='{}', `Imgurl`='{}', `Content`='{}', `Time`=now()\
            WHERE `Project`="{}" && `Name`="{}" && Date(Time)=curdate();'''\
            .format(Class,changediarylog["Workinghours"],changediarylog["Imgurl"],changediarylog["Content"],changediarylog["Project"],Name)

            result = cursor.execute(changecontent)
            cursor.fetchall()
            db.commit()
            db.close()
            # print(result)
            # print("=====")
            if result==1:
                return jsonify(success({"status":'Update'}))
            else:
                return jsonify(failure({"status":'nothing Update'}))
        except Exception as e:
            return {"error":str(e)}
    ##使用者送出前刪除日誌
    @doc(description="使用者送出前刪除日誌", tags=['Diary_Log'])
    @use_kwargs(diary_log_delete, location="json")
    def delete(self,Class,Name,**kwargs):
        try:
            db,cursor = connectsql()
            deletediarylog = {"Project":kwargs["Project"]}
            deletecontent = '''DELETE FROM `diary_log`.`{}`\
            WHERE `Project`= '{}' && `Name`= '{}' && date(Time) LIKE curdate();'''\
            .format(Class,deletediarylog["Project"],Name,)
            result = cursor.execute(deletecontent)
            cursor.fetchall()
            db.commit()
            db.close()
            if result==1:
                return jsonify(success({"status":'deleted'}))
            else:
                return jsonify(failure({"status":'nothing deleted'}))
        except Exception as e:
            return {"error":str(e)}
class Message(MethodResource):
    ##查看問題回覆
    @doc(description="查看問題回覆", tags=['Message'])
    @marshal_with(message_field)
    def get(self,Class,Name):
        try:
            db,cursor = connectsql()
            ##管理端
            if Class=='manager':
                ##未回覆
                getmessage_unreplid = '''SELECT `LeavingTime`,`Class`,`Name`,`Title`,`Content` FROM `message_systemreact`.`message` WHERE `ReplyContent` IS NULL;'''
                cursor.execute(getmessage_unreplid)
                unreplied = cursor.fetchall()
                ##已回覆
                getmessage_replid = '''SELECT `LeavingTime`,`Class`,`Name`,`Title`,`Content` FROM `message_systemreact`.`message` WHERE `ReplyContent` IS NOT NULL;'''
                cursor.execute(getmessage_replid)
                replied = cursor.fetchall()
                db.close()
                result = {"unreplied":unreplied,"replied":replied}
                return jsonify(success(result))
            ##學生、企業
            else:
                getmessage = '''SELECT * FROM `message_systemreact`.`message`\
                WHERE `Class`='{}'&&`Name`='{}' ORDER BY LeavingTime;'''\
                .format(Class,Name)
                cursor.execute(getmessage)
                message = cursor.fetchall()
                result = {}
                for index,mes in enumerate(message):
                    messages = {}
                    messages["LeavingTime"] = mes["LeavingTime"]
                    messages["Title"] = mes["Title"]
                    messages["Content"] = mes["Content"]
                    messages["ReplyContent"] = mes["ReplyContent"]
                    messages["ReplyingTime"] = mes["ReplyingTime"]
                    result[index] = messages
                db.commit()
                db.close()
                return jsonify(success(result))
        except Exception as e:
            return {"error":str(e)}

    @doc(description="留言系統問題", tags=['Message'])        
    @use_kwargs(message_field, location="json")
    ##留言系統問題
    def post(self,Class,Name,**kwargs):
        leavingmessage = {
        'Title': kwargs.get('Title'),
        'Content': kwargs.get('Content'),
        'ReplyContent': kwargs.get('ReplyContent'),
        "Access":kwargs.get("Access"),
        "Class":kwargs.get("studentclass"),
        "Name":kwargs.get("studentname")
        }
        ##student
        if leavingmessage['Access'] == '1' or leavingmessage['Access'] == '3':
            insertmessage ='''INSERT INTO `message_systemreact`.`message`\
            (`Class`, `Name`, `Title`,`Content`, `LeavingTime`)\
            VALUES ('{}','{}','{}','{}', now() );'''\
            .format(Class,Name,leavingmessage["Title"],leavingmessage["Content"])
        if leavingmessage['Access'] == '2':
            insertmessage = '''UPDATE `message_systemreact`.`message`\
            SET `ReplyContent`="{}", `ReplyingTime`=now()\
            WHERE `Class`="{}" and `Name`="{}" and `Title`="{}" and `Content`="{}"'''\
            .format(leavingmessage["ReplyContent"],leavingmessage["Class"],leavingmessage["Name"],leavingmessage["Title"],leavingmessage["Content"])
        try:
            db,cursor = connectsql()
            result = cursor.execute(insertmessage)
            # print(result)
            db.commit()
            db.close()
            if result==1:
                return jsonify(success({"status":"posted"}))
            else:
                return jsonify(failure({"status":"nothing posted"}))
        except Exception as e:
            return {"error":str(e)}


# 日誌登打狀態
class Status(MethodResource):
    @doc(description="日誌登打狀態", tags=['typing Status']) 
    def get(self,Class,Name):
        try:
            db,cursor = connectsql()
            sql = "SELECT `Name` FROM `diary_log`.`{}` WHERE Name='{}' and Date(Time) = curdate();"\
            .format(Class,Name)
            state = cursor.execute(sql)
            cursor.fetchall()
            db.commit()
            # print(state)
            db.close()
            if state == 0:
                return jsonify(success({"message":"今日尚未登打"}))
            else:
                return jsonify(success({"message":"今日已登打"}))
        except Exception as e:
            return {"error":str(e)}

##管理端查看日誌登打率
class typing_rate(MethodResource):
    @doc(description="管理端查看日誌登打率", tags=['typing Status'])
    @marshal_with(typing_rate)
    @use_kwargs(typing_rate,location="json")
    def post(self,**kwargs):
        try:
            db, cursor = connectsql()
            Class = kwargs.get("Class")
            Time = kwargs.get("Time")
            ##當日登打日誌人數
            amount = '''SELECT COUNT(Name) AS student_number FROM `personal_data`.`{}`'''.format(Class)
            cursor.execute(amount)
            student = cursor.fetchall()
            student_number = student[0]["student_number"]
            ##每日登打率
            if Time=="day":
                sql = '''SELECT COUNT(DISTINCT Name) AS Count_day FROM `diary_log`.`{}` WHERE date(Time)=CURRENT_DATE;'''\
                .format(Class)
                cursor.execute(sql)
                typing_count = cursor.fetchall()
                count_day = typing_count[0]["Count_day"]
                type_rate = str(round((count_day/student_number)*100,1))+'%'
            ##每月登打率
            elif Time=="month":
                sql = '''SELECT COUNT(DISTINCT Name) AS Count_month,date(Time) from `diary_log`.`{}`\
                WHERE DATE_FORMAT(date(time), '%m') = DATE_FORMAT(CURRENT_DATE, '%m') GROUP BY date(Time);'''\
                .format(Class)
                cursor.execute(sql)
                typing_count = cursor.fetchall()
                db.commit()
                db.close()
                type_rate_acc = 0
                for count in typing_count:
                    count_month = count["Count_month"]
                    type_rate_perday = count_month/student_number
                    type_rate_acc = type_rate_acc + type_rate_perday
                type_rate = str(round((type_rate_acc / len(typing_count)*100),1))+'%'
                # print(type_rate)
            return jsonify(success({"type_rate":type_rate}))
        except Exception as e:
            return {"error":str(e)}
    # DATE_FORMAT(date(time), '%m') = DATE_FORMAT(CURRENT_DATE, '%m');
    # SELECT COUNT(DISTINCT Name),date(Time) from dv102 GROUP BY date(Time);

#  管理端帳號管理
class Account_management(MethodResource):
    @doc(description="管理端查看學生詳細資料", tags=['Account_management'])
    @use_kwargs(details,location="query")
    ##依據Class,Name查看學生詳細資料
    def get(self,**kwargs):
        try:
            db,cursor = connectsql()
            Name,type,number= kwargs.get("Name"),kwargs.get("type"),kwargs.get("number")
            Class = type+number
            ##個人資料
            if Name != None:
                sql = f'''SELECT * FROM `personal_data`.`{Class}` WHERE `Name`="{Name}"'''
            ##全班資料
            else:
                sql = f'''SELECT * FROM `personal_data`.{Class}'''
            cursor.execute(sql)
            alldata = cursor.fetchall()
            db.commit()
            db.close()
            return jsonify(success(alldata))
        except Exception as e:
            return {"error":str(e)}
    ##批次上傳班級學員基本資料
    @doc(description="批次上傳班級學員基本資料", tags=['Account_management'])
    @use_kwargs(upload_personaldata,location="form")
    def post(self,**kwargs):
        try:
            db,cursor = connectsql()
            file = request.files.get('file')
            ##檢查是不是csv檔
            filename = file.filename.split(".")[0]
            filetype = file.filename.split(".")[1]
            if filetype!="csv":
                print("This is not csv,please upload csv file")
            else:
                ##讀取第一列(欄位)
                columns = file.readline().decode("utf-8").strip()
                columnname = columns.split(',')
                #檢查是不是6個欄位並且檢查欄位名稱是不是有效
                if len(columnname) == 6:
                    if 'Id' and 'Access' and 'Class' and 'Name' and 'Password' and 'Email' in columnname:
                        rows = file.read().decode("utf-8").strip()
                        row = rows.split('\n')
                        print(row)
                        # Class = columnname
                        create_class = '''CREATE TABLE IF NOT EXISTS`personal_data`.{}(\
                        Id int(40) PRIMARY KEY NOT NULL AUTO_INCREMENT,\
                        Access varchar(5) NOT NULL,\
                        Class varchar(10) NOT NULL,\
                        Name varchar(20) NOT NULL,\
                        Password varchar(20) NOT NULL,\
                        Email varchar(20) NOT NULL)'''\
                        .format(filename)
                        cursor.execute(create_class)
                        db.commit()
                        for value in row:
                            value.strip()
                            data = value.split(',')
                            Id = data[0]
                            Access = data[1]
                            Class = data[2]
                            Name = data[3]
                            Password = data[4]
                            Email = data[5]
                            insert_data = '''INSERT INTO `personal_data`.`{}`\
                            (`Id`,`Access`,`Class`,`Name`,`Password`,`Email`)\
                            VALUES ({},'{}','{}','{}','{}','{}');'''\
                            .format(filename,Id,Access,Class,Name,Password,Email)
                            print(insert_data)
                            result = cursor.execute(insert_data)
                        db.commit()
                        db.close()
                        if result==1:
                            return jsonify(success({"status":"Uploaded"}))
                    else:
                        return failure("wrong column")
                else:
                    return failure("losing or unexpected column")
        except Exception as e:
            return {"error":str(e)}

    # Id 無法做修改
    ##學員詳細資料修改
    @doc(description="學員詳細資料修改(ID無法更改)", tags=['Account_management'])
    @use_kwargs(Account,location="json")
    def patch(self,**kwargs):
        try:
            db,cursor = connectsql()
            Id,type,number,Name,Email,Password =\
            kwargs.get("Id"),kwargs.get("type"),kwargs.get("number"),kwargs.get("Name"),kwargs.get("Email"),kwargs.get("Password")
            Class = type+number
            sql = f'''UPDATE `personal_data`.`{Class}`\
            SET `Class` = '{Class}',`Name` = '{Name}',`Email` = '{Email}',`Password` = '{Password}' WHERE `Id`={Id};'''
            result = cursor.execute(sql)
            db.commit()
            db.close()
            if result == 1:
                return jsonify(success({"status":'Update'}))
            else:
                return jsonify(failure({"status":'nothing Update'}))##資料沒改變就patch相當於沒有update
        except Exception as e:
            return {"error":str(e)}
    ##學員詳細資料刪除
    @doc(description="學員詳細資料刪除", tags=['Account_management'])
    @use_kwargs(AccountDelete,location="json")
    def delete(self,**kwargs):
        try:
            db,cursor =connectsql()
            Name,type,number = kwargs.get("Name"),kwargs.get("type"),kwargs.get("number")
            Class = type+number
            sql = f'''INSERT INTO `personal_data`.`Lost`(Id,Access,Class,Name,Password,Email) SELECT * FROM `personal_data`.`{Class}` WHERE `Name` = '{Name}';'''
            sql2 = f'''DELETE FROM `personal_data`.`{Class}` WHERE `Name` = '{Name}';'''
            # print(sql)
            # print("============")
            # print(sql2)
            result = cursor.execute(sql)
            # cont = cursor.fetchall()
            result2 = cursor.execute(sql2)
            # cont2 = cursor.fetchall()
            db.commit()
            db.close()
            if result == 1 and result2 == 1:
                return jsonify(success({"status":'Delete'}))
            else:
                return jsonify({"status":'nothing Delete'})
        except Exception as e:
            return {"error":str(e)}
##############
## 帳號權限管理 新增單個學員/企業/管理者
class Addsingleaccount(MethodResource):
    @doc(description="新增單個學員/企業/管理者(限已存在班級,企業必須傳送 ent，值固定為'ent'，學員必須傳送 type、number)", tags=['Account_management'])
    @use_kwargs(single_Account,location="json")
    def post(self,**kwargs):
        try:
            db,cursor = connectsql()
            type,number,ent,Name,Email,Password = kwargs.get("type"),kwargs.get("number"),kwargs.get("ent"),kwargs.get("Name"),kwargs.get("Email"),kwargs.get("Password")
            if type != None and number != None:
                Class = type + number
            else:
                pass
            if ent == 'ent':
                Access = "3"
                sql = f'''
                INSERT INTO `personal_data`.`{ent}`(`Class`,`Access`,`Name`,`Email`,`Password`) VALUES('{ent}','{Access}','{Name}','{Email}','{Password}');
                '''
            elif ent == None:
                Access = "1"
                sql = f'''
                INSERT INTO `personal_data`.`{Class}`(`Class`,`Access`,`Name`,`Email`,`Password`) VALUES('{Class}','{Access}','{Name}','{Email}','{Password}');
                '''
            else:
                return {"error":"unexpected argument"}
            result = cursor.execute(sql)
            db.commit()
            db.close()
            if result == 1:
                return jsonify(success({"status":"posted"}))
            return jsonify(failure({"status":"nothing posted"}))
        except Exception as e:
            return {"error":str(e)}
##############
class Get_datalist(MethodResource):
    # 列出班別、班級及專案list
    @doc(description="列出班別、班級及專案list", tags=['Get datalist'])
    def get(self):
        try:
            db, cursor = connectsql()
            sql_allClass = '''SHOW TABLES FROM diary_log;'''
            sql_allproject = '''SELECT * FROM `Project`.`project`;'''
            cursor.execute(sql_allClass)
            allClass = cursor.fetchall()
            cursor.execute(sql_allproject)
            allproject = cursor.fetchall()
            db.commit()
            db.close()
            Class_list=[]
            type_list = []
            number_list = []
            project_list = []
            #take all class
            for class_ in allClass:
                Class_list.append(list(class_.values())[0])
            #change all class into type and number
            for class_ in Class_list:
                type = re.findall(r'[a-z|A-Z]+',class_)[0]
                number = re.findall(r'\d+',class_)[0]
                number_list.append(number)
                type_list.append(type)
            for project in allproject:
                Projects = {}
                Projects["Project"] = project["Project"]
                Projects["Status"] = project["Project_status"]
                project_list.append(Projects)
            
            result = {"type":type_list,"number":number_list,"Project":project_list}
            # print(type_list)
            # print(number_list)
            # print(Class_list)
            # print(project_list)
            return jsonify(success(result))
        except Exception as e:
            return {"error":str(e)}

# 管理端查看日誌
class Manager_read_diary(MethodResource):
    @doc(description="管理端查看日誌", tags=["Diary_Log"])
    @marshal_with(ManagerReadList)
    @use_kwargs(ManagerReadList, location="json")
    def post(self, **kwargs):
        try:
            db, cursor = connectsql()
            type = kwargs.get("type")
            number=kwargs.get("number")
            project=kwargs.get("project")
            date_from=kwargs.get("date_from")
            date_to=kwargs.get("date_to")
            Name=kwargs.get("Name")
            Class=type+number
            ##Time, Name, Project, Content
            sql_diary_list='''SELECT * FROM `diary_log`.`{}`\
            WHERE Project='{}' AND date(Time) BETWEEN '{}' AND '{}';'''\
            .format(Class, project, date_from, date_to)
            cursor.execute(sql_diary_list)
            diary_list=cursor.fetchall()
            datail = {}
            ##查看個人日誌
            if Name!=None:
                for detail in diary_list:
                    name_detail = detail["Name"]
                    if name_detail == Name:
                        datail["name_detail"] = name_detail
                        datail["project_detail"] = detail["Project"]
                        datail["time_detail"] = detail["Time"]
                        break
                name_detail,project_detail,time_detail = datail["name_detail"],datail["project_detail"],datail["time_detail"]
                # print(name_detail)
                # print(project_detail)
                # print(time_detail)
                sql_log_detail='''SELECT * FROM `diary_log`.`{}`\
                WHERE Name='{}' AND Time ='{}' AND Project='{}';'''\
                .format(Class, name_detail, time_detail, project_detail)         
                cursor.execute(sql_log_detail)
                datails = cursor.fetchall()
                # print(datails)
                db.commit()
                db.close()
                return jsonify(success(datails))
            ##查看所有人日誌
            else:
                db.close()
                return jsonify(success(diary_list))
        except Exception as e:
            return {"error":str(e)}

## 推薦職缺
class RecommandCareer(MethodResource):
    @doc(description="推薦職缺", tags=['reccomand Career'])
    def get(self,Class,Name):
        db,cursor = connectsql()
## 取工作日誌登打內容
        sql = f'''SELECT Content FROM `diary_log`.`{Class}` WHERE Name = '{Name}';'''
        print(sql)
        cursor.execute(sql)
        content = cursor.fetchall()
        db.commit
        # print(content)

        allContent = []

        for con in content:
            allContent.append(con["Content"])
        allContentjoin = "".join(allContent).upper()
        # print(allContentjoin)

## 結巴切關鍵字
        words = pseg.cut(allContentjoin)
        con_skill = []
        for word, flag in words:
            if flag == 'eng':
                con_skill.append(word)
        random.shuffle(con_skill)
        skill_list = list(set(con_skill))
        result_list = []
        for skill in skill_list:
            # print(i)
            sql2 = f'''
            select `Url`,`Job`,UPPER(`Skill`) AS Skill,`Region`,`Resource` from `Career`.`data`\
            WHERE Skill LIKE "%{skill}%" UNION ALL\
            select `Url`,`Job`,UPPER(`Skill`) AS Skill,`Region`,`Resource` from `Career`.`cloud`\
            WHERE Skill LIKE "%{skill}%" UNION ALL\
            select `Url`,`Job`,UPPER(`Skill`) AS Skill,`Region`,`Resource` from `Career`.`frontend`\
            WHERE Skill LIKE "%{skill}%" ORDER BY RAND() limit 2 ;
            ''' 
            check = cursor.execute(sql2)
            content = cursor.fetchall()
            for job in content:
                # print(job) dic
                result_list.append(job)
        return(result_list)