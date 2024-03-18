import requests
import json
import random
from bs4 import BeautifulSoup

# URL에서 HTML 가져오기
url = 'https://raw.githubusercontent.com/koko8829/chm_TEST/main/2663%5CENG%5CComponents_Component_Calendar.html'
response = requests.get(url)
html = response.text

soup = BeautifulSoup(html, 'html.parser')

# (공통 함수) Description, Remark, Contents Sizing 가져오기 
def get_desc_text(soup, title):
    desc_title_td = soup.find('td', class_='sub_title', string=title)
    if not desc_title_td:
        raise ValueError(f"{title}을 포함한 요소를 찾을 수 없습니다.")
        
    desc_content_td = desc_title_td.find_next('td', class_='list')
    if desc_content_td and desc_content_td.pre:
        desc_text = desc_content_td.pre.get_text().strip()
    else:
        print(f"{title} 본문 텍스트를 포함한 요소를 찾을 수 없습니다.")
    
    return desc_text

# (공통 함수) Contents Sizing 가져오기 
def get_table_content(soup, title):
    content_title_td = soup.find('td', class_='sub_title', string=title)
    if not content_title_td:
        raise ValueError(f"{title}을 포함한 요소를 찾을 수 없습니다.")

    content_tds = content_title_td.find_all_next('td', class_='list')

    for content_td in content_tds:
        # (확인중) class='list'로 목록을 만들었기 때문에 sub_title 항목은 제외됨. 때문에 for 문에서 이를 처리하지 못함. 이런.
        if (content_td.find_previous('td', class_='sub_title').get_text() != title):
            break

        if content_td and content_td.find_next().name=='pre':
            add_element("u_09_"+str(random.random()), "pre", content_td.pre.get_text().strip())
        elif content_td and content_td.find_next().name=='table':
            
            # 속성 제거
            for tag in content_td.find_all():
                attrs_to_remove = [attr for attr in tag.attrs if attr != 'colspan']
                for attr in attrs_to_remove:
                    del tag[attr]

            table_tag = content_td.find('table')  

            # colgroup 태그 삭제
            for colgroup in table_tag.find_all('colgroup'):
                colgroup.decompose()

            # tbody 태그 추가
            tbody_tag = soup.new_tag('tbody')
            caption_tag = soup.new_tag('caption')
            for tr_tag in table_tag.find_all('tr'):
                tr_tag.wrap(tbody_tag)
            table_tag.insert(0, caption_tag)

            # 태그 사이의 공백과 줄바꿈 제거
            for pre_tag in table_tag.find_all('pre'):
                pre_tag.string = pre_tag.text.strip()
            add_element("u_10_"+str(random.random()), "table", str(table_tag), get_table_option("120,?"))            
        else:
            print(f"{title} 본문 텍스트, 표를 포함한 요소를 찾을 수 없습니다.")


# (공통 함수) Structure 이미지 파일명 가져오기
def get_structure_img(soup):
    structure_title_td = soup.find('td', class_='sub_title', string='Structure')
    if not structure_title_td:
        raise ValueError("Structure를 포함한 요소를 찾을 수 없습니다.")
        
    structure_content_td = structure_title_td.find_next('td', class_='list')
    if structure_content_td and structure_content_td.pre:
        structure_img = structure_content_td.pre.find('img')['src'].split('/')[-1]
    else:
        print("Structure 이미지를 포함한 요소를 찾을 수 없습니다.")
    
    return f"<img src='https://github.com/koko8829/chm_TEST/blob/main/2663%5C{structure_img}?raw=true'/>"

# (공통 함수) Supported Environments 표 생성
def get_support_table(soup):
    support_icon = []
    env_keywords = ["Windows", "macOS", "Edge", "Chrome", "Safari", "Firefox", "Opera", "Android", "iOS/iPadOS", "Android", "iOS/iPadOS"]

    support_title_td = soup.find('td', class_='sub_title', string='Supported Environments')    
    if not support_title_td:
        raise ValueError("Supported Environments 타이틀을 찾을 수 없습니다.")
    
    for env_keyword in env_keywords:
        if support_title_td:
            keyword_td = support_title_td.find_next('td', string=env_keyword)
            if keyword_td:
                img_src = keyword_td.find_previous_sibling('td').find('img')['src']
                if img_src == "../../support01.gif":
                    support_icon.append("■");
                else:
                    support_icon.append("▢");
                
            else:
                print(f"{env_keyword} 환경이 지원되지 않습니다.")


    return "<table class='table column_count_7'><caption></caption><thead><tr><th colspan='2'><div>Desktop NRE</div></th><th colspan='5'><div>Desktop WRE</div></th></tr></thead><tbody><tr><td><div>"+support_icon[0]+" Windows</div></td><td><div>"+support_icon[1]+" macOS</div></td><td><div>"+support_icon[2]+" Edge</div></td><td><div>"+support_icon[3]+" Chrome</div></td><td><div>"+support_icon[4]+" Safari</div></td><td><div>"+support_icon[5]+" Firefox</div></td><td><div>"+support_icon[6]+" Opera</div></td></tr><tr><th colspan='2'><div>Mobile NRE</div></th><th colspan='5'><div>Mobile WRE</div></th></tr><tr><td><div>"+support_icon[7]+" Android</div></td><td><div>"+support_icon[8]+" iOS/iPadOS</div></td><td><div>"+support_icon[9]+" Android</div></td><td><div>"+support_icon[10]+" iOS/iPadOS</div></td><td><div></div></td><td><div></div></td><td><div></div></td></tr></tbody></table>"

# (공통 함수) Supported Environments 표 config
def get_table_option(setting="110,110,110,110,110,110,110"):
    return {
        "table_layout": "user",
        "table_layout_setting": setting
    }


# JSON 파일 생성
elements = []

def add_element(id, type, content, option=None):
    element = {
        "id": id,
        "type": type,
        "content": content
    }
    if option is not None:
        element["option"] = option
    elements.append(element)    

add_element("u_01", "heading1", "개요")
add_element("u_02", "pre", get_desc_text(soup, "Description"))
add_element("u_03", "heading2", "지원 환경")
add_element("u_04", "table", get_support_table(soup), get_table_option())
add_element("u_05", "pre", get_desc_text(soup, "Remark"))
add_element("u_06", "heading2", "컴포넌트 구조")
add_element("u_07", "normal", get_structure_img(soup))
add_element("u_08", "heading2", "컴포넌트, 내부 컨텐츠 크기")
get_table_content(soup, "Contents Sizing")

data = {
    "elements": elements
}

# JSON 파일로 저장
with open('result.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=2)    

print("JSON 파일이 생성되었습니다.")    
