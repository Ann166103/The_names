from flask import Flask, request, jsonify
import logging
import random

# создаём приложение
# мы передаём __name__, в нём содержится информация,
# в каком модуле мы находимся.
# В данном случае там содержится '__main__',
# так как мы обращаемся к переменной из запущенного модуля.
# если бы такое обращение, например, произошло внутри модуля logging,
# то мы бы получили 'logging'
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Создадим словарь, чтобы для каждой сессии общения
# с навыком хранились подсказки, которые видел пользователь.
# Это поможет нам немного разнообразить подсказки ответов
# (buttons в JSON ответа).
# Когда новый пользователь напишет нашему навыку,
# то мы сохраним в этот словарь запись формата
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!" ]}
# Такая запись говорит, что мы показали пользователю эти три подсказки.
# Когда он откажется купить слона,
# то мы уберем одну подсказку. Как будто что-то меняется :)
sessionStorage = {}


@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON,
# который отправила нам Алиса в запросе POST
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
                "Правила!",
            ]
        }
        # Заполняем текст ответа
        res['response'][
            'text'] = 'Вы называете имя, а я говорю имя на последнюю букву - и так далее. Только учтите - мягкий' \
                      ' и твердый знак, а также и буквы "ы" и "й" не считаются. Называйте имя! Можете начать со своего'
        with open('names_for_user.txt', 'w', encoding='utf-8') as f:
            f.write('')
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст,
    # что нам прислал пользователь
    # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо',
    # то мы считаем, что пользователь согласился.
    # Подумайте, всё ли в этом фрагменте написано "красиво"?
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        'Я покупаю',
        'Я куплю'
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return

    # Если нет, то убеждаем его купить слона!
    name = req['request']['original_utterance']
    if name:
        name = name.capitalize()
        with open('name.txt', encoding='utf-8') as f:
            a = list(map(lambda x: x[:-1], f.readlines()))
        with open('names_for_user.txt', encoding='utf-8') as f:
            b = list(map(lambda x: x[:-1], f.readlines()))
        if b:
            letterb = b[-1][-1] if b[-1][-1] != 'ь' and b[-1][-1] != 'ы' and b[-1][-1] != 'й' else b[-1][-2]
            if name not in a:
                test_answer = f'Не уверена, что такое имя существует. Вам на "{letterb.capitalize()}"'
            elif name[0] != letterb.capitalize():
                test_answer = f'Вы назвали имя не на ту букву. Вам на "{letterb.capitalize()}"'
            elif name in a and name in b:
                test_answer = f'Такое имя уже было. Вам на "{letterb.capitalize()}"'
            else:
                letter = name[-1] if name[-1] != 'ь' and name[-1] != 'ы' and name[-1] != 'й' else name[-2]
                a = list(filter(lambda x: x[0] == letter.upper() and x not in b, a))
                test_answer = a[random.randrange(len(a))]
                b.append(name)
                b.append(test_answer)
        else:
            if name not in a:
                test_answer = f'Не уверена, что такое имя существует.'
            else:
                letter = name[-1] if name[-1] != 'ь' and name[-1] != 'ы' and name[-1] != 'й' else name[-2]
                a = list(filter(lambda x: x[0] == letter.upper() and x not in b, a))
                test_answer = a[random.randrange(len(a))]
                b.append(name)
                b.append(test_answer)
        with open('names_for_user.txt', 'w', encoding='utf-8') as f:
            for i in b:
                f.write(i + '\n')
    res['response']['text'] = test_answer
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
