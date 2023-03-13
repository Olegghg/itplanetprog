from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from collections import OrderedDict
import re
from datetime import datetime
import datetime
from collections import Counter
import base64

app = Flask(__name__)

# Required
app.config["MYSQL_HOST"] = "db"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "toor"
app.config["MYSQL_DB"] = "Project"
# Extra configs, optional:
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)
def EmailCheck(email):
    regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    if re.fullmatch(regex, email):
        return "True"
    else: return "False"

def SpaceCheck(param1="0",param2="0",param3="0"):
    regex = re.compile(r'^[^\s]*[\S]')
    if (re.fullmatch(regex, param1) and re.fullmatch(regex, param2) and re.fullmatch(regex, param3)):
        return "True"
    else: return "False"

def Checkauth(req,point=0):
    if (req[:6].lower() != "basic "): return "False"
    req = req[6::]
    req = str(base64.b64decode(req))[2:-1]
    loginpass = req.split(":")
    login,password = loginpass[0],loginpass[1]
    if point==1: return [login,password]
    if (EmailCheck(login) == "True"):
        if (SpaceCheck(password) == "True"):
            try:
                cur = mysql.connection.cursor()
                cur.execute("SELECT id FROM Account where email ='"+str(login)+"' and password = '"+str(password)+"';")
                rv = cur.fetchall()[0]
                return "True"
            except:
                return "False"
    else: return "False"

def Auth(stat):
    auth = request.headers.get("Authorization")
    if stat == 0:
        if auth is not None:
            if Checkauth(auth) == "False": return "False"
        else: return "True"
    elif stat ==1:
        if auth is None:
            return "False"
        else:    
            if Checkauth(auth) == "False":
                return "False"
            else: return "True"

def Accountown(id,log,pas):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT email,password FROM Account where id = '"+str(id)+"';")
        otv=cur.fetchall()[0]
        loginbd = otv.get("email")
        passwordbd = otv.get("password")
        if ((loginbd==log) and (passwordbd==pas)):
            return "True"
        else: return "False"
    except:
        return "False"

def Animalprint(animal):
    dictionary = {"id":animal}
    cur = mysql.connection.cursor()
    animalTypes = []
    cur.execute("select animal_type_id from Animal_Types_Array where animal_id = '"+str(animal)+"'")
    rv = cur.fetchall()
    for element in rv:
        animalTypes.append(element.get("animal_type_id"))
    dictionary["animalTypes"]=animalTypes
    #################
    visitedLocations = []
    cur.execute("select locationPointId from Animal_Visited_Location where animalId = '"+str(animal)+"'")
    rv = cur.fetchall()
    for element in rv:
        visitedLocations.append(element.get("locationPointId"))
    dictionary["visitedLocations"]=visitedLocations
    ################### 
    cur.execute("select * from Animal where id = '"+str(animal)+"'")
    a =cur.fetchall()[0]
    dictionary.update(a)
    dictionary.pop("chippingDateTime")
    dictionary.pop("deathDateTime")
    cur.execute("select chippingDateTime from Animal where id = '"+str(animal)+"'")
    chippingDateTime = cur.fetchall()[0].get("chippingDateTime").isoformat()
    dictionary["chippingDateTime"]=str(chippingDateTime)+"Z"
    cur.execute("select deathDateTime from Animal where id = '"+str(animal)+"'")
    death = cur.fetchall()[0].get("deathDateTime") 
    if death is not None:
        deathDateTime =death.isoformat()
        dictionary["deathDateTime"]=str(deathDateTime)+"Z"
    else: dictionary["deathDateTime"]=None
    return dictionary
#####################################
########### Регистрация #############

@app.route('/registration', methods=['POST'])
def registration():
    if request.method == "POST":
        ##### Проверка на уже авторизованного пользователя #######
        if (request.headers.get("Authorization") is not None): return "Status 403",403
        ######### Перменные для проверки и передачи БД #######
        firstName = str(request.json.get("firstName")).replace("'","''")
        lastName = request.json.get("lastName")
        email = request.json.get("email")
        password = request.json.get("password")
        ########## Проверка на null значения ##########
        if (firstName == "None" or lastName == None or 
        email == None or password == None): return "Status 400", 400
        ########## Проверка на валидность почты #######
        if EmailCheck(email) != "True": return "Status 400", 400
        ######## Проверка на пробелы ###############
        if (SpaceCheck(firstName,lastName,password) == "False"):
            return "Status 400", 400
        ######## Проверка на уникальность аккаунта ###
        cur = mysql.connection.cursor()
        cur.execute("SELECT email FROM Account where email = '"+str(email)+"';")
        try:
            if ( cur.fetchall()[0].get("email") is not None): return "Status 409", 409
        except:
        ####### Добавления аккаунта в БД ####
            cur.execute("INSERT INTO Account (firstName,lastName,email,password) VALUES (%s, %s,%s, %s);", (firstName,lastName,email,password))
            mysql.connection.commit()
            cur.execute("SELECT * FROM Account where firstName = %s and lastName = %s and email = %s and password = %s;", (firstName,lastName,email,password))
            rv = cur.fetchall()[0]
            rv.pop("password")
            return jsonify(rv),201

######################################
######## Аккануты пользователей ######

####### Запрос без AccountId #######
@app.route("/accounts/", methods=['GET'])
def accountnull():
    return "Status 400", 400
@app.route("/accounts/-<int:accountId>", methods=['GET'])
def accountminus(accountId):
    return "Status 400", 400
@app.route("/accounts/<int:accountId>", methods=['GET'])
def accountget(accountId):
    ####### Проверка авторизационных данных (При наличии)## 
    if (Auth(0)=="False"): return "Status 401", 401
    ####### Accountid больше 0 #########
    if accountId <= 0: return "Status 400", 400
    ####### Запрос данных из БД #######
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM Account where id ="+str(accountId)+";")
        rv = cur.fetchall()[0]
        rv.pop("password")
        ###### Успех #######
        return rv,200
    ############ Данные не найдены #######
    except: return "Status 404", 404

@app.route("/accounts/search", methods=['GET'])
def accountgetparam():
    ####### Проверка авторизационных данных (При наличии)## 
    if (Auth(0)=="False"): return "Status 401",401
    ######### Аргуметы для поиска в БД #######
    firstName = request.args.get('firstName')
    lastName = request.args.get('lastName')
    email = request.args.get('email')
    froma = request.args.get('from',default=0,type=int)
    sizea = request.args.get('size',default=10,type=int)
    ########## Значения from и size соответствуют условию ###
    if (froma < 0 or sizea <= 0): return "Status 400", 400

    ####### Запрос данных из БД #######
    cur = mysql.connection.cursor()
    try:
        query = "SELECT * FROM Account where id > 0 "
        if firstName is not None: 
            query = query + " and firstName LIKE '%"+str(firstName)+"%' "
        if lastName is not None: 
            query = query + " and lastName LIKE '%"+str(lastName)+"%' "
        if email is not None: 
            query = query + " and email LIKE '%"+str(email)+"%' "
        query = query + " limit "+str(sizea)+" offset "+str(froma)+";"
        cur.execute(query)
        rv = cur.fetchall()
        a=[]
        for i in rv:
            i.pop("password")
            a.append(i)
        ###### Успех #######
        return jsonify(a),200
    ############ Данные не найдены #######
    except: return "Такого пользователя нет", 200
####### Запрос без AccountId #######
@app.route("/accounts/", methods=['PUT'])
def accountputnull():
    return "Status 400", 400
@app.route("/accounts/-<int:accountid>", methods=['PUT'])
def accountputminus(accountid):
    return "Status 400", 400
@app.route('/accounts/<int:accountid>', methods=['PUT'])
def accountupdate(accountid):
    if accountid<=0: return "Status 400", 400
    ######### Перменные для проверки и передачи БД #######
    newfirstName = str(request.json.get("firstName")).replace("'","''")
    lastName = request.json.get("lastName")
    email = request.json.get("email")
    newpassword = request.json.get("password")
    ########## Проверка на null значения ##########
    if (newfirstName == "None" or lastName == None or 
    email == None or newpassword == None): return "Status 400", 400
    if EmailCheck(email) != "True": return "Status 400", 400
    if (SpaceCheck(newfirstName,lastName,newpassword) == "False"):
        return "Status 400", 400
    ####### Авторизационные данные #####
    auth = request.headers.get("Authorization")
    ####### Проверка авторизационных данных## 
    if auth is None:
        return  "Status 401", 401
    else:    
        if Checkauth(auth) == "False":
            return "Status 401", 401
    ######### Проверка на соответствие accountid ####
    login,password = Checkauth(auth,1)
    if (Accountown(accountid,login,password)=="False"):
        return "Status 403", 403
    ######## Проверка на уникальность аккаунта ###
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM Account where id != "+str(accountid)+" and email = '"+str(email)+"';")
    try:
        if ( cur.fetchall()[0].get("email") is not None): return "Status 409", 409
    except:
    ####### Добавления аккаунта в БД ####
        cur.execute("UPDATE Account SET firstName = %s, lastName = %s, email = %s, password = %s where id = %s;", (newfirstName,lastName,email,newpassword,accountid))
        mysql.connection.commit()
        cur.execute("SELECT * FROM Account where id = '"+str(accountid)+"';")
        rv = cur.fetchall()[0]
        rv.pop("password")
        return jsonify(rv),200
####### Запрос без AccountId #######
@app.route("/accounts/", methods=['DELETE'])
def accountdelnull():
    return "Status 400", 400
@app.route("/accounts/-<int:accountid>", methods=['DELETE'])
def accountdelminus(accountid):
    return "Status 400", 400
@app.route('/accounts/<int:accountid>', methods=['DELETE'])
def accountdelete(accountid):
    ####### Авторизационные данные #####
    auth = request.headers.get("Authorization")
    ####### Проверка авторизационных данных## 
    if auth is None:
        return  "Status 401", 401
    else:    
        if Checkauth(auth) == "False":
            return "Status 401", 401
    ###### accountid больше нуля ################# 
    if accountid <=0: return "Status 400", 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal where chipperId ="+str(accountid)+";")
        if ( cur.fetchall()[0] is not None): return "Status 400", 400
    except: pass
    ### Связь с животным ###
    ######### Проверка на соответствие accountid ####
    login,password = Checkauth(auth,1)
    if (Accountown(accountid,login,password)=="False"):
        return "Status 403", 403
    ######### Удаление элемента ###########
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Account where id ="+str(accountid)+";")
    mysql.connection.commit()
    return "Status 200", 200


##########################################################
################ Типы животных ###########################

@app.route("/animals/types/", methods=['GET'])
def typesgetnull():
    return "Status 400", 400
@app.route("/animals/types/-<int:typeId>", methods=['GET'])
def typesgetminus(typeId):
    return "Status 400", 400
@app.route("/animals/types/<int:typeId>", methods=['GET'])
def typesget(typeId):
    if typeId <= 0: return "Status 400", 400
    if (Auth(0)=="False"): return "Status 401", 401
    ####### Запрос данных из БД #######
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM Animal_Type where id ="+str(typeId)+";")
        rv = cur.fetchall()[0]
        ###### Успех #######
        return rv,200
    ############ Данные не найдены #######
    except: return "Status 404", 404

@app.route('/animals/types', methods=['POST'])
def typesinsert():
    if (Auth(1)=="False"): return "Status 401", 401
    type  = request.json.get("type")
    if type is None: return "Status 400",400
    if (SpaceCheck(type) == "False"): return "Status 400", 400
    ######## Проверка на уникальность типа ###
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM Animal_Type where type = '"+str(type)+"';")
    try:
        if ( cur.fetchall()[0].get("id") is not None): return "Status 409", 409
    except:
    ####### Добавления аккаунта в БД ####
        cur.execute("INSERT INTO Animal_Type (type) VALUES ('"+str(type)+"');")
        mysql.connection.commit()
        cur.execute("SELECT * FROM Animal_Type where type = '"+str(type)+"';")
        rv = cur.fetchall()[0]
        return jsonify(rv),201

@app.route("/animals/types/-<int:typeId>", methods=['PUT'])
def  typesputminus(typeId):
    return "Status 400", 400
@app.route("/animals/types", methods=['PUT'])
def  typesputnull():
    return "Status 400", 400
@app.route('/animals/types/<int:typeId>', methods=['PUT'])
def  typesupdate(typeId):
    if typeId <= 0: return "Status 400", 400
    type  = request.json.get("type")
    if type is None: return "Status 400", 400
    if (SpaceCheck(type) == "False"): return "Status 400", 400
    if (Auth(1)=="False"): return "Status 401", 401
    ######## Проверка на уникальность типа ###
    cur = mysql.connection.cursor()
    cur.execute("SELECT type FROM Animal_Type where type = '"+str(type)+"';")
    try:
        if ( cur.fetchall()[0].get("type") is not None): return "Status 409", 409
    except:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal_Type where id ="+str(typeId)+";")
        try: 
            if ( cur.fetchall()[0].get("id") is None): return "Status 404", 404
            cur.execute("UPDATE Animal_Type SET type = %s where id = %s;", (type,typeId))
            mysql.connection.commit()
            cur.execute("SELECT * FROM Animal_Type where id = '"+str(typeId)+"';")
            rv = cur.fetchall()[0]
            return jsonify(rv),200
        except: return "Status 404", 404

@app.route("/animals/types/-<int:typeId>", methods=['DELETE'])
def  typesdelminus(typeId):
    return "Status 400", 400
@app.route("/animals/types/", methods=['DELETE'])
def  typesdelnull():
    return "Status 400", 400
@app.route('/animals/types/<int:typeId>', methods=['DELETE'])
def  typesdelete(typeId):
    if typeId <= 0: return "Status 400", 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT animal_type_id FROM Animal_Types_Array where animal_type_id ="+str(typeId)+";")
        if ( cur.fetchall()[0] is not None): return "Status 400", 400
    except: pass
    if (Auth(1)=="False"): return "Status 401", 401
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Animal_Type where id ="+str(typeId)+";")
    rv = cur.fetchall()
    if (rv == ()): return "Status 404", 404
    ######### Удаление элемента ###########
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Animal_Type where id ="+str(typeId)+";")
    mysql.connection.commit()
    return "Status 200", 200

################################
######## Location Point ########

@app.route("/locations/", methods=['GET'])
def lpgetminus():
    return "Status 400", 400
@app.route("/locations/-<int:lpId>", methods=['GET'])
def lpgetnull(lpId):
    return "Status 400", 400
@app.route("/locations/<int:lpId>", methods=['GET'])
def lpget(lpId):
    if lpId <= 0: return "Status 400", 400
    if (Auth(0)=="False"): return "Status 401", 401
    ####### Запрос данных из БД #######
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM Location_Point where id ="+str(lpId)+";")
        rv = cur.fetchall()[0]
        ###### Успех #######
        return rv,200
    ############ Данные не найдены #######
    except: return "Status 404", 404

@app.route('/locations', methods=['POST'])
def lpinsert():
    if (Auth(1)=="False"): return "Status 401", 401
    try:
        latitude = float(request.json.get("latitude"))
        longitude = float(request.json.get("longitude"))
    except: return "Status 400", 400
    if ((latitude <= 90) and (latitude >= -90)) == False: return "Status 400", 400
    if ((longitude <= 180) and (longitude >= -180)) == False: return "Status 400", 400
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM Location_Point where latitude = %s and longitude = %s;",(latitude,longitude))
    try:
        if ( cur.fetchall()[0].get("id") is not None): return "Status 409", 409
    except:
    ####### Добавления аккаунта в БД ####
        cur.execute("INSERT INTO Location_Point (latitude,longitude) VALUES (%s,%s);",(latitude,longitude))
        mysql.connection.commit()
        cur.execute("SELECT * FROM Location_Point where latitude = %s and longitude = %s;",(latitude,longitude))
        rv = cur.fetchall()[0]
        return jsonify(rv),201

@app.route("/locations/-<int:lpId>", methods=['PUT'])
def lpputminus(lpId):
    return "Status 400", 400
@app.route("/locations/", methods=['PUT'])
def  lpputnull():
    return "Status 400", 400
@app.route('/locations/<int:lpId>', methods=['PUT'])
def  lpupdate(lpId):
    if lpId <=0: return "Status 400", 400
    if (Auth(1)=="False"): return "Status 401", 401
    try:
        latitude = float(request.json.get("latitude"))
        longitude = float(request.json.get("longitude"))
    except: return "Status 400", 400
    if ((latitude >= 90) or (latitude <= -90)):
        return "Status 400", 400
    if ((longitude >= 180) or (longitude <= -180)):
        return "Status 400", 400
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM Location_Point where latitude = %s and longitude = %s;",(latitude,longitude))
    try:
        if ( cur.fetchall()[0].get("id") is not None): return "Status 409", 409
    except:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Location_Point where id ="+str(lpId)+";")
        rv = cur.fetchall()
        if (rv == ()): return "Status 404", 404
        cur.execute("UPDATE Location_Point SET latitude = %s, longitude = %s where id = %s;", (str(latitude),str(longitude),lpId))
        mysql.connection.commit()
        cur.execute("SELECT * FROM Location_Point where id = '"+str(lpId)+"';")
        rv = cur.fetchall()[0]
        return jsonify(rv),200

@app.route("/locations/-<int:lpId>", methods=['DELETE'])
def lpdelminus(lpId):
    return "Status 400", 400
@app.route("/locations/", methods=['DELETE'])
def  lpdelnull():
    return "Status 400", 400
@app.route('/locations/<int:lpId>', methods=['DELETE'])
def  lpdelete(lpId):
    if lpId <=0: return "Status 400", 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT locationPointId FROM Animal_Visited_Location where locationPointId ="+str(lpId)+";")
        if ( cur.fetchall()[0] is not None): return "Status 400", 400
    except: pass
    if (Auth(1)=="False"): return "Status 401", 401
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Location_Point where id ="+str(lpId)+";")
    rv = cur.fetchall()
    if (rv == ()): return "Status 404", 404
    ######### Удаление элемента ###########
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Location_Point where id ="+str(lpId)+";")
    mysql.connection.commit()
    return "Status 200", 200

##########################################
############### Animal ###################

@app.route("/animals/-<int:animalId>", methods=['GET'])
def animalsgetminus(animalId):
    return "Status 400", 400
@app.route("/animals/", methods=['GET'])
def animalsgetnull():
    return "Status 400", 400
@app.route("/animals/search", methods=['GET'])
def animalssearch():
    ####### Проверка авторизационных данных (При наличии)## 
    if (Auth(0)=="False"): return "Status 401",401
    ######### Аргуметы для поиска в БД #######
    startDateTime = request.args.get('startDateTime')
    endDateTime = request.args.get('endDateTime')
    chipperId = request.args.get('chipperId',type=int)
    chippingLocationId = request.args.get('chippingLocationId',type=int)
    lifeStatus = request.args.get('lifeStatus',type=str)
    gender = request.args.get('gender',type=str)
    froma = request.args.get('from',default=0,type=int)
    sizea = request.args.get('size',default=10,type=int)
    ####################################################
    if froma < 0: return "Status 400", 400
    if sizea <= 0: return "Status 400", 400
    if chipperId is not None:
        if chipperId <= 0: return "Status 400", 400
    if chippingLocationId is not None: 
        if chippingLocationId <= 0: return "Status 400", 400
    if gender is not None:
        if (gender != "MALE" and gender != "FEMALE" and gender != "OTHER"): return "Status 400", 400
    if lifeStatus is not None:
        if (lifeStatus != "DEAD" and lifeStatus != "ALIVE"): return "Status 400", 400
    ########################### Поиск в БД ##################
    cur = mysql.connection.cursor()
    try:
        query = "SELECT id FROM Animal where id > 0"
        if startDateTime is not None: 
            query = query + " and chippingDateTime >= '"+str(startDateTime)+"' "
        if endDateTime is not None: 
            query = query + " and chippingDateTime <= '"+str(endDateTime)+"' "
        if lifeStatus is not None: 
            query = query + " and lifeStatus LIKE '%"+str(lifeStatus)+"%' "
        if gender is not None: 
            query = query + " and gender LIKE '"+str(gender)+"' "
        if chipperId is not None: 
            query = query + " and chipperId LIKE '%"+str(chipperId)+"%' "
        if chippingLocationId is not None: 
            query = query + " and chippingLocationId LIKE '%"+str(chippingLocationId)+"%' "
        query = query + " limit "+str(sizea)+" offset "+str(froma)+";"
        cur.execute(query)
        rv = cur.fetchall()
        a=[]
        for i in rv:
            a.append(Animalprint(i.get("id")))
        ###### Успех #######
        return jsonify(a),200
    ############ Данные не найдены #######
    except: return "Такого животного нет", 200
@app.route("/animals/<int:animalId>", methods=['GET'])
def animalsget(animalId):
    if (Auth(0)=="False"): return "Status 401",401
    if animalId <= 0: return "Status 400",400
    cur = mysql.connection.cursor()
    cur.execute("select id from Animal where id = '"+str(animalId)+"'")
    try:
        rv = cur.fetchall()[0]
        return jsonify(Animalprint(animalId)),200
    except: return "Status 404",404

@app.route('/animals', methods=['POST'])
def animalsinsert():
    if (Auth(1)=="False"): return "Status 401", 401
    animalTypes = request.json.get("animalTypes")
    weight = request.json.get("weight")
    length = request.json.get("length")
    height = request.json.get("height")
    gender = request.json.get("gender")
    chipperId = request.json.get("chipperId")
    chippingLocationId = request.json.get("chippingLocationId")
    lifeStatus = "ALIVE"
    chippingDateTime = datetime.datetime.now().replace(microsecond=0).isoformat()
    ####################### Проверка введенных данных ############
    if animalTypes == []: return "Status 400",400 
    for element in animalTypes:
        try:
            if int(element) <= 0: return "Status 400",400
        except: return "Status 400",400 
    if weight is None or length is None or height is None or chipperId is None or chippingLocationId is None:
        return "Status 400", 400
    if (weight ==0): return "Status 400", 400
    if (float(weight) <= 0): return "Status 400", 400
    if (length ==0): return "Status 400", 400
    if (float(length) <= 0): return "Status 400", 400
    if (height ==0): return "Status 400", 400
    if (float(height) <= 0): return "Status 400", 400
    if (gender != "MALE" and gender != "FEMALE" and gender != "OTHER"): return "Status 400", 400
    if (chipperId ==0): return "Status 400", 400
    if (int(chipperId) <= 0): return "Status 400", 400
    if (int(chippingLocationId) <= 0): return "Status 400", 400
    if ([k for k,v in Counter(animalTypes).items() if v>1] != []): return "Status 409",409
    try:
        cur = mysql.connection.cursor()
        for typei in animalTypes:
            cur.execute("SELECT id FROM Animal_Type where id = '"+str(typei)+"';")
            if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
        cur.execute("SELECT id FROM Account where id = '"+str(chipperId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 chipper", 404
        cur.execute("SELECT id FROM Location_Point where id = '"+str(chippingLocationId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 location", 404
    except: return "Status 404", 404
    ##################################### Ввод данных в sql таблицу ######################################
    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO Animal (weight,length,height,gender,chipperId,chippingLocationId,lifeStatus,chippingDateTime) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s);""",(weight,length,height,gender,chipperId,chippingLocationId,lifeStatus,chippingDateTime))
    mysql.connection.commit()
    cur.execute("SELECT id FROM Animal ORDER BY ID DESC limit 1")
    animal_id = cur.fetchall()[0].get("id")
    for typei in animalTypes:
        cur.execute("INSERT INTO Animal_Types_Array (animal_id, animal_type_id) VALUES (%s,%s);",(animal_id,typei))
        mysql.connection.commit()
    cur.execute("""INSERT INTO Animal_Visited_Location (animalId, locationPointId,dateTimeOfVisitLocationPoint) 
    VALUES (%s,%s,%s);""",(animal_id,chippingLocationId,chippingDateTime))
    mysql.connection.commit()
    ############################################### Вывод данных ###########################
    return jsonify(Animalprint(animal_id)),201

@app.route("/animals/-<int:animalId>", methods=['PUT'])
def animalsputminus(animalId):
    return "Status 400", 400
@app.route("/animals/", methods=['PUT'])
def  animalsputnull():
    return "Status 400", 400
@app.route('/animals/<int:animalId>', methods=['PUT'])
def  animalsupdate(animalId):
    if animalId <=0: return "Status 400", 400
    if (Auth(1)=="False"): return "Status 401", 401
    weight = request.json.get("weight")
    length = request.json.get("length")
    height = request.json.get("height")
    gender = request.json.get("gender")
    chipperId = request.json.get("chipperId")
    chippingLocationId = request.json.get("chippingLocationId")
    lifeStatus = request.json.get("lifeStatus")
    chippingDateTime = datetime.datetime.now().replace(microsecond=0).isoformat()
    deathDateTime = None
    if weight is None or length is None or height is None or chipperId is None or chippingLocationId is None:
        return "Status 400", 400
    ####################### Проверка введенных данных ############
    if (weight ==0): return "Status 400", 400
    if (float(weight) <= 0): return "Status 400", 400
    if (length ==0): return "Status 400", 400
    if (float(length) <= 0): return "Status 400", 400
    if (height ==0): return "Status 400", 400
    if (float(height) <= 0): return "Status 400", 400
    if (gender != "MALE" and gender != "FEMALE" and gender != "OTHER"): return "Status 400", 400
    if (lifeStatus != "ALIVE"  and lifeStatus != "DEAD"): return "Status 400", 400
    if (chipperId ==0): return "Status 400", 400
    if (int(chipperId) <= 0): return "Status 400", 400
    if (chippingLocationId ==0): return "Status 400", 400
    if (int(chippingLocationId) <= 0): return "Status 400", 400
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT id FROM Animal where id = '"+str(animalId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
    except: return "Status 404", 404
    cur.execute("select lifeStatus from Animal where id = '"+str(animalId)+"'")
    if (cur.fetchall()[0].get("lifeStatus") == "DEAD"):
        if lifeStatus == "ALIVE": return "Status 400", 400
    cur.execute("select locationPointId from Animal_Visited_Location where animalId = '"+str(animalId)+"' limit 1")
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal where id = '"+str(animalId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
        cur.execute("SELECT id FROM Account where id = '"+str(chipperId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 chipper", 404
        cur.execute("SELECT id FROM Location_Point where id = '"+str(chippingLocationId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 location", 404
    except: return "Status 404", 404
    ##################################### Ввод данных в sql таблицу ######################################
    if lifeStatus == "DEAD": deathDateTime = datetime.datetime.now().replace(microsecond=0).isoformat()
    cur = mysql.connection.cursor()
    cur.execute("""UPDATE Animal SET weight =%s,length=%s,height=%s,gender=%s,
    lifeStatus = %s,chipperId=%s,chippingLocationId=%s,chippingDateTime=%s,deathDateTime = %s where id = %s;""",
    (weight,length,height,gender,lifeStatus,chipperId,chippingLocationId,chippingDateTime, deathDateTime,animalId))
    mysql.connection.commit()
    cur.execute("""INSERT INTO Animal_Visited_Location (animalId, locationPointId,dateTimeOfVisitLocationPoint) 
    VALUES (%s,%s,%s);""",(animalId,chippingLocationId,chippingDateTime))
    mysql.connection.commit()
    ############################################### Вывод данных ###########################
    return jsonify(Animalprint(animalId)),200

@app.route("/animals/-<int:animalId>", methods=['DELETE'])
def animaldelminus(animalId):
    return "Status 400", 400
@app.route("/animals/", methods=['DELETE'])
def  animaldelnull():
    return "Status 400", 400
@app.route('/animals/<int:animalId>', methods=['DELETE'])
def  animaldelete(animalId):
    if (Auth(1)=="False"): return "Status 401", 401
    if animalId <=0: return "Status 400", 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal where id = '"+str(animalId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
    except: return "Status 404 type", 404 
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT chipperId FROM Animal where id = '"+str(animalId)+"';")
        if ( cur.fetchall()[0].get("id") is not None): return "Status 400 type", 400
    except: pass
    visitedLocations = []
    cur.execute("select locationPointId from Animal_Visited_Location where animalId = '"+str(animalId)+"'")
    rv = cur.fetchall()
    for element in rv:
        visitedLocations.append(element.get("locationPointId"))
    if len(visitedLocations) > 1: return "Status 400", 400
    cur.execute("DELETE FROM Animal_Types_Array where animal_id ="+str(animalId)+";")
    mysql.connection.commit()
    cur.execute("DELETE FROM Animal_Visited_Location where animalId ="+str(animalId)+";")
    mysql.connection.commit()
    cur.execute("DELETE FROM Animal where id ="+str(animalId)+";")
    mysql.connection.commit()
    return "Status 200", 200

@app.route('/animals/-<int:animalId>/types/<int:typesId>', methods=['POST'])
def animalsminustypesinsert(animalId,typesId):
    return "Status 400", 400
@app.route('/animals/<int:animalId>/types/-<int:typesId>', methods=['POST'])
def animalstypesminusinsert(animalId,typesId):
    return "Status 400", 400
@app.route('/animals/-<int:animalId>/types/-<int:typesId>', methods=['POST'])
def animalsminustypesminusinsert(animalId,typesId):
    return "Status 400", 400
@app.route('/animals/<int:animalId>/types/<int:typesId>', methods=['POST'])
def animalstypesinsert(animalId,typesId):
    if (Auth(1)=="False"): return "Status 401", 401
    if (animalId <=0) or (typesId <=0): return "Status 400", 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal where id = '"+str(animalId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
        cur.execute("SELECT id FROM Animal_Type where id = '"+str(typesId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
    except: return "Status 404 type", 404 
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal_Types_Array where animal_id = '"+str(animalId)+"' and animal_type_id = '"+str(typesId)+"';")
        if ( cur.fetchall()[0].get("id") is not None): return "Status 409 type", 409
    except: pass
    cur.execute("INSERT INTO Animal_Types_Array (animal_id, animal_type_id) VALUES (%s,%s);",(animalId,typesId))
    mysql.connection.commit()
    return jsonify(Animalprint(animalId)),201

@app.route("/animals/-<int:animalId>/types", methods=['PUT'])
def animalsputminustypes(animalId):
    return "Status 400", 400
@app.route('/animals/<int:animalId>/types', methods=['PUT'])
def  animalsupdatetypes(animalId):
    if animalId <=0: return "Status 400", 400
    if (Auth(1)=="False"): return "Status 401", 401
    oldTypeId = request.json.get("oldTypeId")
    newTypeId = request.json.get("newTypeId")
    if (oldTypeId is None) or (newTypeId is None): return "Status 400", 400
    if (oldTypeId <=0) or (newTypeId <=0): return "Status 400", 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal where id = '"+str(animalId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
        cur.execute("SELECT id FROM Animal_Type where id = '"+str(oldTypeId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
        cur.execute("SELECT id FROM Animal_Type where id = '"+str(newTypeId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
        cur.execute("SELECT id FROM Animal_Types_Array where animal_id	 = '"+str(animalId)+"' and animal_type_id = '"+str(oldTypeId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
    except: return "Status 404 type", 404 
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal_Types_Array where animal_id	 = '"+str(animalId)+"' and animal_type_id = '"+str(newTypeId)+"';")
        if ( cur.fetchall()[0].get("id") is not None): return "Status 409 type", 409
    except: pass
    cur.execute("UPDATE Animal_Types_Array SET animal_type_id = '"+str(newTypeId)+"' where animal_id	 = '"+str(animalId)+"' and animal_type_id ='"+str(oldTypeId)+"';")
    mysql.connection.commit()
    return jsonify(Animalprint(animalId)),200

@app.route('/animals/-<int:animalId>/types/<int:typesId>', methods=['DELETE'])
def animalsminustypesdel(animalId,typesId):
    return "Status 400", 400
@app.route('/animals/<int:animalId>/types/-<int:typesId>', methods=['DELETE'])
def animalstypesminusdel(animalId,typesId):
    return "Status 400", 400
@app.route('/animals/-<int:animalId>/types/-<int:typesId>', methods=['DELETE'])
def animalsminustypesminusdel(animalId,typesId):
    return "Status 400", 400
@app.route('/animals/<int:animalId>/types/<int:typesId>', methods=['DELETE'])
def animalstypesdel(animalId,typesId):
    if (Auth(1)=="False"): return "Status 401", 401
    if animalId <=0 or typesId <=0: return "Status 400", 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal where id = '"+str(animalId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404", 404
        cur.execute("SELECT id FROM Animal_Type where id = '"+str(typesId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404", 404
        cur.execute("SELECT id FROM Animal_Types_Array where animal_id	 = '"+str(animalId)+"' and animal_type_id = '"+str(typesId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404", 404
    except: return "Status 404", 404 
    cur = mysql.connection.cursor()
    cur.execute("select count(*) from Animal_Types_Array where animal_id = '"+str(animalId)+"';")
    if ( cur.fetchall()[0].get("count(*)") < 2): return "Status 400", 400
    cur.execute("DELETE FROM Animal_Types_Array where animal_type_id ="+str(typesId)+" and animal_id ="+str(animalId)+";")
    mysql.connection.commit()
    return jsonify(Animalprint(animalId)),200
####################################################
#################### Location Animals ##############
@app.route("/animals/-<int:animalId>/locations", methods=['GET'])
def animalsminuslocget(animalId):
    return "Status 400", 400
@app.route("/animals/<int:animalId>/locations", methods=['GET'])
def animalslocget(animalId):
    if (Auth(0)=="False"): return "Status 401",401
    if animalId <= 0: return "Status 400",400
    startDateTime = request.args.get('startDateTime')
    endDateTime = request.args.get('endDateTime')
    froma = request.args.get('from',default=1,type=int)
    sizea = request.args.get('size',default=10,type=int)
    ####################################################
    if froma < 0: return "Status 400", 400
    if sizea <= 0: return "Status 400", 400
    try:
        if startDateTime is not None:
            if (str(datetime.strptime(startDateTime, "%Y-%m-%dT%H:%M:%S").isoformat())) != startDateTime: return "Status 400", 400
        if endDateTime is not None:
            if (str(datetime.strptime(endDateTime, "%Y-%m-%dT%H:%M:%S").isoformat())) != endDateTime: return "Status 400", 400
    except: return "Status 400", 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal where id = '"+str(animalId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
    except: return "Status 404", 404 
    ########################### Поиск в БД ##################
    cur = mysql.connection.cursor()
    try:
        query = "SELECT * FROM Animal_Visited_Location where id > 0"
        if startDateTime is not None: 
            query = query + " and chippingDateTime >= '"+str(startDateTime)+"' "
        if endDateTime is not None: 
            query = query + " and chippingDateTime <= '"+str(endDateTime)+"' "
        query = query + " and animalId = '"+str(animalId)+"' "
        query = query + " limit "+str(sizea)+" offset "+str(froma)+";"
        cur.execute(query)
        rv = cur.fetchall()
        for i in rv:
            del i["animalId"]
            i["dateTimeOfVisitLocationPoint"]=str(i.get("dateTimeOfVisitLocationPoint").isoformat())+"Z"
        return jsonify(rv),200
    except: return "Такого животного нет", 200

@app.route('/animals/-<int:animalId>/locations/<int:pointId>', methods=['POST'])
def animalsminuslocationsinsert(animalId,pointId):
    return "Status 400", 400
@app.route('/animals/<int:animalId>/locations/-<int:pointId>', methods=['POST'])
def animalslocationsminusinsert(animalId,pointId):
    return "Status 400", 400
@app.route('/animals/-<int:animalId>/locations/-<int:pointId>', methods=['POST'])
def animalsminuslocationsminusinsert(animalId,pointId):
    return "Status 400", 400
@app.route('/animals/<int:animalId>/locations/<int:pointId>', methods=['POST'])
def animalslocationsinsert(animalId,pointId):
    if (Auth(1)=="False"): return "Status 401", 401
    if (animalId <=0) or (pointId <=0): return "Status 400", 400
    dateTimeOfVisitLocationPoint = datetime.datetime.now().replace(microsecond=0).isoformat()
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id,lifeStatus FROM Animal where id = '"+str(animalId)+"';")
        otv = cur.fetchall()[0]
        if ( otv.get("id") is None): return "Status 404 type", 404
        if ( otv.get("lifeStatus") == "DEAD"): return "Status 400", 400
        cur.execute("SELECT id FROM Location_Point where id = '"+str(pointId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
        cur.execute("select locationPointId	from Animal_Visited_Location where animalId = '"+str(animalId)+"' limit 1;")
        firstpoint = cur.fetchall()[0].get("locationPointId	")
        if firstpoint == pointId: return "Status 400", 400
    except: return "Status 404", 404
    cur.execute("select locationPointId	from Animal_Visited_Location where animalId = '"+str(animalId)+"';")
    firstpoint = cur.fetchall()[-1].get("locationPointId")
    if firstpoint == pointId: return "Status 400", 400
    cur.execute("""INSERT INTO Animal_Visited_Location (animalId, locationPointId,dateTimeOfVisitLocationPoint) 
    VALUES (%s,%s,%s);""",(animalId,pointId,dateTimeOfVisitLocationPoint))
    mysql.connection.commit()
    cur.execute("select id,locationPointId,dateTimeOfVisitLocationPoint	from Animal_Visited_Location where animalId = '"+str(animalId)+"';")
    otv = cur.fetchall()[-1]
    dateTimeOfVisitLocationPoint = str(otv.get("dateTimeOfVisitLocationPoint").isoformat())+"Z"
    del otv["dateTimeOfVisitLocationPoint"]
    otv["dateTimeOfVisitLocationPoint"]= dateTimeOfVisitLocationPoint
    return jsonify(otv), 201

@app.route("/animals/-<int:animalId>/locations", methods=['PUT'])
def animalsputminuslocations(animalId):
    return "Status 400", 400
@app.route('/animals/<int:animalId>/locations', methods=['PUT'])
def  animalsupdatelocations(animalId):
    if animalId <=0: return "Status 400", 400
    if (Auth(1)=="False"): return "Status 401", 401
    visitedLocationPointId = request.json.get("visitedLocationPointId")
    locationPointId = request.json.get("locationPointId")
    if (visitedLocationPointId is None) or (locationPointId is None): return "Status 400", 400
    if (visitedLocationPointId <= 0) or (locationPointId <= 0): return "Status 400", 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal where id = '"+str(animalId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
        cur.execute("SELECT id FROM Location_Point where id = '"+str(locationPointId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
        cur.execute("SELECT id FROM Animal_Visited_Location where animalId = '"+str(animalId)+"' and id = '"+str(visitedLocationPointId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
    except: return "Status 404", 404
    try:
        cur.execute("select locationPointId	from Animal_Visited_Location where animalId = '"+str(animalId)+"' limit 1;")
        firstpoint = cur.fetchall()[0].get("locationPointId")
        if firstpoint == locationPointId: return "Status 400", 400
        cur.execute("select locationPointId	from Animal_Visited_Location where animalId = '"+str(animalId)+"' ORDER BY `id` desc limit 1;")
        lpoint = cur.fetchall()[0].get("locationPointId")
        if lpoint == locationPointId: return "Status 400", 400
        cur.execute("select locationPointId	from Animal_Visited_Location where animalId = '"+str(animalId)+"' and  id < '"+str(visitedLocationPointId)+"' ORDER BY `id` desc limit 1;")
        lastpoint = cur.fetchall()[0].get("locationPointId")
        cur.execute("select locationPointId	from Animal_Visited_Location where animalId = '"+str(animalId)+"' and  id > '"+str(visitedLocationPointId)+"' ORDER BY `id` limit 1;")
        nextpoint = cur.fetchall()[0].get("locationPointId")
        if lastpoint == locationPointId: return "Status 400", 400
        if nextpoint == locationPointId: return "Status 400", 400
    except: pass
    cur.execute("UPDATE Animal_Visited_Location SET locationPointId = '"+str(locationPointId)+"' where id = '"+str(visitedLocationPointId)+"';")
    mysql.connection.commit()
    cur.execute("select id,locationPointId,dateTimeOfVisitLocationPoint	from Animal_Visited_Location where id = '"+str(visitedLocationPointId)+"';")
    otv = cur.fetchall()[0]
    dateTimeOfVisitLocationPoint = str(otv.get("dateTimeOfVisitLocationPoint").isoformat())+"Z"
    del otv["dateTimeOfVisitLocationPoint"]
    otv["dateTimeOfVisitLocationPoint"]= dateTimeOfVisitLocationPoint
    return jsonify(otv), 200

@app.route('/animals/-<int:animalId>/locations/<int:visitedPointId>', methods=['DELETE'])
def animalsminuslocationsdel(animalId,visitedPointId):
    return "Status 400", 400
@app.route('/animals/<int:animalId>/locations/-<int:visitedPointId>', methods=['DELETE'])
def animalslocationsminusdel(animalId,visitedPointId):
    return "Status 400", 400
@app.route('/animals/-<int:animalId>/locations/-<int:visitedPointId>', methods=['DELETE'])
def animalsminuslocationsminusdel(animalId,visitedPointId):
    return "Status 400", 400
@app.route('/animals/<int:animalId>/locations/<int:visitedPointId>', methods=['DELETE'])
def animalslocationsdel(animalId,visitedPointId):
    if (Auth(1)=="False"): return "Status 401", 401
    if animalId <=0 or visitedPointId <=0: return "Status 400", 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Animal where id = '"+str(animalId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
        cur.execute("SELECT id FROM Animal_Visited_Location where animalId = '"+str(animalId)+"' and id = '"+str(visitedPointId)+"';")
        if ( cur.fetchall()[0].get("id") is None): return "Status 404 type", 404
    except: return "Status 404", 404
    cur.execute("DELETE FROM Animal_Visited_Location where id ="+str(visitedPointId)+";")
    mysql.connection.commit()
    return "Status 200",200
if __name__ == "__main__":
    app.run(host="0.0.0.0",port="5000")
