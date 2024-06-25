import argparse
import json

from typing import Optional, Generator
from requests import Session, Response, HTTPError

PAGE_SIZE: int = 1000

URL_BASE: str = 'https://{hostname}/sepm/api/v1'
URL_LOGON: str = f'{URL_BASE}/identity/authenticate'
URL_MACHINES: str = f'{URL_BASE}/machines'


def logon(session: Session, hostname: str, username: str, password: str, domain: Optional[str] = None) -> str:
    logon_url: str = URL_LOGON.format(hostname=hostname)
    post_data: dict = {
        'username': username,
        'password': password,
    }
    if domain:
        post_data['domain'] = domain
    resp_auth: Response = session.post(url=logon_url, json=post_data)
    resp_auth.raise_for_status()
    token: str = resp_auth.json().get('token')
    return token


def list_machines(session: Session, hostname: str, machine: Optional[str] = None) -> Generator[dict, None, None]:
    params: dict = {
        'offset': 0,
        'limit': PAGE_SIZE,
    }
    if machine:
        params['computerName'] = machine
    while True:
        resp_accounts: Response = session.get(url=URL_MACHINES.format(hostname=hostname), params=params)
        resp_accounts.raise_for_status()
        data: dict = resp_accounts.json()
        machines: list = data.get('content')
        yield from machines
        if len(machines) < PAGE_SIZE:
            break
        params['offset'] += PAGE_SIZE


def main(
        hostname: str,
        username: str,
        password: str,
        user_domain: Optional[str] = None,
        machine: Optional[str] = None,
        proxies: Optional[dict] = None,
) -> Generator[dict, None, None]:
    session = Session()

    headers: dict = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    session.headers = headers
    session.proxies = proxies

    token: None | str = None
    try:
        token = logon(
            session=session,
            hostname=hostname,
            username=username,
            password=password,
            domain=user_domain,
        )
        session.headers.update({'Authorization': f'Bearer {token}'})
    except HTTPError as http_err:
        print(f'HTTPError during logon: {http_err}')
        raise
    except Exception as exc_auth:
        print(f'Unexpected error during logon: {exc_auth}')
        raise

    try:
        yield from list_machines(session=session, hostname=hostname, machine=machine)
    except HTTPError as http_err:
        print(f'HTTPError during accounts retrieval: {http_err}')
        raise
    except Exception as exc_auth:
        print(f'Unexpected error during accounts retrieval: {exc_auth}')
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--hostname',
        default=None,
        type=str,
        required=True,
        help="The host name of your SEP server (my-sep-host.my-domain.com)",
    )
    parser.add_argument(
        '--username',
        default=None,
        type=str,
        required=True,
        help='The user name for your SEP admin user',
    )
    parser.add_argument(
        '--password',
        default=None,
        type=str,
        required=True,
        help='The password for your SEP admin user',
    )
    parser.add_argument(
        '--domain',
        type=str,
        required=False,
        help='The domain for your SEP admin user',
    )
    parser.add_argument(
        '--machine',
        type=str,
        required=False,
        help='machine name to search for',
    )
    parser.add_argument(
        '--proxies',
        type=str,
        required=False,
        help="JSON structure specifying 'http' and 'https' proxy URLs",
    )

    args = parser.parse_args()

    proxies: Optional[dict] = None
    if proxies:
        try:
            proxies: dict = json.loads(args.proxies)
        except Exception as exc_json:
            print(f'WARNING: failure parsing proxies: {exc_json}: proxies provided: {proxies}')

    for machine in main(
        hostname=args.hostname,
        username=args.username,
        password=args.password,
        user_domain=args.domain,
        machine=args.machine,
        proxies=proxies,
    ):
        print(json.dumps(machine, indent=4))
    else:
        print('No results found')
