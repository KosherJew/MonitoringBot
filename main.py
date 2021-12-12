import telebot, telebot.types as types,json,os, datetime as dt
from datetime import datetime
bot = telebot.TeleBot('5074269648:AAHeazmppyZrzDcyRuhs4SNuyXkvXrLneZ4')
with open('Activitys.json') as json_file:
    Activitys = json.load(json_file)
with open('Users.json') as json_file:
    Users = json.load(json_file)
with open('Admins.json') as json_file:
    Admins = json.load(json_file)
with open('Groups.json') as json_file:
    Groups = json.load(json_file)
ActivGroup =Groups['ActivGroup']
User_reg = {}

@bot.message_handler()
def comands(message):
    print(message)
    if message.chat.type == 'private':
        if message.chat.username in Users.keys():
            if message.text == '/start':
                RenderActivity("MainMenu",message)
                ClearChat(message.chat.id,message.id)
            elif message.text == '/admin':
                if message.chat.username in Admins:
                    RenderActivity("AdminMenu", message)  # Функция в разработке
                else:
                    bot.send_message(message.chat.id, text='Недостаточно прав. Не трогать! Напиши /help')
                ClearChat(message.chat.id,message.id)
            elif message.text == '/help':
                bot.send_message(message.chat.id, text="\n/start Главное меню\n\n/admin Админка, не лезь, оно тебя сожрет")
                ClearChat(message.chat.id,message.id)
            else:
                bot.send_message(message.chat.id, text='Напиши /help')
                ClearChat(message.chat.id,message.id)
        else:
            bot.send_message(message.chat.id, text='Я тебя не знаю. Попроси ТимЛида внести тебя.')
    else:
        if message.chat.title != 'ActivGroup':
            Groups[message.chat.title]=message.chat.id
            with open('Groups.json', 'w') as f:
                json.dump(Groups, f)
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    with open('DinerTimes.json') as json_file:
        Times = json.load(json_file)
    if call.data in Activitys.keys():
        RenderActivity(call.data,call.message)
    else: #Обработка форм
        if call.data == 'Today':
            Dinner(call.message,'Today')
        elif call.data == 'Tomorrow':
            Dinner(call.message,'Tomorrow')
        elif call.data == 'Notification':
            Text ='Введите в какой чат выводить уведомления:'
            for gr in Groups.keys():
                if gr !='ActivGroup':
                    Text +='\n' + gr
            bot.send_message(call.message.chat.id, Text)
            bot.register_next_step_handler(call.message, AdminNotif)
        elif call.data == 'AdminDinner':
            bot.send_message(call.message.chat.id, "Введите Дату в формате ДД-ММ-ГГГГ")
            bot.register_next_step_handler(call.message, AdminDinners)
        elif call.data == 'AdminBreaks':
            bot.send_message(call.message.chat.id, "Введите Ник телеграма и Дату в формате Ник:ДД-ММ-ГГГГ")
            bot.register_next_step_handler(call.message, AdminBreaks)
        elif call.data == 'TrueReg':
            Users[User_reg[call.message.chat.id]['teleg']] = {"Name": User_reg[call.message.chat.id]['Name'],"SurName": User_reg[call.message.chat.id]['SurName'],"Schedule": User_reg[call.message.chat.id]['Schedule'],"Caption":User_reg[call.message.chat.id]['Caption'],"Line": User_reg[call.message.chat.id]['Line']}
            with open('Users.json', 'w') as f:
                json.dump(Users, f)
            bot.send_message(call.message.chat.id, "Сотрудник успешно зарегестрирован")
            RenderActivity('AdminMenu',call.message)
        elif call.data == 'FalseReg':
            User_reg[call.message.chat.id] = {}
            bot.send_message(call.message.chat.id, "Введите имя сотрудника")
            bot.register_next_step_handler(call.message, Name)
            ClearChat(call.message.chat.id, call.message.id)
        elif call.data == 'AfterTomorrow':
            Dinner(call.message,'AfterTomorrow')
        elif call.data.find("|") != -1:
            splited = call.data.split('|')
            if splited[0] == 'Tomorrow':
                Data = datetime.now() + dt.timedelta(days=1)
            elif splited[0] == 'AfterTomorrow':
                Data = datetime.now() + dt.timedelta(days=2)
            elif splited[0] == 'Today':
                Data = datetime.now()
            with open('Dinners/' + Data.strftime("%d-%m-%Y") + '.json') as json_file:
                dinners = json.load(json_file)
            if len(dinners[Users[call.message.chat.username]["Line"]][splited[1]]) < 2 and dinners['Users'][call.message.chat.username] < 2:
                dinners[Users[call.message.chat.username]["Line"]][splited[1]].append(call.message.chat.username)
                dinners['Users'][call.message.chat.username] += 1
                bot.send_message(call.message.chat.id, text='Обед установлен на '+splited[1])
                with open('Dinners/' + Data.strftime("%d-%m-%Y") + '.json', 'w') as f:
                    json.dump(dinners, f)
                RenderActivity('Dinner', call.message)
            else:
                bot.send_message(call.message.chat.id, text='Не удалось зарезервировать обед на' + splited[1])
                RenderActivity('Dinner', call.message)
        elif call.data.find("HistoryDinner") != -1:
            splited = call.data.split(' ')
            if splited[1] == 'Tomorrow':
                Data = datetime.now() + dt.timedelta(days=1)
            elif splited[1] == 'AfterTomorrow':
                Data = datetime.now() + dt.timedelta(days=2)
            elif splited[1] == 'Today':
                Data = datetime.now()
            if os.path.isfile('Dinners/' + Data.strftime("%d-%m-%Y") + '.json'):
                with open('Dinners/' + Data.strftime("%d-%m-%Y") + '.json') as json_file:
                    dinners = json.load(json_file)
                if not call.message.chat.username in dinners['Users'].keys():
                    dinners['Users'][call.message.chat.username] = 0
            else:
                dinners = {"Users": {}, "Л1": {}, "Модерация": {}, "Почта": {}}
                with open('DinerTimes.json') as json_file:
                    Times = json.load(json_file)
                dinners['Users'][call.message.chat.username] = 0
                for time in Times:
                    dinners['Л1'][time] = []
                    dinners['Модерация'][time] = []
                    dinners['Почта'][time] = []
            with open('Dinners/' + Data.strftime("%d-%m-%Y") + '.json', 'w') as f:
                json.dump(dinners, f)
            keyboard = types.InlineKeyboardMarkup()
            Text = 'Перерывы на ' + Data.strftime("%d-%m-%Y")
            key = types.InlineKeyboardButton(text='назад', callback_data='HistoryDinner')
            keyboard.add(key)
            for din in dinners[Users[call.message.chat.username]["Line"]].keys():
                if call.message.chat.username in dinners[Users[call.message.chat.username]["Line"]][din]:
                    key = types.InlineKeyboardButton(text=din, callback_data= din)
                    keyboard.add(key)
            bot.send_message(call.message.chat.id, text=Text, reply_markup=keyboard)
            ClearChat(call.message.chat.id,call.message.id)
        elif call.data.find("OpenShift") != -1:
            Data = datetime.now()
            breaks = LoadBreaks(Data,call)
            breaks['Start'] =Data.strftime("%H:%M:%S")
            SaveBreaks(Data,call,breaks)
            bot.send_message(call.message.chat.id, text='Смена открыта')
            SendToActivGroup('@'+call.message.chat.username + ' На смене' )
            RenderActivity('MainMenu', call.message)
        elif call.data.find("CloseShift") != -1:
            Data = datetime.now()
            breaks = LoadBreaks(Data,call)
            breaks['Stop'] = Data.strftime("%H:%M:%S")
            SaveBreaks(Data,call,breaks)
            bot.send_message(call.message.chat.id, text='Смена закрыта')
            SendToActivGroup('@' + call.message.chat.username + ' Закончил смену')
            RenderActivity('MainMenu', call.message)
        elif call.data.find("DinnerBreak") != -1:
            SetBreak(call, 'Обед')
        elif call.data.find("BreakN") != -1:
            SetBreak(call, 'Перерыв')
        elif call.data.find("TechnicalProblems") != -1:
            SetBreak(call, 'Технические трудности')
        elif call.data.find("Break 5") != -1:
            SetBreak(call,'Перерыв 5 минут')
        elif call.data.find("Break 10") != -1:
            SetBreak(call,'Перерыв 10 минут')
        elif call.data.find("Break 15") != -1:
            SetBreak(call,'Перерыв 15 минут')
        elif call.data.find("StopBreak") != -1:
            Data = datetime.now()
            breaks = LoadBreaks(Data,call)
            for br in breaks['Breaks']:
                if br['StopTime'] == '':
                    br['StopTime'] = Data.strftime("%H:%M:%S")
            SaveBreaks(Data,call,breaks)
            SendToActivGroup('@' + call.message.chat.username+' Вернулся')
            RenderActivity('SetBreak', call.message)
        elif call.data.find("HistoryBreak") != -1:
            Data = datetime.now()
            breaks = LoadBreaks(Data, call)
            keyboard = types.InlineKeyboardMarkup()
            key = types.InlineKeyboardButton(text='назад', callback_data='MyBreaks')
            keyboard.add(key)
            Text = 'Перерывы на ' + Data.strftime("%d-%m-%Y")
            Text += '\nНачал смену в ' + breaks['Start']
            for br in breaks['Breaks']:
                Text += '\n' + br['Status'] + "\nс " + br['StartTime'] + "\nдо " + br['StopTime']
            Text += '\nЗакончил смену в ' + breaks['Stop']
            bot.send_message(call.message.chat.id, text=Text, reply_markup=keyboard)
            ClearChat(call.message.chat.id,call.message.id)
        elif call.data.find("reg") != -1:
            User_reg[call.message.chat.id] = {}
            bot.send_message(call.message.chat.id, "Введите имя сотрудника")
            bot.register_next_step_handler(call.message, Name)  # следующий шаг – функция get_name

def LoadBreaks(Data,call):
    if os.path.isdir('Breaks/' + Data.strftime("%d-%m-%Y")):
        if os.path.isfile('Breaks/' + Data.strftime("%d-%m-%Y") + '/' + call.message.chat.username + '.json'):
            with open('Breaks/' + Data.strftime(
                    "%d-%m-%Y") + '/' + call.message.chat.username + '.json') as json_file:
                breaks = json.load(json_file)
        else:
            breaks = {'Start': '', 'Stop': '', 'Breaks': []}
    else:
        os.makedirs('Breaks/' + Data.strftime("%d-%m-%Y"))
        callback_worker(call)
        RenderActivity('SetBreak', call.message)
    return breaks
def SendToActivGroup(MessageText):
    if ActivGroup != '':
        bot.send_message(ActivGroup, text=MessageText)

def SaveBreaks(Data,call,breaks):
    with open('Breaks/' + Data.strftime("%d-%m-%Y") + '/' + call.message.chat.username + '.json', 'w') as f:
        json.dump(breaks, f)
def SetBreak(call,Status):
    Data = datetime.now()
    breaks = LoadBreaks(Data, call)
    breaks['Breaks'].append({'Status': Status, 'StartTime': Data.strftime("%H:%M:%S"), 'StopTime': ''})
    SaveBreaks(Data, call, breaks)
    SendToActivGroup('@' + call.message.chat.username+' '+Status)
    RenderActivity('SetBreak', call.message)
def Name(message):
    User_reg[message.chat.id]['Name'] = message.text

    bot.send_message(message.from_user.id, 'Введите фамилию сотрудника')
    bot.register_next_step_handler(message, get_surnme)
    ClearChat(message.chat.id, message.id)

def AdminNotif(message):
    try:
        Groups['ActivGroup'] = Groups[message.text]
        with open('Groups.json.json', 'w') as f:
            json.dump(Groups, f)
        RenderActivity('AdminMenu', message)
    except:
        Text = 'Данные введены некорректно. Введите в какой чат выводить уведомления:'
        for gr in Groups.keys():
            if gr != 'ActivGroup':
                Text += '\n' + gr
        bot.send_message(message.chat.id, Text)
        bot.register_next_step_handler(message, AdminNotif)
        ClearChat(message.chat.id, message.id)
def AdminDinners(message):
    if os.path.isfile('Dinners/' + message.text + '.json'):
        with open('Dinners/' + message.text + '.json') as json_file:
            dinners = json.load(json_file)
    else:
        dinners = {"Users": {}, "Л1": {}, "Модерация": {}, "Почта": {}}
        with open('DinerTimes.json') as json_file:
            Times = json.load(json_file)
        for time in Times:
            dinners['Л1'][time] = []
            dinners['Модерация'][time] = []
            dinners['Почта'][time] = []
    with open('Dinners/' + message.text + '.json', 'w') as f:
        json.dump(dinners, f)
    keyboard = types.InlineKeyboardMarkup()
    Text = 'Обеды на ' + message.text + '\n Список сотрудников:'
    key = types.InlineKeyboardButton(text='назад', callback_data='AdminMenu')
    keyboard.add(key)
    for din in dinners['Users'].keys():
        Text +='\n@'+ din
    Text += '\nЛ1:'
    for din in dinners['Л1'].keys():
        Text +='\n'+ din +' - ' + str(dinners['Л1'][din])
    Text += '\nМодерация:'
    for din in dinners['Модерация'].keys():
        Text +='\n'+ din +' - ' + str(dinners['Модерация'][din])
    Text += '\nПочта:'
    for din in dinners['Почта'].keys():
        Text +='\n'+ din +' - ' + str(dinners['Почта'][din])
    bot.send_message(message.chat.id, text=Text, reply_markup=keyboard)
    RenderActivity('AdminMenu', message)
    ClearChat(message.chat.id, message.id)

def AdminBreaks(message):
    if os.path.isdir('Breaks/' + message.text.split(':')[1]):
        if os.path.isfile('Breaks/' + message.text.split(':')[1] + '/' + message.text.split(':')[0] + '.json'):
            with open('Breaks/' + message.text.split(':')[1]+ '/' + message.text.split(':')[0] + '.json') as json_file:
                breaks = json.load(json_file)
        else:
            breaks = {'Start': '', 'Stop': '', 'Breaks': []}
    else:
        os.makedirs('Breaks/' + message.text.split(':')[1])
        AdminBreaks(message)
        RenderActivity('AdminMenu', message)
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='назад', callback_data='AdminMenu')
    keyboard.add(key)
    Text = 'Перерывы на ' + message.text.split(':')[1]
    Text += '\nНачал смену в ' + breaks['Start']
    for br in breaks['Breaks']:
        Text += '\n' +br['Status'] + "\nс " + br['StartTime'] + "\nдо " + br['StopTime']
    Text += '\nЗакончил смену в ' + breaks['Stop']
    bot.send_message(message.chat.id, text=Text, reply_markup=keyboard)
    ClearChat(message.chat.id, message.id)

def get_surnme(message):
    User_reg[message.chat.id]['SurName'] = message.text

    bot.send_message(message.from_user.id, 'Введите график в формате 00:00-00:00?')
    bot.register_next_step_handler(message, Schedule)
    ClearChat(message.chat.id, message.id)
def Schedule(message):
    User_reg[message.chat.id]['Schedule'] = message.text.split('-')
    bot.send_message(message.from_user.id, 'Комментарий к сотруднику')
    bot.register_next_step_handler(message, Caption)
    ClearChat(message.chat.id, message.id)
def Caption(message):
    User_reg[message.chat.id]['Caption'] = message.text
    bot.send_message(message.from_user.id, 'Линия на которой работает сотрудник')
    bot.register_next_step_handler(message, Line)
    ClearChat(message.chat.id, message.id)
def Line(message):
    User_reg[message.chat.id]['Line'] = message.text
    bot.send_message(message.from_user.id, 'Логин Telegram без @')
    bot.register_next_step_handler(message, teleg)
    ClearChat(message.chat.id, message.id)
def teleg(message):
    try:
        User_reg[message.chat.id]['teleg'] = message.text
        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='TrueReg')
        keyboard.add(key_yes)
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='FalseReg')
        keyboard.add(key_no)
        key = types.InlineKeyboardButton(text='Назад в админку', callback_data='AdminMenu')
        keyboard.add(key)
        question = 'Введенные данные:  ' + User_reg[message.chat.id]['Name'] + '  ' + User_reg[message.chat.id]['SurName'] + ', работает с ' + User_reg[message.chat.id]['Schedule'][0]  + ' до ' + User_reg[message.chat.id]['Schedule'][1]+ ' на линии ' + User_reg[message.chat.id]['Line'] + ' Он(а) ' + User_reg[message.chat.id]['Caption'] + ' для связи: @' + User_reg[message.chat.id]['teleg'];
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
        ClearChat(message.chat.id, message.id)
    except:
        bot.send_message(message.chat.id, "Неуспешная регистрация, повторите попытку.")
        RenderActivity('AdminMenu', message)

def Dinner(message,day):
    if day == 'Today':
        Data = datetime.now()
    elif day == 'Tomorrow':
        Data = datetime.now() + dt.timedelta(days=1)
    elif day == 'AfterTomorrow':
        Data = datetime.now() + dt.timedelta(days=2)
    if os.path.isfile('Dinners/'+Data.strftime("%d-%m-%Y")+'.json'):
        with open('Dinners/'+Data.strftime("%d-%m-%Y")+'.json') as json_file:
            dinners = json.load(json_file)
        if not message.chat.username in dinners['Users'].keys():
            dinners['Users'][message.chat.username] = 0
    else:
        dinners = {"Users":{},"Л1":{},"Модерация":{},"Почта":{}}
        with open('DinerTimes.json') as json_file:
            Times = json.load(json_file)
        dinners['Users'][message.chat.username]+=1
        for time in Times:
            dinners['Л1'][time] =[]
            dinners['Модерация'][time] = []
            dinners['Почта'][time] = []
    with open('Dinners/'+Data.strftime("%d-%m-%Y")+'.json', 'w') as f:
        json.dump(dinners, f)
    # Отрисовка формы
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='назад', callback_data='SetDinner')
    keyboard.add(key)
    Text = 'Свободное время на ' + Data.strftime("%d-%m-%Y")
    for din in dinners[Users[message.chat.username]["Line"]].keys():
        Ltime = din.split('-')
        if int(Ltime[0].split(':')[0])>int(Users[message.chat.username]['Schedule'][0].split(':')[0]) and int(Ltime[0].split(':')[0])<int(Users[message.chat.username]['Schedule'][1].split(':')[0])-1:
            if len(dinners[Users[message.chat.username]["Line"]][din])<2:
                key = types.InlineKeyboardButton(text=din, callback_data=day+'|'+din)
                keyboard.add(key)
    bot.send_message(message.chat.id, text=Text, reply_markup=keyboard)
    ClearChat(message.chat.id,message.id)
def RenderActivity(Name,message):
    keyboard = types.InlineKeyboardMarkup()
    Text = Activitys[Name]['Text']
    for k in Activitys[Name]['Keys'].keys():
        key = types.InlineKeyboardButton(text=k, callback_data=Activitys[Name]['Keys'][k])
        keyboard.add(key)  # добавляем кнопку в клавиатуру
    bot.send_message(message.chat.id, text=Text, reply_markup=keyboard)
    ClearChat(message.chat.id,message.id)
def ClearChat(chatid,messageid):
    for id in range(messageid,0,-1):
        try:
            bot.delete_message(chatid, id)
        except:
            break

bot.polling(none_stop=True, interval=0)