import requests
import base64
import re
import xxhash
import plistlib
import struct

from pprint import pprint
from Crypto.Cipher import ARC4
from math import floor
from plistlib import FMT_BINARY, _BinaryPlistParser, _undefined


def crypto_rc4(raw_data: bytes, sec_key: str):
    cipher = ARC4.new(sec_key.encode())
    rc4_bytes = cipher.encrypt(raw_data)
    return rc4_bytes


def judge_title(a):
    if "onclick" not in a and a != "search_subject" and a != "" and "doubanio" not in a:
        return True
    return False


def main():
    url = f"https://search.douban.com/book/subject_search?search_text=虫师&cat=1001"
    res = requests.get(url)
    data = re.search(r'window.__DATA__ = "(.+?)"', res.text, flags=re.DOTALL).group(1)

    i = 16
    a = base64.b64decode(data)
    s = floor((len(a) - 2 * i) / 3)
    u = a[s : s + i]
    raw_bytes = a[0:s] + a[s + i :]
    sec_key = xxhash.xxh64_hexdigest(u, 41405)
    # print(sec_key)
    # print(raw_text)
    
    rc4_bytes = crypto_rc4(raw_bytes, sec_key)
    # print(rc4_bytes)
    pb_results = plistlib.loads(rc4_bytes, fmt=FMT_BINARY)
    print("最终结果为：")
    pprint(pb_results)
    results = list(
        filter(
            lambda d: isinstance(d, dict)
            and len(d["k"]) > 10
            and len(d.keys()) == 2,
            pb_results,
        )
    )

    for d in results:
        for a in d["k"]:
            if bool(a) and isinstance(a, int) or isinstance(a, str):
                a = str(a)
                if "img" in a:
                    print(f"封面：{a}")
                elif "book.douban.com" in a:
                    print(f"豆瓣链接：{a}")
                elif a.isdigit():
                    print(f"豆瓣id：{a}")
                elif " / " in a:
                    print(f"出版信息：{a}")
                elif judge_title(a):
                    print(f"书名：{a}")
        print("cxs".center(50, "-"))

        
if __name__ == "__main__":
    main()
