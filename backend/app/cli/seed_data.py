
from app.models.database import AchievementType

MODULES_DATA = [
    {
        "title": "Введение в SQL",
        "description": "Основы работы с SQL: создание запросов, выборка данных, базовые операции",
        "order": 1,
        "is_published": True,
    },
    {
        "title": "Работа с таблицами",
        "description": "Создание, изменение и удаление таблиц. Работа со структурой данных",
        "order": 2,
        "is_published": True,
    },
    {
        "title": "Фильтрация и сортировка",
        "description": "Использование WHERE, ORDER BY, LIMIT для управления выборкой данных",
        "order": 3,
        "is_published": True,
    },
    {
        "title": "Агрегация данных",
        "description": "Функции COUNT, SUM, AVG, MIN, MAX и группировка с GROUP BY",
        "order": 4,
        "is_published": True,
    },
    {
        "title": "Объединение таблиц",
        "description": "JOIN операции: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN",
        "order": 5,
        "is_published": True,
    },
    {
        "title": "Подзапросы",
        "description": "Вложенные запросы, коррелированные подзапросы, использование IN и EXISTS",
        "order": 6,
        "is_published": True,
    },
    {
        "title": "Индексы и оптимизация",
        "description": "Создание индексов, анализ производительности, оптимизация запросов",
        "order": 7,
        "is_published": True,
    },
    {
        "title": "Транзакции и блокировки",
        "description": "ACID свойства, управление транзакциями, уровни изоляции",
        "order": 8,
        "is_published": True,
    },
    {
        "title": "Хранимые процедуры",
        "description": "Создание и использование функций, процедур и триггеров",
        "order": 9,
        "is_published": True,
    },
    {
        "title": "Продвинутые техники",
        "description": "Оконные функции, CTE (Common Table Expressions), рекурсивные запросы",
        "order": 10,
        "is_published": True,
    },
]

LESSONS_DATA = [
    {
        "module_order": 1,
        "lessons": [
            {
                "title": "Основы SELECT",
                "content": "В этом уроке вы познакомитесь с основным оператором SQL - SELECT. Он используется для выборки данных из таблиц базы данных.",
                "theory": "SELECT - это основной оператор для запросов к базе данных. Синтаксис: SELECT column1, column2 FROM table_name;\n\nДля выборки всех столбцов используйте звёздочку: SELECT * FROM table_name;",
                "sql_solution": "SELECT * FROM users;",
                "expected_result": {
                    "columns": ["id", "name", "email"],
                    "rows": [
                        [1, "Иван", "ivan@example.com"],
                        [2, "Мария", "maria@example.com"]
                    ]
                },
                "order": 1,
                "estimated_duration": 15,
                "is_published": True,
            },
            {
                "title": "Выборка конкретных столбцов",
                "content": "Научитесь выбирать только нужные столбцы из таблицы, чтобы оптимизировать запросы.",
                "theory": "Вместо SELECT * можно указать конкретные столбцы через запятую.\n\nПример: SELECT name, email FROM users;\n\nЭто более эффективно, так как не передаются лишние данные.",
                "sql_solution": "SELECT name, email FROM users;",
                "expected_result": {
                    "columns": ["name", "email"],
                    "rows": [
                        ["Иван", "ivan@example.com"],
                        ["Мария", "maria@example.com"]
                    ]
                },
                "order": 2,
                "estimated_duration": 10,
                "is_published": True,
            },
            {
                "title": "Псевдонимы столбцов",
                "content": "Используйте псевдонимы (AS) для изменения имен столбцов в результате запроса.",
                "theory": "Оператор AS позволяет задать псевдоним для столбца или таблицы.\n\nСинтаксис: SELECT column_name AS alias_name FROM table_name;\n\nПсевдонимы делают результат более читаемым.",
                "sql_solution": "SELECT name AS имя, email AS почта FROM users;",
                "expected_result": {
                    "columns": ["имя", "почта"],
                    "rows": [
                        ["Иван", "ivan@example.com"],
                        ["Мария", "maria@example.com"]
                    ]
                },
                "order": 3,
                "estimated_duration": 12,
                "is_published": True,
            },
        ],
    },
    {
        "module_order": 2,
        "lessons": [
            {
                "title": "Создание таблиц",
                "content": "Узнайте, как создавать таблицы с помощью оператора CREATE TABLE.",
                "theory": "CREATE TABLE используется для создания новой таблицы.\n\nСинтаксис: CREATE TABLE table_name (column1 datatype, column2 datatype, ...);\n\nВажно правильно выбрать типы данных для столбцов.",
                "sql_solution": "CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(100), price DECIMAL(10, 2));",
                "expected_result": {
                    "message": "Таблица products успешно создана",
                    "columns": ["id", "name", "price"]
                },
                "order": 1,
                "estimated_duration": 20,
                "is_published": True,
            },
            {
                "title": "Изменение таблиц",
                "content": "Научитесь изменять структуру существующих таблиц с помощью ALTER TABLE.",
                "theory": "ALTER TABLE позволяет изменять структуру таблицы: добавлять, удалять, изменять столбцы.\n\nПример: ALTER TABLE table_name ADD column_name datatype;",
                "sql_solution": "ALTER TABLE products ADD description TEXT;",
                "expected_result": {
                    "message": "Столбец description добавлен в таблицу products",
                    "columns": ["id", "name", "price", "description"]
                },
                "order": 2,
                "estimated_duration": 15,
                "is_published": True,
            },
        ],
    },
    {
        "module_order": 3,
        "lessons": [
            {
                "title": "Условие WHERE",
                "content": "Фильтруйте данные с помощью условия WHERE для получения только нужных записей.",
                "theory": "WHERE используется для фильтрации записей по условию.\n\nСинтаксис: SELECT * FROM table_name WHERE condition;\n\nМожно использовать операторы: =, <>, <, >, <=, >=, LIKE, IN, BETWEEN.",
                "sql_solution": "SELECT * FROM products WHERE price > 100;",
                "expected_result": {
                    "columns": ["id", "name", "price"],
                    "rows": [
                        [1, "Ноутбук", 50000],
                        [2, "Смартфон", 30000]
                    ]
                },
                "order": 1,
                "estimated_duration": 18,
                "is_published": True,
            },
            {
                "title": "Сортировка ORDER BY",
                "content": "Упорядочивайте результаты запроса с помощью ORDER BY.",
                "theory": "ORDER BY сортирует результаты по указанным столбцам.\n\nСинтаксис: SELECT * FROM table_name ORDER BY column_name ASC/DESC;\n\nASC - по возрастанию (по умолчанию), DESC - по убыванию.",
                "sql_solution": "SELECT * FROM products ORDER BY price DESC;",
                "expected_result": {
                    "columns": ["id", "name", "price"],
                    "rows": [
                        [1, "Ноутбук", 50000],
                        [2, "Смартфон", 30000],
                        [3, "Мышь", 500]
                    ]
                },
                "order": 2,
                "estimated_duration": 15,
                "is_published": True,
            },
            {
                "title": "Ограничение LIMIT",
                "content": "Ограничивайте количество возвращаемых записей с помощью LIMIT.",
                "theory": "LIMIT используется для ограничения количества результатов.\n\nСинтаксис: SELECT * FROM table_name LIMIT number;\n\nМожно использовать OFFSET для пропуска записей.",
                "sql_solution": "SELECT * FROM products ORDER BY price DESC LIMIT 5;",
                "expected_result": {
                    "columns": ["id", "name", "price"],
                    "rows": [
                        [1, "Ноутбук", 50000],
                        [2, "Смартфон", 30000],
                        [3, "Планшет", 25000],
                        [4, "Монитор", 15000],
                        [5, "Клавиатура", 2000]
                    ]
                },
                "order": 3,
                "estimated_duration": 12,
                "is_published": True,
            },
        ],
    },
    {
        "module_order": 4,
        "lessons": [
            {
                "title": "Функция COUNT",
                "content": "Подсчитывайте количество записей с помощью агрегатной функции COUNT.",
                "theory": "COUNT возвращает количество строк.\n\nСинтаксис: SELECT COUNT(*) FROM table_name;\n\nCOUNT(column_name) не учитывает NULL значения.",
                "sql_solution": "SELECT COUNT(*) as total FROM products;",
                "expected_result": {
                    "columns": ["total"],
                    "rows": [[50]]
                },
                "order": 1,
                "estimated_duration": 15,
                "is_published": True,
            },
            {
                "title": "Функции SUM и AVG",
                "content": "Вычисляйте сумму и среднее значение с помощью SUM и AVG.",
                "theory": "SUM вычисляет сумму значений, AVG - среднее.\n\nСинтаксис: SELECT SUM(column_name), AVG(column_name) FROM table_name;\n\nРаботают только с числовыми типами.",
                "sql_solution": "SELECT SUM(price) as total_price, AVG(price) as avg_price FROM products;",
                "expected_result": {
                    "columns": ["total_price", "avg_price"],
                    "rows": [[500000, 10000]]
                },
                "order": 2,
                "estimated_duration": 15,
                "is_published": True,
            },
        ],
    },
    {
        "module_order": 5,
        "lessons": [
            {
                "title": "INNER JOIN",
                "content": "Объединяйте таблицы с помощью INNER JOIN для получения связанных данных.",
                "theory": "INNER JOIN возвращает записи, имеющие совпадения в обеих таблицах.\n\nСинтаксис: SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.foreign_id;",
                "sql_solution": "SELECT orders.id, users.name, orders.total FROM orders INNER JOIN users ON orders.user_id = users.id;",
                "expected_result": {
                    "columns": ["id", "name", "total"],
                    "rows": [
                        [1, "Иван", 5000],
                        [2, "Мария", 3000]
                    ]
                },
                "order": 1,
                "estimated_duration": 20,
                "is_published": True,
            },
            {
                "title": "LEFT JOIN",
                "content": "Используйте LEFT JOIN для получения всех записей из левой таблицы и совпадающих из правой.",
                "theory": "LEFT JOIN возвращает все записи из левой таблицы и совпадающие из правой.\n\nЕсли совпадений нет, для правой таблицы будут NULL значения.",
                "sql_solution": "SELECT users.name, orders.total FROM users LEFT JOIN orders ON users.id = orders.user_id;",
                "expected_result": {
                    "columns": ["name", "total"],
                    "rows": [
                        ["Иван", 5000],
                        ["Мария", None],
                        ["Петр", 3000]
                    ]
                },
                "order": 2,
                "estimated_duration": 20,
                "is_published": True,
            },
            {
                "title": "Множественные JOIN",
                "content": "Объединяйте более двух таблиц в одном запросе.",
                "theory": "Можно использовать несколько JOIN в одном запросе для связывания нескольких таблиц.\n\nПример: SELECT * FROM table1 JOIN table2 ON ... JOIN table3 ON ...",
                "sql_solution": "SELECT users.name, orders.id, products.name FROM users JOIN orders ON users.id = orders.user_id JOIN order_items ON orders.id = order_items.order_id JOIN products ON order_items.product_id = products.id;",
                "expected_result": {
                    "columns": ["name", "id", "name"],
                    "rows": [
                        ["Иван", 1, "Ноутбук"],
                        ["Иван", 1, "Мышь"]
                    ]
                },
                "order": 3,
                "estimated_duration": 25,
                "is_published": True,
            },
        ],
    },
    {
        "module_order": 6,
        "lessons": [
            {
                "title": "Подзапросы в WHERE",
                "content": "Используйте вложенные запросы для фильтрации данных.",
                "theory": "Подзапрос - это запрос внутри другого запроса.\n\nСинтаксис: SELECT * FROM table1 WHERE column IN (SELECT column FROM table2 WHERE condition);",
                "sql_solution": "SELECT * FROM products WHERE category_id IN (SELECT id FROM categories WHERE name = 'Электроника');",
                "expected_result": {
                    "columns": ["id", "name", "price", "category_id"],
                    "rows": [
                        [1, "Ноутбук", 50000, 1],
                        [2, "Смартфон", 30000, 1]
                    ]
                },
                "order": 1,
                "estimated_duration": 20,
                "is_published": True,
            },
            {
                "title": "Подзапросы в SELECT",
                "content": "Используйте подзапросы для вычисления дополнительных данных в результате.",
                "theory": "Подзапросы в SELECT позволяют добавить вычисляемые столбцы.\n\nПример: SELECT name, (SELECT COUNT(*) FROM orders WHERE user_id = users.id) as order_count FROM users;",
                "sql_solution": "SELECT name, (SELECT COUNT(*) FROM orders WHERE user_id = users.id) as order_count FROM users;",
                "expected_result": {
                    "columns": ["name", "order_count"],
                    "rows": [
                        ["Иван", 5],
                        ["Мария", 3]
                    ]
                },
                "order": 2,
                "estimated_duration": 20,
                "is_published": True,
            },
        ],
    },
    {
        "module_order": 7,
        "lessons": [
            {
                "title": "Создание индексов",
                "content": "Ускорьте выполнение запросов с помощью индексов.",
                "theory": "Индексы ускоряют поиск данных в таблице.\n\nСинтаксис: CREATE INDEX index_name ON table_name (column_name);\n\nИндексы занимают дополнительное место и замедляют INSERT/UPDATE.",
                "sql_solution": "CREATE INDEX idx_users_email ON users(email);",
                "expected_result": {
                    "message": "Индекс idx_users_email успешно создан"
                },
                "order": 1,
                "estimated_duration": 18,
                "is_published": True,
            },
            {
                "title": "EXPLAIN для анализа",
                "content": "Анализируйте производительность запросов с помощью EXPLAIN.",
                "theory": "EXPLAIN показывает план выполнения запроса.\n\nСинтаксис: EXPLAIN SELECT * FROM table_name WHERE condition;\n\nПомогает найти узкие места в производительности.",
                "sql_solution": "EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';",
                "expected_result": {
                    "plan": "Using index idx_users_email",
                    "type": "ref",
                    "rows": 1
                },
                "order": 2,
                "estimated_duration": 20,
                "is_published": True,
            },
            {
                "title": "Оптимизация запросов",
                "content": "Научитесь оптимизировать медленные SQL запросы.",
                "theory": "Основные способы оптимизации:\n- Использование индексов\n- Избегание SELECT *\n- Правильное использование JOIN\n- Оптимизация WHERE условий",
                "sql_solution": "SELECT id, name FROM users WHERE id IN (1, 2, 3) AND is_active = 1;",
                "expected_result": {
                    "columns": ["id", "name"],
                    "rows": [
                        [1, "Иван"],
                        [2, "Мария"]
                    ]
                },
                "order": 3,
                "estimated_duration": 25,
                "is_published": True,
            },
        ],
    },
    {
        "module_order": 8,
        "lessons": [
            {
                "title": "Основы транзакций",
                "content": "Управляйте транзакциями для обеспечения целостности данных.",
                "theory": "Транзакция - это последовательность операций, выполняемых как единое целое.\n\nКоманды: BEGIN, COMMIT, ROLLBACK\n\nСвойства ACID: Atomicity, Consistency, Isolation, Durability",
                "sql_solution": "BEGIN; UPDATE accounts SET balance = balance - 100 WHERE id = 1; UPDATE accounts SET balance = balance + 100 WHERE id = 2; COMMIT;",
                "expected_result": {
                    "message": "Транзакция успешно выполнена",
                    "affected_rows": 2
                },
                "order": 1,
                "estimated_duration": 22,
                "is_published": True,
            },
            {
                "title": "Откат транзакций",
                "content": "Используйте ROLLBACK для отмены изменений при ошибке.",
                "theory": "ROLLBACK отменяет все изменения, сделанные в текущей транзакции.\n\nПример: BEGIN; ... операции ...; ROLLBACK;\n\nПолезно при обработке ошибок.",
                "sql_solution": "BEGIN; UPDATE products SET stock = stock - 1 WHERE id = 1; ROLLBACK;",
                "expected_result": {
                    "message": "Транзакция отменена",
                    "changes_reverted": True
                },
                "order": 2,
                "estimated_duration": 18,
                "is_published": True,
            },
        ],
    },
    {
        "module_order": 9,
        "lessons": [
            {
                "title": "Создание функций",
                "content": "Создавайте пользовательские функции для многократного использования.",
                "theory": "Функции позволяют инкапсулировать логику и использовать её повторно.\n\nСинтаксис: CREATE FUNCTION function_name(parameters) RETURNS return_type BEGIN ... END;",
                "sql_solution": "CREATE FUNCTION calculate_discount(price DECIMAL(10,2)) RETURNS DECIMAL(10,2) BEGIN RETURN price * 0.9; END;",
                "expected_result": {
                    "message": "Функция calculate_discount успешно создана"
                },
                "order": 1,
                "estimated_duration": 25,
                "is_published": True,
            },
            {
                "title": "Триггеры",
                "content": "Автоматизируйте действия с помощью триггеров.",
                "theory": "Триггер - это код, который автоматически выполняется при определенных событиях.\n\nСобытия: INSERT, UPDATE, DELETE\n\nМоменты: BEFORE, AFTER",
                "sql_solution": "CREATE TRIGGER update_timestamp BEFORE UPDATE ON users FOR EACH ROW SET NEW.updated_at = NOW();",
                "expected_result": {
                    "message": "Триггер update_timestamp успешно создан"
                },
                "order": 2,
                "estimated_duration": 25,
                "is_published": True,
            },
        ],
    },
    {
        "module_order": 10,
        "lessons": [
            {
                "title": "Оконные функции",
                "content": "Выполняйте вычисления по группам строк с помощью оконных функций.",
                "theory": "Оконные функции выполняют вычисления для набора строк, связанных с текущей строкой.\n\nПример: ROW_NUMBER(), RANK(), SUM() OVER(), AVG() OVER()\n\nИспользуют OVER() для определения окна.",
                "sql_solution": "SELECT name, salary, RANK() OVER (ORDER BY salary DESC) as salary_rank FROM employees;",
                "expected_result": {
                    "columns": ["name", "salary", "salary_rank"],
                    "rows": [
                        ["Иван", 100000, 1],
                        ["Мария", 95000, 2],
                        ["Петр", 90000, 3]
                    ]
                },
                "order": 1,
                "estimated_duration": 30,
                "is_published": True,
            },
            {
                "title": "CTE (Common Table Expressions)",
                "content": "Упрощайте сложные запросы с помощью CTE.",
                "theory": "CTE создает временный именованный результат запроса.\n\nСинтаксис: WITH cte_name AS (SELECT ...) SELECT * FROM cte_name;\n\nДелает код более читаемым.",
                "sql_solution": "WITH top_products AS (SELECT * FROM products ORDER BY sales DESC LIMIT 10) SELECT * FROM top_products WHERE price > 1000;",
                "expected_result": {
                    "columns": ["id", "name", "price", "sales"],
                    "rows": [
                        [1, "Ноутбук", 50000, 500],
                        [2, "Смартфон", 30000, 800]
                    ]
                },
                "order": 2,
                "estimated_duration": 28,
                "is_published": True,
            },
            {
                "title": "Рекурсивные запросы",
                "content": "Работайте с иерархическими данными используя рекурсивные CTE.",
                "theory": "Рекурсивные CTE позволяют обрабатывать иерархические структуры.\n\nСинтаксис: WITH RECURSIVE cte_name AS (базовый запрос UNION ALL рекурсивный запрос) SELECT * FROM cte_name;",
                "sql_solution": "WITH RECURSIVE category_tree AS (SELECT id, name, parent_id FROM categories WHERE parent_id IS NULL UNION ALL SELECT c.id, c.name, c.parent_id FROM categories c JOIN category_tree ct ON c.parent_id = ct.id) SELECT * FROM category_tree;",
                "expected_result": {
                    "columns": ["id", "name", "parent_id"],
                    "rows": [
                        [1, "Электроника", None],
                        [2, "Компьютеры", 1],
                        [3, "Ноутбуки", 2]
                    ]
                },
                "order": 3,
                "estimated_duration": 35,
                "is_published": True,
            },
        ],
    },
]

ACHIEVEMENTS_DATA = [
    {
        "code": "first_lesson",
        "type": AchievementType.LESSON_COMPLETED,
        "title": "Первые шаги",
        "description": "Завершите свой первый урок по SQL",
        "icon": "🎓",
        "points": 10,
        "criteria": "Завершите любой урок",
    },
    {
        "code": "module_1_complete",
        "type": AchievementType.MODULE_COMPLETED,
        "title": "Основы освоены",
        "description": "Завершите модуль 'Введение в SQL'",
        "icon": "📚",
        "points": 50,
        "criteria": "Завершите все уроки модуля 1",
    },
    {
        "code": "ten_lessons",
        "type": AchievementType.LESSON_COMPLETED,
        "title": "Упорный ученик",
        "description": "Завершите 10 уроков",
        "icon": "💪",
        "points": 100,
        "criteria": "Завершите 10 уроков",
    },
    {
        "code": "streak_7",
        "type": AchievementType.STREAK,
        "title": "Недельная серия",
        "description": "Занимайтесь 7 дней подряд",
        "icon": "🔥",
        "points": 75,
        "criteria": "Завершите хотя бы один урок 7 дней подряд",
    },
    {
        "code": "streak_30",
        "type": AchievementType.STREAK,
        "title": "Месячная серия",
        "description": "Занимайтесь 30 дней подряд",
        "icon": "🏆",
        "points": 300,
        "criteria": "Завершите хотя бы один урок 30 дней подряд",
    },
    {
        "code": "challenge_master",
        "type": AchievementType.CHALLENGES_SOLVED,
        "title": "Мастер задач",
        "description": "Решите 50 практических задач",
        "icon": "🎯",
        "points": 200,
        "criteria": "Решите 50 практических задач",
    },
    {
        "code": "perfect_score",
        "type": AchievementType.MILESTONE,
        "title": "Идеальный результат",
        "description": "Получите 100% в любом уроке",
        "icon": "⭐",
        "points": 25,
        "criteria": "Получите максимальный балл в уроке",
    },
    {
        "code": "all_modules",
        "type": AchievementType.MODULE_COMPLETED,
        "title": "Полное владение",
        "description": "Завершите все модули курса",
        "icon": "👑",
        "points": 500,
        "criteria": "Завершите все 10 модулей",
    },
    {
        "code": "speed_runner",
        "type": AchievementType.MILESTONE,
        "title": "Спринтер",
        "description": "Завершите урок быстрее расчетного времени",
        "icon": "⚡",
        "points": 30,
        "criteria": "Завершите урок за время меньше estimated_duration",
    },
    {
        "code": "night_owl",
        "type": AchievementType.MILESTONE,
        "title": "Ночная сова",
        "description": "Завершите урок после полуночи",
        "icon": "🦉",
        "points": 15,
        "criteria": "Завершите урок между 00:00 и 06:00",
    },
]
