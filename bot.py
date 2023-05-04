from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from locations import locations_dic
import telegram
import logging
import io
import random
from time import sleep

# Here you should put your bot's token

updater = Updater(token='', use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Меню с кнопками // Menu with buttons

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

# Клавиатура изначальная // Main keyboard

def keyboard():
    button_list = [
    telegram.InlineKeyboardButton("Правила", callback_data="rl"),
    telegram.InlineKeyboardButton("Локации", callback_data="lc"),
    telegram.InlineKeyboardButton("Обратная связь", callback_data="fb")
    ]
    return telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=3))

 #Стартовое сообщение, выводит меню с функционалом // Starting message, shows functional menu

def start(update, context):
    if update.message.chat.type == 'private':
        context.bot.send_message(chat_id=update.effective_chat.id, text = "test", reply_markup = keyboard())

# Выводит краткий список правил // Shows short rule's list

def rules(update, context):
    query = update.callback_query
    header_buttons = telegram.InlineKeyboardButton("Полная версия правил", callback_data="rlf")
    button_list = [
    telegram.InlineKeyboardButton("Локации", callback_data="loc"),
    telegram.InlineKeyboardButton("Обратная связь", callback_data="fb"),
    telegram.InlineKeyboardButton("Назад", callback_data="b") ]
    reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=3, header_buttons = header_buttons))
    rule = io.open('file.txt', encoding='utf-8')
    query.edit_message_text(text=rule.read(), reply_markup=reply_markup)
    
# Кидает PDF-файл с официальными правилами от Hobby World // Sends PDF file with Hobby's World official rules
   
def rulelist(update, context):
    query = update.callback_query
    context.bot.send_document(chat_id=update.effective_chat.id, document=open('rules.pdf', 'rb'))

# Возвращает обратно к /start // Returns back to /start

def back(update, context):
    query = update.callback_query
    query.edit_message_text(text = "test", reply_markup=keyboard())

# Выводит список всех локаций, доступных в игре / Sends a list of the locations

def locations(update, context):
    query = update.callback_query
    button_list = [
    telegram.InlineKeyboardButton("Правила", callback_data="rl"),
    telegram.InlineKeyboardButton("Обратная связь", callback_data="fb"),
    telegram.InlineKeyboardButton("Назад", callback_data="b")
    ]
    reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    location = io.open('location.txt', encoding='utf-8')
    query.edit_message_text(text = location.read(), reply_markup=reply_markup)

# Выводит способ связаться со мной / Sends a way to contact me

def feedback(update, context):
    query = update.callback_query
    button_list = [
    telegram.InlineKeyboardButton("Правила", callback_data="rl"),
    telegram.InlineKeyboardButton("Локации", callback_data="loc"),
    telegram.InlineKeyboardButton("Назад", callback_data="b")
    ]
    reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    feedback = io.open('feedback.txt', encoding='utf-8')
    query.edit_message_text(text = feedback.read(), reply_markup=reply_markup)

#Cleanup after game is finished

def clearGame(): 
    global group_id
    global player_dict
    global host_id
    global phase
    global abstain_votes
    global abort_confirmation
    global roles

    group_id = 0 #Default group ID redacted
    player_dict = {}
    host_id = 0
    phase = 'off' #off, startup, day, night
    abstain_votes = 0
    abort_confirmation = False
    roles = []
    loc = ""


# Начало игры

def create(update, context):
    global group_id
    global phase
    host_id = update.message.from_user.id
    if not phase == 'off':
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Игра уже создана. Введите команду /join чтобы присоединиться",reply_to_message_id=update.message.message_id)
    elif update.message.chat.type == 'private' or update.message.chat.type == 'channel':
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Чтобы создать игру, введите команду /create в группе, где будет проходить игра",
        reply_to_message_id=update.message.message_id)
    else:
        host_id = update.message.from_user.id
        host_name = update.message.from_user.first_name
        player_dict[host_id] = host_name
        group_id = update.message.chat_id
        phase = 'startup'
        button = [telegram.InlineKeyboardButton("Ознакомиться",  url = "t.me/BoardGameSpyBot", callback_data = "join")]
        reply_markup = telegram.InlineKeyboardMarkup(build_menu(button, n_cols=1))
        context.bot.sendMessage(chat_id=group_id, text="Игра начата! Чтобы присоединиться, ОБЯЗАТЕЛЬНО ознакомтесь с правилами игры по кнопке ниже, а после введите в чате команду /join .", reply_markup = reply_markup)

#Команла присоединения

def join(update, context):
    if phase == 'off':
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="Игра еще не создана. Чтобы создать её пропишите команду /create", reply_to_message_id=update.message.message_id)
    elif update.message.from_user.id in player_dict:
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="Ты уже в игре.", reply_to_message_id=update.message.message_id)
    elif not phase == 'startup':
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="Sorry, the game has already started. Join the next one!",
        reply_to_message_id=update.message.message_id)
    elif not update.message.chat.type == 'private':
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="Пожалуйста, введите команду /join мне в личку",
        reply_to_message_id=update.message.message_id)
    else:
        chat_id = update.message.from_user.id
        new_user = update.message.from_user
        name = new_user.first_name
        player_dict[new_user.id] = name
        string = "You have joined the game!\n"
        context.bot.sendMessage(chat_id=new_user.id, text=string)

#Returns a list of players who have joined

def playerlist(update, context): 
    global player_dict
    if len(player_dict) == 0:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="No players yet.",reply_to_message_id=update.message.message_id)
    else:
        string = 'The players are:\n'
        for i in list(player_dict.values()):
            string += i
            string += "\n"   
        string = string[:-1]
        context.bot.sendMessage(chat_id=update.message.chat_id, text=string)

#Starts the game

def game_start(update, context): 
    global phase
    global player_dict
    global mafia_ids
    global host_id
    global group_id
    global roles
    global spy_id
    global loc

    if phase == 'off':
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Игра еще не создана. Чтобы создать напишите команду /create в общий чат",reply_to_message_id=update.message.message_id)
    elif phase == 'game':
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Игра уже началась!",reply_to_message_id=update.message.message_id)
    elif len(player_dict) < 3:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Для начала игры нужно минимум 3 игрока",reply_to_message_id=update.message.message_id)
    else:
        phase = 'game'
        loc = random.choice(list(locations_dic.keys()))    
        spy_id = random.choice(list(player_dict.keys()))
        roles = random.shuffle(locations_dic[loc])
        non_spy = {}

        # Генерирует роль для каждого 

        for id in list(player_dict.keys()):
            if id == spy_id:
                continue
            else:
                role = random.choice(locations_dic[loc])
                while role in list(non_spy.values()):
                    role = random.choice(locations_dic[loc])
                non_spy[id] = role
        
            context.bot.sendMessage(chat_id = id, text = "Вы - нешпион.\nЛокация = %s\nРоль = %s" % (loc, non_spy[id]))
        
        spy_loc = []
        for l in list(locations_dic.keys()):
            spy_loc.append(telegram.InlineKeyboardButton(l, callback_data = "choose"))
        reply_markup_spy = telegram.InlineKeyboardMarkup(build_menu(spy_loc, n_cols=3))
        context.bot.sendMessage(chat_id = spy_id, text= "Вы - шпион. Вы должны угадать локацию, на которой находятся остальные игроки", reply_markup = reply_markup_spy)
        context.bot.sendMessage(chat_id = update.message.chat_id, text= "Игра началась! Вы можете посмотреть свои роли в личных сообщениях.")

"""def guess(update, context):
    global spy_id
    global loc
    global group_id

    if not phase == "game":
        context.bot.sendMessage(chat_id = update.message.chat_id, text= "Эта команда доступна только во время игры!")
    elif not update.message.chat.type == "private":
        context.bot.sendMessage(chat_id = update.message.chat_id, text= "Эх ты! Эту команду нужно писать мне в личные сообщения. Теперь все знают, что ты шпион")
    elif update.message.from_user.id != spy_id:
        context.bot.sendMessage(chat_id = update.message.chat_id, text= "Эта команда доступна только шпиону!")
    else:
        print(context.args)
        if context.args[0] == loc:
            context.bot.sendMessage(chat_id = update.message.chat_id, text= "Ты угадал! Поздравляю с победой", reply_to_message_id=update.message.message_id)
            context.bot.sendMessage(chat_id = group_id, text= "Игра окончена! Победил шпион %s, он правильно угадал локацию!" % (player_dict[spy_id]))
        else:
            context.bot.sendMessage(chat_id = update.message.chat_id, text= "К сожалению, ты проиграл. Правильный ответ - %s. Повезет в следующий раз!" % (loc), reply_to_message_id=update.message.message_id)
            context.bot.sendMessage(chat_id = group_id, text= "Игра окончена! Шпион %s неправильно назвал локацию. Поздравляю нешпионов с победой!" % (player_dict[spy_id]))
        clearGame()"""

#Haven't implemented this function yet, must make some changes
def guess(update, context):
    query = update.callback_query
    global loc
    global group_id
    print(query)
    # Не спрашивайте почему так, эта строчка определяет текст кнопки
    bt = query["message"]["reply_markup"]["inline_keyboard"][0][0]["text"]
    print( "Я не ебу что это " + bt)
    print("Это локация которая сейчас в игре - " + loc)

    if bt == loc:
        query.edit_message_text(text= "Ты угадал! Поздравляю с победой")
        context.bot.sendMessage(chat_id = group_id, text= "Игра окончена! Победил шпион %s, он правильно угадал локацию!" % (player_dict[spy_id]))
    else:
        query.edit_message_text(text= "К сожалению, ты проиграл. Правильный ответ - %s. Повезет в следующий раз!" % (loc))
        context.bot.sendMessage(chat_id = group_id, text= "Игра окончена! Шпион %s неправильно назвал локацию. Поздравляю нешпионов с победой!" % (player_dict[spy_id]))
    clearGame()

def vote():
    votes = {}
    players = list(player_dict.values())
    for i in players:
        votes[i] = 0
    button_list= []
    for p in players:
        button_list.append(telegram.InlineKeyboardButton(text = p, callback_data="p"))
    reply_markup = reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    context.bot.sendMessage(chat_id=update.message.chat_id, text="Пришло время голосовать! Вы больше не можете задавать вопросы, но у вас есть одна минута для того, чтобы обсудить и решить кто является шпионом", reply_markup = reply_markup)
    time.sleep(60)
    target = votes.index(max(list(votes.values())))
    if player_dict.index(target) == spy_id:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Вы выиграли")
    else:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Вы проиграли")
    clearGame()

def voting(call):
    vote[call.data] += 1
    print(vote)

game_start_handler = CommandHandler('game_start', game_start)
dispatcher.add_handler(game_start_handler)        

playerlist_handler = CommandHandler('playerlist',playerlist)
dispatcher.add_handler(playerlist_handler)

start_handler = CommandHandler('start', start)
create_handler = CommandHandler('create', create)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(create_handler)

join_handler = CommandHandler('join', join)
dispatcher.add_handler(join_handler)

guess_handler = CommandHandler('guess', guess)
dispatcher.add_handler(guess_handler)

updater.dispatcher.add_handler(CallbackQueryHandler(rules, pattern = "rl"))
updater.dispatcher.add_handler(CallbackQueryHandler(rulelist, pattern = "rlf"))
updater.dispatcher.add_handler(CallbackQueryHandler(back, pattern = "b"))
updater.dispatcher.add_handler(CallbackQueryHandler(locations, pattern = "lc"))
updater.dispatcher.add_handler(CallbackQueryHandler(feedback, pattern = "fb"))
updater.dispatcher.add_handler(CallbackQueryHandler(guess, pattern = "choose"))


clearGame()
updater.start_polling()
