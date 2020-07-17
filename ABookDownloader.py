import requests

file = open("Sol.html", "r", encoding="utf-8")

keyword = "resourses"
block_keyword = "style"
url_base = "http://abook.hep.com.cn/ICourseFiles/"
cnt = 1

def downloader(url, file_type, name):
    r = requests.get(url)
    with open(str(cnt) + str(file_type),'wb') as f:
        f.write(r.content)



for lines in file:
    if str(lines).find(keyword) != -1 and str(lines).find(block_keyword) == -1:
        index_start = str(lines).find("value=\"")
        index_end = str(lines).find(".")
        url_detail = str(lines)[index_start + 7 : index_end + 4]
        url = url_base + url_detail
        ext_end = str(lines).find("\"", index_end)
        ext = lines[index_end : ext_end]
        print(url)
        print(ext)
        # downloader(url, ext, cnt)
        cnt += 1
file.close()

