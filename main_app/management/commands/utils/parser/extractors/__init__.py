from urllib.parse import urlparse

from .astov import extract_price as astov_extract
from .easysteam import extract_price as easysteam_extract
from .gk_kovcheg import extract_price as gk_kovcheg_extract
from .kamin import extract_price as kamin_extract
from .nkamin import extract_price as nkamin_extract
from .prometall import extract_price as prometall_extract
from .saunaru import extract_price as saunaru_extract
from .technolit import extract_price as technolit_extract


EXTRACTORS = {
    "astov.ru": astov_extract,
    "easysteam.ru": easysteam_extract,
    "gk-kovcheg.ru": gk_kovcheg_extract,
    "kamin.ru": kamin_extract,
    "nkamin.ru": nkamin_extract,
    "prometall.ru": prometall_extract,
    "saunaru.com": saunaru_extract,
    "technolit.ru": technolit_extract,
}


def get_extractor(url: str):
    domain = urlparse(url).netloc.replace("www.", "")
    return EXTRACTORS.get(domain)