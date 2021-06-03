from flask import Flask,render_template,request
import sqlalchemy as db
import requests
# from sqlalchemy import func
# import math

app = Flask(__name__)

#連接資料庫
username = 'root'            # 資料庫帳號
password = 'password'        # 資料庫密碼
host = 'localhost'           # 資料庫位址
port = '3306'                # 資料庫埠號
database = 'final_project'   # 資料庫名稱
table = '西北太平洋颱風列表'  # 表格名稱
# 建立資料庫引擎
engine = db.create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')
# 建立資料庫連線
connection  = engine.connect()
# 取得資料庫的元資料（資料庫預設編碼、表格清單、表格的欄位與型態、... 等）
metadata = db.MetaData()
# 取得 table 資料表的 Python 對應操作物件
table_typhoon = db.Table(table, metadata, autoload=True, autoload_with=engine)



#以下為網頁連線路徑

@app.route('/')
def index():
    return render_template('first_page.html')

@app.route('/wea')
def wea():
    return render_template('weather_info.html')


#颱風列表分頁
@app.route('/typ')
def typ():
    connection  = engine.connect() 
    query = db.select(table_typhoon)
    proxy = connection.execute(query)
    results = proxy.fetchall()
    connection.close()
    
    return render_template('typhoon_info.html',
                           outputs=results
                        )


@app.route('/veg')
def veg():
    return render_template('product_info.html')



#蔬菜交易資料分頁
# 這裡是接受資料以及沒接受資料進入的畫面
@app.route('/veg_day', methods=['GET', 'POST']) 
def veg_day():
    # 這邊是是接 POST 回來
    firstin = veg_api()
    if request.method == 'POST':
        # 從丟回來的POST裡接出veg_type裡的值
        veg_code=request.form.get('veg_type')
        fs_date=request.form.get('fs_date')
        se_date=request.form.get('se_date')
        print(len(fs_date),len(fs_date))
        f=len(fs_date)
        s=len(se_date)
        print(veg_code)

        if f > 0 and s > 0:
            fs_li=fs_date.split('.')
            se_li=se_date.split('.')
            print("進來兩個都大於0")
            for i in range(3):
                fs_li[i]=fs_li[i].strip()
                se_li[i]=se_li[i].strip()

            for i in range(2):
                if int(fs_li[i])<10:
                    fs_li[i]='0'+fs_li[i]
                if int(se_li[i])<10:
                    se_li[i]='0'+se_li[i]
            
            print(fs_li)
            print(se_li)
            data=veg_api(veg_code,star_date=fs_li,end_date=se_li)

        elif f > 0:
            print("進來只有起始時間")
            fs_li=fs_date.split('.')
            for i in range(3):
                fs_li[i]=fs_li[i].strip()
            for i in range(2):
                if int(fs_li[i])<10:
                    fs_li[i]='0'+fs_li[i]   
            data=veg_api(veg_code,star_date=fs_li)   

        elif s > 0:
            print("進來只有終點時間")
            se_li=se_date.split('.')
            for i in range(3):
                se_li[i]=se_li[i].strip()                  
            for i in range(2):
                if int(se_li[i])<10:
                    se_li[i]='0'+se_li[i]
            data=veg_api(veg_code,end_date=se_li)
        
        else:
            print("進來沒有選時間")
            data=veg_api(veg_code)

        return render_template('veg_api_page.html',data=data)
    
    return render_template('veg_api_page.html',data=firstin)

# @app.route('/team')
# def team():
#     return render_template('my_team.html')

# 蔬菜API
def veg_api(veg_code='',star_date='',end_date=''):
    url='https://data.coa.gov.tw/Service/OpenData/FromM/FarmTransData.aspx?top=1000&CropCode='
    start=star_date
    end=end_date
    path=f'{url}{veg_code}'
    if len(star_date)>0:
        path=f'{path}&StartDate={str(int(start[2])-1911)+"."+start[1]+"."+start[0]}'
    if len(end_date)>0:
        path=f'{path}&EndDate={str(int(end[2])-1911)+"."+end[1]+"."+end[0]}'
    print(path)
    re=requests.get(path)
    data=re.json()
    li=[]
    for i in data:
        li1=[]
        li1.extend([i["交易日期"],i["作物名稱"],i["市場名稱"],i["上價"],i["中價"],i["下價"],i["平均價"],str(i["交易量"])])
        li.append(li1)
    return li


#即時天氣分頁
@app.route('/wea_day', methods=['GET', 'POST'])
def wea_api():
    # Insert government's API URL & parameters.
        # place = '基隆,鞍部,臺北,竹子湖,淡水,板橋,新屋,新竹,臺中,梧棲,日月潭,玉山,田中,嘉義,阿里山,永康,高雄,恆春,蘇澳,宜蘭,花蓮,臺東,成功,澎湖,金門,馬祖,蘭嶼'
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization=CWB-F8315AE0-0269-43E5-9FB2-FD9EB762422E&format=JSON&elementName=TIME,TEMP,HUMD,24R&parameterName=CITY,TOWN&locationName='
    if request.method != 'POST':
    # Receive API data according to specific arguments and it's in JSON format.
        re = requests.get(url).json()
        data = re['records']['location']
        weather=[]
        for i in data:
            li=[]
            li.extend([str(i['time']['obsTime']) , i['locationName'] ,str(i['weatherElement'][0]["elementValue"]),str(i['weatherElement'][1]["elementValue"]) ,str(i['weatherElement'][2]["elementValue"]) ,str(i['parameter'][0]["parameterValue"]) ,str(i['parameter'][1]["parameterValue"])])
            weather.append(li)
        return render_template('wea_api_page.html',data=weather)

    if request.method == 'POST':
        test = request.form.get('wea_type')
        path = f'{url}{test}'
        re1 = requests.get(path).json()
        data1 = re1['records']['location']
        weather1=[]
        for i1 in data1:
            lis=[]
            lis.extend(['觀測時間: '+str(i1['time']['obsTime']) , '測站名稱: '+i1['locationName'] ,'現在氣溫: '+ str(i1['weatherElement'][0]["elementValue"])+' ℃', '現在濕度: '+str(i1['weatherElement'][1]["elementValue"]) , '累積雨量: '+str(i1['weatherElement'][2]["elementValue"])+' mm' ,'所處縣市: '+str(i1['parameter'][0]["parameterValue"]) ,'所處鄉鎮: '+str(i1['parameter'][1]["parameterValue"])])
            weather1.append(lis)
        print(weather1)
        return render_template('wea_api_page1.html',data=weather1)



if __name__ == '__main__':
    app.run(debug=True)