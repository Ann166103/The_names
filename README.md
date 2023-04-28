# Alice Skill The_names
Навык алисы "Игра Имена"

* [Документация](https://yandex.ru/dev/dialogs/alice/doc/index.html)
* [Создать диалог](https://dialogs.yandex.ru/developer/skills/)
* [Инструкция по размещению](https://yandex.ru/dev/dialogs/alice/doc/quickstart-programming.html)

## Настойка диалога

### Главные настройки
В поле `Backend` выбираем пункт `Webhook URL` и указываем ссылку
```shell
https://capable-balanced-path.glitch.me/post
```
## Правила ##
Пользователь называете имя, а Алиса говорит имя на последнюю букву - и так далее. Мягкий и твердый знак, а также и буквы "ы" и "й" не считаются. 
