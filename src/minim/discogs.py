"""
Discogs
=======
.. moduleauthor:: Benjamin Ye <GitHub: bbye98>
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process

try:
    from flask import Flask, request
    FOUND_FLASK = True
except ModuleNotFoundError:
    FOUND_FLASK = False

from . import (
    json, logging, os, re, requests, secrets, time, urllib, warnings, webbrowser,
    FOUND_PLAYWRIGHT, REPOSITORY_URL, VERSION, DIR_HOME, DIR_TEMP,
    Any, Union, config
)

if FOUND_PLAYWRIGHT:
    from . import sync_playwright

__all__ = ["API"]

class _DiscogsRedirectHandler(BaseHTTPRequestHandler):
    
    """
    HTTP request handler for the Discogs OAuth 1.0a flow.
    """

    def do_GET(self):
        
        """
        Handles an incoming GET request and parses the query string.
        """

        self.server.response = dict(
            urllib.parse.parse_qsl(
                urllib.parse.urlparse(f"{self.path}").query
            )
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        status = "denied" if "denied" in self.server.response else "granted" 
        self.wfile.write(f"Access {status}. You may close this page now.".encode())

class API:

    _FLOWS = {"discogs", "oauth"}
    _NAME = f"{__module__}.{__qualname__}"

    API_URL = "https://api.discogs.com"
    ACCESS_TOKEN_URL = f"{API_URL}/oauth/access_token"
    AUTH_URL = "https://www.discogs.com/oauth/authorize"
    REQUEST_TOKEN_URL = f"{API_URL}/oauth/request_token"

    def __init__(
            self, *, consumer_key: str = None, consumer_secret: str = None,
            flow: str = None, browser: bool = False, web_framework: str = None, 
            port: Union[int, str] = 8888, redirect_uri: str = None, 
            access_token: str = None, access_token_secret: str = None, 
            overwrite: bool = False, save: bool = True) -> None:
        
        self.session = requests.Session()
        self.session.headers["User-Agent"] = f"Minim/{VERSION} +{REPOSITORY_URL}"

        if (access_token is None and config.has_section(self._NAME) 
                and not overwrite):
            flow = config.get(self._NAME, "flow")
            access_token = config.get(self._NAME, "access_token")
            access_token_secret = config.get(self._NAME, "access_token_secret")
            consumer_key = config.get(self._NAME, "consumer_key")
            consumer_secret = config.get(self._NAME, "consumer_secret")
        elif flow is None and access_token is not None:
            flow = "discogs" if access_token_secret is None else "oauth"

        self.set_flow(
            flow, consumer_key=consumer_key, consumer_secret=consumer_secret,
            browser=browser, web_framework=web_framework, port=port, 
            redirect_uri=redirect_uri, save=save
        )
        self.set_access_token(access_token, access_token_secret)

    def _get_json(self, url: str, **kwargs) -> dict:

        return self._request("get", url, **kwargs).json()

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:

        if self._flow == "oauth" \
                and "Authorization" not in kwargs.get("headers", {}):
            oauth = self._oauth | {
                "oauth_nonce": secrets.token_hex(32), 
                "oauth_timestamp": f"{time.time():.0f}"
            }
            if "oauth" in kwargs:
                oauth |= kwargs.pop("oauth")

            if "headers" not in kwargs:
                kwargs["headers"] = {}
            kwargs["headers"]["Authorization"] = "OAuth " + ", ".join(
                f'{k}="{v}"' for k, v in oauth.items()
            )

        r = self.session.request(method, url, **kwargs)
        if r.status_code not in range(200, 299):
            raise RuntimeError(f"{r.status_code}: {r.json()['message']}")
        return r

    def set_access_token(
            self, access_token: str = None, access_token_secret: str = None
        ) -> None:

        if self._flow == "oauth":
            self._oauth = {
                "oauth_consumer_key": self._consumer_key,
                "oauth_signature_method": "PLAINTEXT"
            }

            if access_token is None:
                oauth = {"oauth_signature": f"{self._consumer_secret}&"}
                if self._redirect_uri is not None:
                    oauth["oauth_callback"] = self._redirect_uri
                r = self._request(
                    "get",
                    self.REQUEST_TOKEN_URL, 
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    oauth=oauth
                )
                auth_url = f"{self.AUTH_URL}?{r.text}"
                oauth = dict(urllib.parse.parse_qsl(r.text))

                if self._web_framework == "playwright":
                    har_file = DIR_TEMP / "minim_discogs.har"
                    
                    with sync_playwright() as playwright:
                        browser = playwright.firefox.launch(headless=False)
                        context = browser.new_context(record_har_path=har_file)
                        page = context.new_page()
                        page.goto(auth_url, timeout=0)
                        page.wait_for_url(f"{self._redirect_uri}*", 
                                            wait_until="commit")
                        context.close()
                        browser.close()

                    with open(har_file, "r") as f:
                        oauth |= dict(
                            urllib.parse.parse_qsl(
                                urllib.parse.urlparse(
                                    re.search(f'{self._redirect_uri}\?(.*?)"', 
                                                f.read()).group(0)
                                ).query
                            )
                        )
                    har_file.unlink()

                else:
                    if self._browser:
                        webbrowser.open(auth_url)
                    else:
                        print("To grant Minim access to Discogs data "
                              "and features, open the following link "
                              f"in your web browser:\n\n{auth_url}\n")

                    if self._web_framework == "http.server":
                        httpd = HTTPServer(("", self._port), 
                                            _DiscogsRedirectHandler)
                        httpd.handle_request()
                        oauth |= httpd.response

                    elif self._web_framework == "flask":
                        app = Flask(__name__)
                        json_file = DIR_TEMP / "minim_discogs.json"

                        @app.route("/callback", methods=["GET"])
                        def _callback() -> str:
                            if "error" in request.args:
                                return ("Access denied. You may close "
                                        "this page now.")
                            with open(json_file, "w") as f:
                                json.dump(request.args, f)
                            return ("Access granted. You may close "
                                    "this page now.")

                        server = Process(target=app.run, 
                                         args=("0.0.0.0", self._port))
                        server.start()
                        while not json_file.is_file():
                            time.sleep(0.1)
                        server.terminate()

                        with open(json_file, "rb") as f:
                            oauth |= json.load(f)
                        json_file.unlink()

                    else:
                        oauth["oauth_verifier"] = input(
                            "After authorizing Minim to access Discogs "
                            "on your behalf, enter the displayed code "
                            "below.\n\nCode: "
                        )

                if "denied" in oauth:
                    raise RuntimeError("Authorization failed.")

                oauth["oauth_signature"] = (f"{self._consumer_secret}"
                                            f"&{oauth['oauth_token_secret']}")
                r = self._request(
                    "post",
                    self.ACCESS_TOKEN_URL,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    oauth=oauth
                )
                access_token, access_token_secret = \
                    dict(urllib.parse.parse_qsl(r.text)).values()

                if self._save:
                    config[self._NAME] = {
                        "flow": self._flow,
                        "access_token": access_token,
                        "access_token_secret": access_token_secret,
                        "consumer_key": self._consumer_key,
                        "consumer_secret": self._consumer_secret
                    }
                    with open(DIR_HOME / "minim.cfg", "w") as f:
                        config.write(f)
        
            self._oauth |= {
                "oauth_token": access_token,
                "oauth_signature": self._consumer_secret
                                   + f"&{access_token_secret}"
            }

        elif self._flow == "discogs":
            if access_token is None:
                self.session.headers["Authorization"] = (
                    f"Discogs key={self._consumer_key}, "
                    f"secret={self._consumer_secret}"
                )
            else:
                self.session.headers["Authorization"] = \
                    f"Discogs token={access_token}"
                
        if (self._flow == "oauth" 
                or self._flow == "discogs" 
                   and "token" in self.session.headers["Authorization"]):
            identity = self.get_identity()
            self._username = identity["username"]

    def set_flow(
            self, flow: str, *, consumer_key: str = None,
            consumer_secret: str = None, browser: bool = False,
            web_framework: str = None, port: Union[int, str] = 8888,
            redirect_uri: str = None, save: bool = True) -> None:

        self._consumer_key = \
            consumer_key or os.environ.get("DISCOGS_CONSUMER_KEY")
        self._consumer_secret = \
            consumer_secret or os.environ.get("DISCOGS_CONSUMER_SECRET")

        if flow is None:
            if (self._consumer_key is not None 
                    and self._consumer_secret is not None):
                flow = "discogs"
        elif flow not in self._FLOWS:
            emsg = (f"Invalid authorization flow ({flow=}). "
                    f"Valid values: {', '.join(self._FLOWS)}.")
            raise ValueError(emsg)
        self._flow = flow
        self._save = save

        if flow == "oauth":
            self._browser = browser
            if redirect_uri:
                self._redirect_uri = redirect_uri
                if "localhost" in redirect_uri:
                    self._port = re.search("localhost:(\d+)", 
                                            redirect_uri).group(1)
                elif web_framework:
                    wmsg = ("The redirect URI is not on localhost, "
                            "so automatic authorization code "
                            "retrieval is not available.")
                    logging.warning(wmsg)
                    web_framework = None
            elif port:
                self._port = port
                self._redirect_uri = f"http://localhost:{port}/callback"
            else:
                self._port = self._redirect_uri = None

            self._web_framework = (
                web_framework 
                if web_framework is None 
                   or web_framework == "http.server"
                   or globals()[f"FOUND_{web_framework.upper()}"]
                else None
            )
            if self._web_framework is None and web_framework:
                wmsg = (f"The {web_framework.capitalize()} web "
                        "framework was not found, so automatic "
                        "authorization code retrieval is not "
                        "available.")
                warnings.warn(wmsg)

    def get_identity(self) -> dict[str, Any]:
        return self._get_json(f"{self.API_URL}/oauth/identity")