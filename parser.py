#pip install facebook-sdk
#phone 0537260812
#name "khv99@mail.ru"
#passw "Ozomad500")
import json 
import facebook 
import requests  

def mainold(): 
#306497605824905|KCGJCpJf2vCsb9v8IxugFNDoWhs   app token
    #token = "306497605824905|KCGJCpJf2vCsb9v8IxugFNDoWhs"
    token="EAAEWwgjrcYkBOZCjTZCPBSpS463L0BIHeg8ZBZC6HqFphzdUSCzdRS2RZCsgv5OBZB7PzUsR4ZBPYReZBAvtUFaf4mb0l6tXhR9MCmj1h0jJXwf5bG9DnQfxSqYReDWmBJjvlBNv7r2F2eHkxHXf3kDHNoU6MW9ZCdZAxnUjcBDZBEXLZCUyt2ZC0JsOJLhZCcoZA6DXk5pZCrWvKJ80ZBtaqFSflcC0dDsZB1QMgMWuRPhM5ZCLNj0dL4eUev81j29h9kr7BaHukf4NDQRKQZDZD"
 
    graph = facebook.GraphAPI(token) 
    profile = graph.get_object('me', fields ='first_name, gender, birthday, email')  
      # return desired fields 
    print(json.dumps(list)) 

#EAAEWwgjrcYkBOZCjTZCPBSpS463L0BIHeg8ZBZC6HqFphzdUSCzdRS2RZCsgv5OBZB7PzUsR4ZBPYReZBAvtUFaf4mb0l6tXhR9MCmj1h0jJXwf5bG9DnQfxSqYReDWmBJjvlBNv7r2F2eHkxHXf3kDHNoU6MW9ZCdZAxnUjcBDZBEXLZCUyt2ZC0JsOJLhZCcoZA6DXk5pZCrWvKJ80ZBtaqFSflcC0dDsZB1QMgMWuRPhM5ZCLNj0dL4eUev81j29h9kr7BaHukf4NDQRKQZDZD
def main2():
    #url = "https://graph.facebook.com/v12.0/me/groups"
    token="EAAEWwgjrcYkBOZCjTZCPBSpS463L0BIHeg8ZBZC6HqFphzdUSCzdRS2RZCsgv5OBZB7PzUsR4ZBPYReZBAvtUFaf4mb0l6tXhR9MCmj1h0jJXwf5bG9DnQfxSqYReDWmBJjvlBNv7r2F2eHkxHXf3kDHNoU6MW9ZCdZAxnUjcBDZBEXLZCUyt2ZC0JsOJLhZCcoZA6DXk5pZCrWvKJ80ZBtaqFSflcC0dDsZB1QMgMWuRPhM5ZCLNj0dL4eUev81j29h9kr7BaHukf4NDQRKQZDZD"
   
    url = "https://graph.facebook.com/v12.0/2304086446304025/feed"
    # Параметры запроса
    params = {
        'access_token': token,
        'fields':  'message,created_time,from'

    }

    # Выполнение запроса
    response = requests.get(url, params=params)

    # Проверка успешности запроса
    if response.status_code == 200:
       print(response.text)
      
       data = response.json()
       print(data)
       for post in data['data']:
            print(f"Post from {post['from']['name']} at {post['created_time']}: {post['message']}")

def main():
    token="EAAEWwgjrcYkBOZCjTZCPBSpS463L0BIHeg8ZBZC6HqFphzdUSCzdRS2RZCsgv5OBZB7PzUsR4ZBPYReZBAvtUFaf4mb0l6tXhR9MCmj1h0jJXwf5bG9DnQfxSqYReDWmBJjvlBNv7r2F2eHkxHXf3kDHNoU6MW9ZCdZAxnUjcBDZBEXLZCUyt2ZC0JsOJLhZCcoZA6DXk5pZCrWvKJ80ZBtaqFSflcC0dDsZB1QMgMWuRPhM5ZCLNj0dL4eUev81j29h9kr7BaHukf4NDQRKQZDZD"
    gID=2304086446304025
    graph = facebook.GraphAPI(token) 
    groupData = graph.get_object(gID + "/feed", page=True, retry=3, limit=500)
    print(groupData)    
        

if __name__ == '__main__': 
    main() 