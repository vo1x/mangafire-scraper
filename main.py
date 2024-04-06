import requests,re
from bs4 import BeautifulSoup

def get_chapter_pages(url):
    tag = re.search(r'read/.*?\.(.*?)/',url).group(1) if 'read' in url and 'chapter' in url else None
    ch  = url.rsplit('/',1)[1].split('-')[1] if 'chapter' in url else None
    if not tag and not ch:
        return 'Invalid url'
    data_url = f'https://mangafire.to/ajax/read/{tag}/chapter/en'
    resp = requests.get(data_url,headers={'user-agent':'Android'})
    data = resp.text
    id = re.search(f'data-number=.*?{ch}.*?data-id=.*?(\d+)',data)
    if 'nonetype' in str(type(id)).lower():
        return "ID not found"
    resp = requests.get(f'https://mangafire.to/ajax/read/chapter/{id.group(1)}')
    img_data = resp.json()
    images = img_data.get('result')
    ch_pages = []
    for i,image in enumerate(images.get('images'),start=1):
        ch_pages.append({'pg_num':i,'pg_url':image[0]})
    return ch_pages



def get_chapters(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text,'html.parser')
    
    ch_div = soup.find('div',class_='list-body')
    ch_list = ch_div.find('ul')
    chapters = []
    if ch_list:
        for ch in ch_list.find_all('li'):
            a=ch.find('a')
            ch_title = a.find('span')
            ch_published = ch_title.find_next_sibling('span').text.strip()
            ch_data = {
                "url":a.get('href'),
                "title": ch_title.text.strip(),
                "published_on": ch_published,
                "ch_num":ch.get('data-number'),

            }
            chapters.append(ch_data)
    return chapters

def get_mv_daily():
    url = 'https://mangafire.to/home'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    mv_section = soup.find('section', {'id': 'most-viewed'})
    results = {}

    if mv_section:
        periods = ["day", "week", "month"]
        
        for period in periods:
            data_tab = mv_section.find('div', {'class': 'tab-content', 'data-name': period})
            period_results = []
            
            if data_tab:
                swiper_slides = data_tab.find_all('div', class_='swiper-slide unit')
                
                for slide in swiper_slides:
                    result = {}
                    a_tag = slide.find('a')
                    
                    if a_tag:
                        link = a_tag.get('href')
                        poster_url = a_tag.find('img').get('src')
                        rank = a_tag.find('b').text.strip()
                        name = a_tag.find('span').text.strip()
                        
                        result = {'name': name, 'rank': rank, 'identifier': link.split('/')[2], 'poster_url': poster_url}
                        period_results.append(result)
            
            results[period]=period_results

    return results

def get_trending():
    url='https://mangafire.to/home'
    res = requests.get(url)
    
    if res.status_code != 200:
        print("Failed to fetch the URL:", url)
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    
    swiper_slides = soup.find_all('div', class_='swiper-slide')
    
    results = []
    
    count = 0
    
    for slide in swiper_slides:
        if count >= 9:
            break
        result = {}
        info_div = slide.find('div', class_='info')
        
        if info_div:
            name_a = info_div.find('a', class_='unit')
            if name_a:
                name = name_a.text.strip()
                link = name_a.get('href')
                result = {
                        'name': name, 'identifier':link.split('/')[2]
                }
                count += 1
        
        poster_div = slide.find('a',class_='poster')
        poster = poster_div.find('img')
        poster_url = poster.get('src')

        below_div = slide.find('div',class_='below')
        desc = below_div.find('span')
        desc_text = desc.text.strip()

        chapter_latest = below_div.find('p')
        chapter = chapter_latest.text.strip().split('-')[0]
        volume = chapter_latest.text.strip().split('-')[1]
        latest_chapter = {}
        latest_chapter.update({'chapter':chapter.split(' ')[1],'volume':volume.strip().split(' ')[1]})
        genre_div = below_div.find('div')
        genre_a_tags = genre_div.find_all('a')
        genres = []
        for tag in genre_a_tags:
            genres.append(tag.text.strip().lower())
        result.update({'poster_url':poster_url, 'genres':genres, 'latest_chapter':latest_chapter, 'description':desc_text})
        results.append(result)


    return results

def get_search_results(query):
    # only extracts the results from Page 1
    url = f'https://mangafire.to/filter?keyword={query}'
    res = requests.get(url)
    soup = BeautifulSoup(res.text,'html.parser')

    unit_divs = soup.find_all('div',class_='unit')
    results = []
    if unit_divs:
        for div in unit_divs:
            poster = div.find('img')
            poster_url = poster.get('src')
            link = div.find('a', class_='poster')
            link_l = link.get('href')
            type = div.find('span',class_='type').text.strip()
            info_div = div.find('div',class_='info')
            name = info_div.find('a').text.strip()
            result = {'name':name,'type':type,'poster_url':poster_url,'identifier':link_l.split('/')[2]}
            results.append(result)
    return results


def get_recently_updated():
    url = "https://mangafire.to/home"
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        recently_updated_sections = soup.find_all('section')
        needed_section = None

        for section in recently_updated_sections:
            head_div = section.find('div', class_='head')
            if head_div:
                span = head_div.find('span')
                if span and "Updated" in span.text.strip():
                    needed_section = section
                    break

        if needed_section:
            unit_divs = needed_section.find_all('div',class_='unit')
            results = []
            if unit_divs:
                    for div in unit_divs:
                        poster = div.find('img')
                        poster_url = poster.get('src')
                        link = div.find('a', class_='poster')
                        link_l = link.get('href')
                        type = div.find('span',class_='type').text.strip()
                        info_div = div.find('div',class_='info')
                        name = info_div.find('a').text.strip()
                        result = {'name':name,'type':type,'poster_url':poster_url,'identifier':link_l.split('/')[2]}
                        results.append(result)
            return results
        

def get_new_releases():
    url = 'https://mangafire.to/home'
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        recently_updated_sections = soup.find_all('section')
        needed_section = None

        for section in recently_updated_sections:
            head_div = section.find('div', class_='head')
            if head_div:
                h2 = head_div.find('h2')
                if h2 and "New Release" in h2.text.strip():
                    needed_section = section
                    break

        if needed_section:
            slide_divs = needed_section.find_all('div',class_='swiper-slide')
            results = []
            if slide_divs:
                    for div in slide_divs:
                        poster = div.find('img')
                        poster_url = poster.get('src')
                        link = div.find('a')
                        link_l = link.get('href')
                        named = div.find('span')
                        if named:
                            name = named.text.strip()
                        result = {'name':name,'poster_url':poster_url,'identifier':link_l.split('/')[2]}
                        results.append(result)
            return results


def get_metadata(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text,'html.parser')

    details_div = soup.find('div', class_='info')
    name=details_div.find('h1').text.strip()
    alt_names = [alt.strip() for alt in details_div.find('h6').text.strip().split('; ')]
    status = details_div.find('p').text.strip().lower()
    type_div = details_div.find('div',class_='min-info')
    type = type_div.find('a').text.strip().lower() if type_div else ''
    
    description = soup.find('div',id="synopsis").text.strip()

    metadata = {}
    for tag_name in ['Author:', 'Published:', 'Genres:', 'Magazines:']:
        tag = soup.find('span', string=tag_name)
        if tag:
            key = tag_name.lower().replace(':', '')
            if key == 'genres':
                metadata[key] = [genre.text for genre in tag.find_next_sibling('span').find_all('a')]
            elif key == 'magazines':
                metadata[key] = [magazine.text for magazine in tag.find_next_sibling('span').find_all('a')]
            else:
                metadata[key] = tag.find_next_sibling('span').text.strip()
    
    poster_div = soup.find('div',class_='poster')
    if poster_div:
        img_tag = poster_div.find('img')
        if img_tag: poster_url = img_tag.get('src')

    manga_details = {
       "name":name,
       "alt_names":alt_names,
       "status":status,
       "type":type,
       "synopsis":description,
       "poster_url":poster_url
   }
    manga_details.update(metadata)
    return (manga_details)


# print(get_metadata('https://mangafire.to/manga/solo-leveling.52x0'))