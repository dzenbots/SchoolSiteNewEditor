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
        worker.edit_page_content(
            page_path=env.str('PAGE_PATH'),
            page_content=new_content
        )
