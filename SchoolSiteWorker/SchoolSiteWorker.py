from typing import Union

from requests import Session
from bs4 import BeautifulSoup
from faker import Faker


class SchoolSiteWorker(Session):
    _login: str
    _password: str
    _school_url: str
    _access_token: Union[str, None] = None
    _ekis_code: str = None
    _authorized: bool = False

    def __init__(self, school_url: str, login: str, password: str, ekis_code: str):
        super(SchoolSiteWorker, self).__init__()
        Faker.seed(0)
        self.faker = Faker()
        self._login = login
        self._school_url = school_url
        self._password = password
        self.headers.update(
            {
                'User-Agent': self.faker.chrome(),
                'Accept': '*/*',
                'Accept-encoding': 'gzip, deflate, br, zstd'
            }
        )
        self._ekis_code = ekis_code

    def authorized(self):
        return self._authorized

    def authorize(self):
        self.get(
            url=self._school_url,
        )
        self.get(
            url=self._school_url + '/logout',
            headers={
                'Authorization': 'Bearer'
            }
        )

        request = self.get(
            url=self._school_url + '/v1/login',
            allow_redirects=True
        )
        soup = BeautifulSoup(request.text, 'html.parser')
        self.post(
            url='https://center.educom.ru/oauth/auth',
            data={
                'sr': soup.find('input', {'name': 'sr'}).get('value'),
                'csrf_name': soup.find('input', {'name': 'csrf_name'}).get('value'),
                'csrf_value': soup.find('input', {'name': 'csrf_value'}).get('value'),
                'username': self._login,
                'password': self._password
            },
            headers={
                'Content-type': 'application/x-www-form-urlencoded',
            },
            allow_redirects=True
        )
        self._access_token = self.cookies.get('AccessToken')
        self.get(
            url='https://api-app.mskobr.ru/api/v3/organization/' + self._ekis_code
        )
        self.get(
            url=self._school_url + '/v1/api/user/auth/me',
            headers={
                'Authorization': 'Bearer ' + self._access_token
            }
        )
        self._authorized = self._access_token is not None
        return self._authorized

    def edit_page_content(self, page_path, page_content):
        request = self.post(
            url=self._school_url + '/v1/api/page/id',
            headers={
                'Content-type': 'application/json'
            },
            json={
                'path': page_path,
            },
        )
        page_id = request.json()['data']['id']
        resp = self.get(
            url=self._school_url + '/v1/api/page/content/' + str(page_id),
        )

        resp = self.post(
            url=self._school_url + '/v1/api/page/content/' + str(page_id),
            headers={
                'Content-type': 'application/json',
                'Authorization': 'Bearer ' + self._access_token
            },
            json={
                'old_data': [],
                'data': [
                    {
                        'block_type_id': None,
                        'data': [
                            {
                                'type': 'text',
                                'content': {
                                    'errors': False,
                                    'key': resp.json()['blocks'][0]['data'][0]['content']['key'],
                                    'data': page_content
                                }
                            }
                        ]
                    }
                ]
            }
        )
