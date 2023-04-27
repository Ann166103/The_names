from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    # Преобразовываем в JSON и возвращаем
    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз

        sessionStorage[user_id] = {
            'suggests': [
                "Подсказка",
                "На какую букву ходить",
                "Правила",
            ]
        }
        # Заполняем текст ответа
        # Используем изображение из ресурсов
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = '1533899/9e82819a86739cb9e5bd'
        res['response']['text'] = 'Игра в имена'
        res['response']['card'][
            'description'] = 'Это игра в имена. Вы называете имя, а я говорю имя на последнюю букву - и так далее.' \
                             ' Только учтите - мягкий и твердый знаки, а также и буквы "ы" и "й"' \
                             ' не считаются. Называйте имя! Можете начать со своего'
        with open('names_for_user.txt', 'w', encoding='utf-8') as f:
            f.write('')
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обрабатываем ответ пользователя.
    name = req['request']['original_utterance']
    with open('name.txt', encoding='utf-8') as f:
        all_names = list(map(lambda x: x[:-1], f.readlines()))
    with open('names_for_user.txt', encoding='utf-8') as f:
        names_for_user = list(map(lambda x: x[:-1], f.readlines()))
    # Обрабатываем сторонние ветки
    if 'правила' in name.lower():
        res['response']['text'] = 'Вы называете имя, а я говорю имя на последнюю букву - и так далее. Только ' \
                                  'учтите – мягкий и твердый знак, а также и буквы "ы" и "й" не считаются'
        res['response']['buttons'] = get_suggests(user_id)
        return
    if "букв" in name.lower():
        if names_for_user:
            last_letter = names_for_user[-1][-1] if names_for_user[-1][-1] != 'ь' and \
                                                    names_for_user[-1][-1] != 'ы' and \
                                                    names_for_user[-1][-1] != 'й' else names_for_user[-1][-2]
            res['response']['text'] = f'Назовите имя на букву "{last_letter.capitalize()}"'
        else:
            res['response']['text'] = 'Ваш ход – вам и решать'
        res['response']['buttons'] = get_suggests(user_id)
        return
    if 'подсказк' in name.lower():
        if names_for_user:
            last_letter = names_for_user[-1][-1] if names_for_user[-1][-1] != 'ь' and \
                                                    names_for_user[-1][-1] != 'ы' and \
                                                    names_for_user[-1][-1] != 'й' else names_for_user[-1][-2]
            all_names = list(filter(lambda x: x[0] == last_letter.upper() and x not in names_for_user, all_names))
            if len(all_names) == 0:
                res['response']['text'] = f'У меня закончились имена на ' \
                                          f'букву "{last_letter.capitalize()}"! Игра окончена. Жду вас снова!'
                res['response']['end_session'] = True
                return
        test_answer_1 = list(all_names[random.randrange(len(all_names))].upper())
        random.shuffle(test_answer_1)
        test_answer_1 = f'Такое сочетание букв ничего не напоминает "{"".join(test_answer_1)}"?'
        all_names_2 = list(filter(lambda x: len(x) > 5, all_names))
        word = all_names_2[random.randrange(len(all_names_2))]
        test_answer_2 = f'В имени {len(word)} букв. Начинается на "{word[:4]}"'
        text_answer = [test_answer_1, test_answer_2][random.randrange(2)]
        res['response']['text'] = text_answer
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обрабатываем основную ветку
    if name:
        name = name.capitalize()
        if names_for_user:
            last_letter = names_for_user[-1][-1] if names_for_user[-1][-1] != 'ь' and \
                                                    names_for_user[-1][-1] != 'ы' and \
                                                    names_for_user[-1][-1] != 'й' else names_for_user[-1][-2]
            if name not in all_names:
                text_answer = f'Не уверена, что такое имя существует. Вам на "{last_letter.capitalize()}"'
            elif name[0] != last_letter.capitalize():
                text_answer = f'Вы назвали имя не на ту букву. Вам на "{last_letter.capitalize()}"'
            elif name in all_names and name in names_for_user:
                text_answer = f'Такое имя уже было. Вам на "{last_letter.capitalize()}"'
            else:
                letter = name[-1] if name[-1] != 'ь' and name[-1] != 'ы' and name[-1] != 'й' else name[-2]
                all_names = list(filter(lambda x: x[0] == letter.upper() and x not in names_for_user, all_names))
                if len(all_names) == 0:
                    res['response']['text'] = f'У меня закончились имена на ' \
                                              f'букву "{letter.capitalize()}"! Игра окончена. Жду вас снова!'
                    res['response']['end_session'] = True
                    return
                text_answer = all_names[random.randrange(len(all_names))]
                names_for_user.append(name)
                names_for_user.append(text_answer)
        else:
            if name not in all_names:
                text_answer = f'Не уверена, что такое имя существует.'
            else:
                letter = name[-1] if name[-1] != 'ь' and name[-1] != 'ы' and name[-1] != 'й' else name[-2]
                all_names = list(filter(lambda x: x[0] == letter.upper() and x not in names_for_user, all_names))
                text_answer = all_names[random.randrange(len(all_names))]
                names_for_user.append(name)
                names_for_user.append(text_answer)
        with open('names_for_user.txt', 'w', encoding='utf-8') as f:
            for i in names_for_user:
                f.write(i + '\n')
    res['response']['text'] = text_answer
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    session['suggests'] = session['suggests']
    sessionStorage[user_id] = session

    return suggests


if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')
