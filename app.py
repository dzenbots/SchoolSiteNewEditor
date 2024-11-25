from environs import Env

from SchoolSiteWorker import SchoolSiteWorker

if __name__ == '__main__':

    env = Env()

    env.read_env()

    with open(env.str('NEW_PAGE_CONTENT_FILE'), 'r') as f:
        new_content = f.read()
    worker = SchoolSiteWorker(
        school_url=env.str('SCHOOL_SITE_URL'),
        login=env.str('LOGIN'),
        password=env.str('PASSWORD'),
        ekis_code=env.str('EKIS_CODE')
    )
    worker.authorize()
    if worker.authorized():
        print('Аавторизация успешна. Пробую заменить контент страницы...')
        if worker.edit_page_content(
            page_path=env.str('PAGE_PATH'),
            page_content=new_content
        ):
            print(f'Обновление контента страницы прошло успешно. Результат можете посмотреть по ссылке: {env.str('SCHOOL_SITE_URL')}{env.str('PAGE_PATH')}')
        else:
            print('Что-то пошло не так. Попробуйте позже')
    else:
        print('Аавторизация не пройдена. Проверьте правильность указания логина и пароля от ЛК Маяк')
