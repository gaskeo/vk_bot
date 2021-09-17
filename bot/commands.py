def create_commands(bot) -> dict:
    return {
        # commands for all users
        "/": bot.redo_command,
        "/help": bot.show_help,

        "/gs": bot.get_synonyms,  # get synonyms
        "/synonyms": bot.get_synonyms,  # get synonyms
        "/синонимы": bot.get_synonyms,  # get synonyms

        "/cp": bot.create_postirony,  # create postirony
        "/postirony": bot.create_postirony,  # create postirony
        "/постирония": bot.create_postirony,  # create postirony

        "/cs": bot.create_shakal,  # create shakal
        "/shakal": bot.create_shakal,  # create shakal
        "/шакал": bot.create_shakal,  # create shakal

        "/cg": bot.create_grain,  # create grain
        "/grain": bot.create_grain,  # create grain
        "/зернистость": bot.create_grain,  # create grain

        "/ca": bot.create_arabfunny,  # create arabfunny
        "/arabfunny": bot.create_arabfunny,  # create arabfunny
        "/арабфанни": bot.create_arabfunny,  # create arabfunny

        "/cd": bot.create_dab,
        "/dab": bot.create_dab,
        "/дэб": bot.create_dab,

        "/ut": bot.get_uptime,
        "/uptime": bot.get_uptime,
        "/время": bot.get_uptime,

        "/a": bot.alive,
        "/alive": bot.alive,
        "/живой": bot.alive,

        "/ck": bot.clear_keyboard,
        "/keyboard": bot.clear_keyboard,
        "/клавиатура": bot.clear_keyboard,

        "/yn": bot.answer_yes_no,
        "/yesno": bot.answer_yes_no,
        "/ответ": bot.answer_yes_no,

        # in chats only
        "/gac": bot.get_chance,  # get answer chance
        "/get_answer": bot.get_chance,  # get answer chance
        "/шансответа": bot.get_chance,  # get answer chance

        "/ghc": bot.get_chance,  # get huy chance
        "/get_huy": bot.get_chance,  # get huy chance
        "/шансхуя": bot.get_chance,  # get huy chance

        "/gc": bot.get_count_words,
        "/get_count_words": bot.get_count_words,
        "/слов": bot.get_count_words,

        "/si": bot.search_image,
        "/search_image": bot.search_image,
        "/картинка": bot.search_image,

        # "/gsw": bot.get_similarity_words,
        "/g": bot.generate_speak,
        "/generate": bot.generate_speak,
        "/скажи": bot.generate_speak,

        "/at": bot.get_words_after_that,
        "/after_that": bot.get_words_after_that,
        "/после": bot.get_words_after_that,

        "/p": bot.get_peer,
        "/peer": bot.get_peer,
        "/айди": bot.get_peer,

        "/gnt": bot.generate_token,
        "/generate_new_token": bot.generate_token,
        "/сгенерируй": bot.generate_token,

        "/c": bot.connect,
        "/connect": bot.connect,
        "/присоединиться": bot.connect,

        "/send": bot.send_other_chat,
        "/отправить": bot.send_other_chat,

        "/l": bot.lox_command,
        "/lox": bot.lox_command,
        "/л": bot.lox_command,

        "/mc": bot.get_my_count,
        "/my_count": bot.get_my_count,
        "/написал": bot.get_my_count,

        "/gt": bot.get_top,
        "/get_top": bot.get_top,
        "/топ": bot.get_top,

        "/cc": bot.create_chat,

        # for chat admins only
        "/tac": bot.toggle_access_chat_settings,  # toggle access
        "/ac": bot.set_chance,  # set answer chance
        "/hc": bot.set_chance,  # set huy chance
        "/s": bot.show_settings,  # settings
        "/clear": bot.clear_chat_speaker,
        "/update": bot.update_chat,
        "/dt": bot.delete_this,
        "/disconnect": bot.disconnect,
        "/accept_connect": bot.accept_connect,
        # "/dsw": bot.clear_similarity_words,
        # for bot admins only
        "/adm": bot.admin_help,  # help admins
        "/sa": bot.set_admin,  # set admin
        "/ga": bot.get_admin,  # get admin
        "/ia": bot.is_admin,  # is admin
        "/bb": bot.bye_bye,  # exit program
        "/th": bot.alive_threads,
        "/sp": bot.send_in_peer,
        # experimental
        "/csg": None,  # create gif shakal
        "/cag": None,  # create gif arabfunny
        # other
        "other": bot.send_answer,  # answer on simple message
        # archive
        "/glc": bot.archived,  # get ladno chance
        "/gnc": bot.archived,  # get nu... chance
        "/lc": bot.archived,  # set ladno chance
        "/nc": bot.archived,  # set nu... chance
        "/test": bot.test
    }
