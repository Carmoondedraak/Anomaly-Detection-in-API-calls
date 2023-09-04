import http
from urllib import request
from locust import User, task, between
import random
import requests
from requests.auth import HTTPBasicAuth
import json
from requests_toolbelt.adapters.source import SourceAddressAdapter
import random
import pandas as pd
import requests
from requests_toolbelt.utils import dump
from collections import OrderedDict
import csv
import os
import random
import time

user_credentials = [('LeoCastillo', 'cqjCuemq', 'LCastillo@live.com', 'Leo', 'Castillo', 'Main Street', 4385, 'Melbourne ', 'Australia', 43660631661, '8/2023', 598), ('GiannaBennet', 'raZzGLsM', 'GBennet@gmail.com', 'Gianna', 'Bennet', '9th Street', 9385, 'Nanchong ', 'China', 22419327484, '6/2029', 146), ('EzekielHoward', 'RtoPtcCx', 'EHoward@yahoo.com', 'Ezekiel', 'Howard', 'Virginia Avenue ', 3073, 'Mogadishu ', 'Somalia', 85320476856, '12/2029', 998), ('SebastianWard', 'dtKMksBb', 'SWard@live.com', 'Sebastian', 'Ward', '3rd Street ', 7918, 'Moscow ', 'Russia', 60853515692, '5/2026', 677), ('LucasJimenez', 'ZYBKRdlZ', 'LJimenez@yahoo.com', 'Lucas', 'Jimenez', 'Front Street ', 8277, 'London ', 'United Kingdom', 65051587245, '5/2029', 465), ('JackHoward', 'DMfpOeZS', 'JHoward@live.com', 'Jack', 'Howard', 'East Street ', 5874, 'Caracas ', 'Venezuela', 21805009699, '10/2026', 968), ('GraceWatson', 'hkPVAygW', 'GWatson@hotmail.com', 'Grace', 'Watson', 'Highland Avenue ', 5251, 'Xian ', 'China', 33405099951, '12/2029', 794), ('EliasBrooks', 'oXIrObce', 'EBrooks@yahoo.com', 'Elias', 'Brooks', 'Valley Road', 5197, 'Wuhan ', 'China', 23900591872, '6/2028', 648), ('ZoeyCox', 'wpsPWfpn', 'ZCox@hotmail.com', 'Zoey', 'Cox', 'Meadow Lane ', 7219, 'Rome ', 'Italy', 88273832401, '2/2030', 347), ('MateoCook', 'uptzpEEW', 'MCook@yahoo.com', 'Mateo', 'Cook', 'Maple Street', 3450, 'Rome ', 'Italy', 71618993271, '11/2023', 403), ('EllaRichardson', 'MjZZTyfD', 'ERichardson@hotmail.com', 'Ella', 'Richardson', 'Church Street', 1590, 'Pyongyang ', 'North Korea', 28144082754, '8/2029', 595), ('LaylaKelly', 'TNlMpiZw', 'LKelly@yahoo.com', 'Layla', 'Kelly', 'Monroe Street ', 7482, 'Tehran ', 'Iran', 31034271136, '5/2024', 220), ('HazelStewart', 'OLEmTNTO', 'HStewart@hotmail.com', 'Hazel', 'Stewart', 'Elizabeth Street', 3949, 'Rome ', 'Italy', 63254985111, '6/2029', 940), ('SophiaMendoza', 'dVcUXvPQ', 'SMendoza@live.com', 'Sophia', 'Mendoza', 'Main Street North', 3921, 'Taipei ', 'Taiwan', 60481443826, '11/2024', 735), ('IsaiahJimenez', 'KmnAsDPe', 'IJimenez@gmail.com', 'Isaiah', 'Jimenez', 'Hill Street ', 8466, 'Los Angeles ', 'United States', 85160631751, '5/2025', 795), ('AuroraBailey', 'XcaKaEkj', 'ABailey@yahoo.com', 'Aurora', 'Bailey', '9th Street', 7039, 'Harbin ', 'China', 91494097941, '12/2026', 388), ('WilliamSanders', 'VhZFLtKT', 'WSanders@live.com', 'William', 'Sanders', 'Madison Street ', 8106, 'Alexandria ', 'Egypt', 29941706469, '5/2025', 175), ('IslaStewart', 'vHuXygaF', 'IStewart@live.com', 'Isla', 'Stewart', 'Prospect Street', 3341, 'Seoul ', 'South Korea', 19723019126, '8/2023', 101), ('WaylonBrooks', 'DiszGwdv', 'WBrooks@yahoo.com', 'Waylon', 'Brooks', '7th Street', 3956, 'Yunfu ', 'China', 44132174677, '3/2028', 105), ('AriaWard', 'wNSMrUNk', 'AWard@yahoo.com', 'Aria', 'Ward', 'Church Street', 5614, 'Berlin ', 'Germany', 80700137779, '2/2029', 519), ('HenryMurphy', 'XzsWGnvW', 'HMurphy@yahoo.com', 'Henry', 'Murphy', 'Prospect Avenue', 1265, 'Lahore ', 'Pakistan', 36246698486, '7/2024', 661), ('PenelopeReed', 'vzAoFWDa', 'PReed@live.com', 'Penelope', 'Reed', 'Fairway Drive ', 7805, 'Kinshasa', 'Democratic Republic of the Congo', 49061012566, '7/2027', 743), ('LunaMorgan', 'WpKkjXWO', 'LMorgan@live.com', 'Luna', 'Morgan', 'East Street ', 7335, 'Pyongyang ', 'North Korea', 89155812230, '12/2023', 178), ('HarperOrtiz', 'YDmPfkLB', 'HOrtiz@live.com', 'Harper', 'Ortiz', 'Jackson Street ', 1160, 'Incheon ', 'South Korea', 15943105128, '10/2030', 810), ('JaxonPeterson', 'dytwPpxG', 'JPeterson@live.com', 'Jaxon', 'Peterson', '3rd Street ', 5976, 'Moscow ', 'Russia', 74518581636, '7/2026', 102), ('NoahCastillo', 'PuEMJKyU', 'NCastillo@yahoo.com', 'Noah', 'Castillo', 'Spring Street ', 6549, 'Berlin ', 'Germany', 44060340404, '10/2024', 166), ('LucasWilliams', 'HxEisuKm', 'LWilliams@yahoo.com', 'Lucas', 'Williams', 'Main Street West', 7365, 'Seoul ', 'South Korea', 99715402167, '2/2029', 911), ('AlexanderBailey', 'dURKAIVM', 'ABailey@yahoo.com', 'Alexander', 'Bailey', 'Main Street East ', 3692, 'Los Angeles ', 'United States', 65031407415, '9/2023', 675), ('MilaReed', 'ZQBGvkpF', 'MReed@yahoo.com', 'Mila', 'Reed', 'Vine Street ', 5242, 'Taipei ', 'Taiwan', 47034623288, '6/2028', 400), ('PaisleyMiller', 'VESjbBWN', 'PMiller@hotmail.com', 'Paisley', 'Miller', 'Main Street East ', 8059, 'Tianjin ', 'China', 36750540714, '9/2026', 149), ('LaylaRogers', 'nEUIAObj', 'LRogers@live.com', 'Layla', 'Rogers', 'Church Street', 1588, 'Riyadh', 'Saudi Arabia', 50971048012, '9/2030', 350), ('MatthewCook', 'aawJBGGo', 'MCook@gmail.com', 'Matthew', 'Cook', 'Broad Street', 8615, 'Shiyan ', 'China', 37985290178, '2/2027', 172), ('MatthewBrooks', 'jJfiSoki', 'MBrooks@live.com', 'Matthew', 'Brooks', 'Grove Street', 8976, 'Pune ', 'India', 57801331784, '8/2025', 947), ('ScarlettGump', 'YFKrpIRh', 'SGump@live.com', 'Scarlett', 'Gump', 'Central Avenue ', 9366, 'Al Barah ', 'Iraq', 29215278439, '3/2023', 720), ('JacksonRodriguez', 'aoUjtzbV', 'JRodriguez@yahoo.com', 'Jackson', 'Rodriguez', 'Winding Way', 2817, 'Jaipur ', 'India', 14259202298, '2/2025', 141), ('LukeHughes', 'KDniMYyI', 'LHughes@hotmail.com', 'Luke', 'Hughes', 'Mill Street ', 9846, ' Tokyo ', 'Japan', 23882190455, '8/2029', 864), ('GraysonCooper', 'IGtYrUmj', 'GCooper@gmail.com', 'Grayson', 'Cooper', 'Green Street', 2872, 'Madrid ', 'Spain', 76940273221, '1/2023', 859), ('WilliamDavis', 'IWxAHsUl', 'WDavis@hotmail.com', 'William', 'Davis', 'Madison Street ', 4666, 'Mexico City ', 'Mexico', 28164566487, '12/2029', 837), ('LiamHughes', 'JdOvvexo', 'LHughes@gmail.com', 'Liam', 'Hughes', 'Walnut Street', 7018, 'Dar es Salaam ', 'Tanzania', 41947502800, '1/2030', 801), ('EliasCook', 'EHfVHAFM', 'ECook@yahoo.com', 'Elias', 'Cook', 'Lincoln Avenue ', 9240, 'Ahmadabad ', 'India', 96265269828, '7/2028', 196), ('SophiaChavez', 'gpIdwbvj', 'SChavez@yahoo.com', 'Sophia', 'Chavez', 'Lincoln Avenue ', 2518, 'Dar es Salaam ', 'Tanzania', 52282501100, '7/2024', 245), ('OliviaReyes', 'zFsqBADf', 'OReyes@yahoo.com', 'Olivia', 'Reyes', 'Lincoln Avenue ', 5475, 'Shenyang ', 'China', 35580884171, '6/2025', 700), ('LilyForest', 'QhjEDOsT', 'LForest@live.com', 'Lily', 'Forest', 'Central Avenue ', 8327, 'Bangkok ', 'Thailand', 28967863820, '7/2030', 922), ('HenryTrump', 'qrNAPPPz', 'HTrump@yahoo.com', 'Henry', 'Trump', '11th Street', 6123, 'Cape Town ', 'South Africa', 90212898211, '8/2025', 363), ('HudsonCox', 'huEGBFVF', 'HCox@gmail.com', 'Hudson', 'Cox', 'Prospect Avenue', 6519, 'Lagos ', 'Nigeria', 17376935456, '10/2028', 234), ('JulianCooper', 'IBaFUNsw', 'JCooper@hotmail.com', 'Julian', 'Cooper', '5th Avenue', 9004, 'Lima ', 'Peru', 16064641669, '3/2023', 359), ('ChloeCastillo', 'JrnMYGMj', 'CCastillo@hotmail.com', 'Chloe', 'Castillo', 'Jefferson Avenue', 2029, 'Wuhan ', 'China', 89684564154, '3/2030', 797), ('EmmaCox', 'LwfNlGOK', 'ECox@gmail.com', 'Emma', 'Cox', '12th Street', 5694, 'Melbourne ', 'Australia', 78085269237, '4/2028', 384), ('VioletMyers', 'IkdOVlJe', 'VMyers@hotmail.com', 'Violet', 'Myers', 'Park Street ', 6731, 'Melbourne ', 'Australia', 79251576391, '7/2025', 646), ('OliviaCox', 'uCRZgYcq', 'OCox@live.com', 'Olivia', 'Cox', '3rd Street West ', 5835, 'Rome ', 'Italy', 68749838337, '1/2023', 152), ('LeoPrice', 'mmqfDPmF', 'LPrice@hotmail.com', 'Leo', 'Price', 'Hill Street ', 4496, 'Kabul ', 'Afghanistan', 54023063069, '4/2024', 731), ('GraceMorales', 'NqhpWRzE', 'GMorales@hotmail.com', 'Grace', 'Morales', '1st Street ', 2297, 'Sydney ', 'Australia', 99385969971, '8/2023', 526), ('OliverOrtiz', 'uIDyBOKO', 'OOrtiz@yahoo.com', 'Oliver', 'Ortiz', 'Park Place ', 3638, 'Singapore ', 'Singapore', 84317546585, '3/2026', 998), ('MiaRoss', 'HSgyRwGh', 'MRoss@yahoo.com', 'Mia', 'Ross', 'Main Street South ', 4561, 'Lima ', 'Peru', 81160958829, '2/2030', 117), ('EverlyBrooks', 'mZdxqATh', 'EBrooks@hotmail.com', 'Everly', 'Brooks', '4th Street West', 4636, ' Mumbai ', 'India', 57472867927, '11/2025', 599), ('EzraJones', 'dcjKcTfY', 'EJones@gmail.com', 'Ezra', 'Jones', 'Franklin Street ', 2266, 'Karachi ', 'Pakistan', 41492295180, '6/2028', 980), ('StellaHughes', 'KSOVZzbk', 'SHughes@gmail.com', 'Stella', 'Hughes', '11th Street', 8579, 'Jeddah ', 'Saudi Arabia', 37272181999, '5/2025', 767), ('DanielRoss', 'oNgEFkfZ', 'DRoss@gmail.com', 'Daniel', 'Ross', 'Jackson Street ', 6636, 'Zhumadian', 'China', 83229922687, '5/2028', 960), ('WyattRamos', 'sFDctJez', 'WRamos@live.com', 'Wyatt', 'Ramos', '1st Street ', 6369, 'Tianjin ', 'China', 45508929616, '4/2028', 348), ('LiamMyers', 'kQjkdrHp', 'LMyers@live.com', 'Liam', 'Myers', 'Pine Street', 2219, 'Jeddah ', 'Saudi Arabia', 98682648051, '6/2028', 189), ('SebastianPeterson', 'fFPDJszY', 'SPeterson@hotmail.com', 'Sebastian', 'Peterson', 'Green Street', 2780, 'Madrid ', 'Spain', 65147087861, '5/2027', 619), ('EliasWard', 'CBvovTLW', 'EWard@gmail.com', 'Elias', 'Ward', 'Meadow Lane ', 5483, 'Durban ', 'South Africa', 57935971602, '5/2025', 260), ('AidenRuiz', 'jiDmDyxs', 'ARuiz@live.com', 'Aiden', 'Ruiz', 'Maple Street', 9913, 'Sirat ', 'India', 67688613358, '5/2026', 296), ('LincolnStewart', 'iPdZJQSE', 'LStewart@hotmail.com', 'Lincoln', 'Stewart', 'East Street ', 1716, 'Guangzho ', 'China', 11078040134, '3/2023', 146), ('VioletWood', 'SKcqArTW', 'VWood@hotmail.com', 'Violet', 'Wood', 'Prospect Street', 6323, 'Karachi ', 'Pakistan', 23859372153, '12/2030', 803), ('HenryPeterson', 'lHMsPsDq', 'HPeterson@gmail.com', 'Henry', 'Peterson', 'Jefferson Street ', 7516, 'Sydney ', 'Australia', 26246787770, '8/2028', 381), ('OliverCook', 'dkGBCImu', 'OCook@yahoo.com', 'Oliver', 'Cook', 'Main Street South ', 3333, 'Chongqing', 'China', 59116893297, '4/2027', 864), ('HenryWilliams', 'qFueHlDK', 'HWilliams@live.com', 'Henry', 'Williams', 'East Street ', 2894, "Tai'an ", 'China', 86583415921, '4/2028', 283), ('LiamAlvarez', 'QSLtZyZb', 'LAlvarez@yahoo.com', 'Liam', 'Alvarez', 'Union Street ', 9059, 'Salvador ', 'Brazil', 24821078152, '4/2029', 978), ('WilliamWilliams', 'eRnkTytN', 'WWilliams@live.com', 'William', 'Williams', 'Spruce Street ', 3557, 'Nanchong ', 'China', 42691249165, '3/2028', 406), ('LincolnRogers', 'BCvutqik', 'LRogers@live.com', 'Lincoln', 'Rogers', '10th Street ', 9792, 'Zhumadian', 'China', 57899812798, '12/2023', 645), ('PaisleyReed', 'zvLdeKmy', 'PReed@hotmail.com', 'Paisley', 'Reed', '12th Street', 1466, 'Manila ', 'Philippines', 50069493675, '10/2025', 220), ('NovaChavez', 'VrZKHKOC', 'NChavez@yahoo.com', 'Nova', 'Chavez', 'Front Street ', 7379, "Tai'an ", 'China', 24606697922, '7/2030', 565), ('EliasRamos', 'tGIchuht', 'ERamos@live.com', 'Elias', 'Ramos', 'Park Street ', 6628, 'Pusan ', 'South Korea', 31872115128, '1/2027', 838), ('TheodoreMorales', 'sTmBdOPF', 'TMorales@gmail.com', 'Theodore', 'Morales', 'Highland Avenue ', 2498, 'Yueyang ', 'China', 26727863474, '3/2027', 438), ('GabrielWard', 'WihPLKlk', 'GWard@yahoo.com', 'Gabriel', 'Ward', 'School Street ', 4145, 'Saint Petersburg ', 'Russia', 57712686853, '11/2030', 139), ('GabrielGump', 'iVChVYZJ', 'GGump@yahoo.com', 'Gabriel', 'Gump', '3rd Street ', 7544, 'Delhi ', 'India', 99440487195, '3/2027', 329), ('OliviaLong', 'lQOJgbJs', 'OLong@yahoo.com', 'Olivia', 'Long', 'River Road ', 9633, 'Chongqing', 'China', 12007591887, '6/2023', 217), ('KinsleyJones', 'OXNgcGKz', 'KJones@yahoo.com', 'Kinsley', 'Jones', 'Elm Street ', 9028, 'Kinshasa', 'Democratic Republic of the Congo', 31362064271, '3/2025', 792), ('EleanorReyes', 'YeNCcPic', 'EReyes@hotmail.com', 'Eleanor', 'Reyes', 'Washington Street ', 6234, ' Chi Minh City ', 'Vietnam', 84308436009, '1/2029', 740), ('HarperMyers', 'zDnPmWxL', 'HMyers@gmail.com', 'Harper', 'Myers', 'Jefferson Street ', 7272, 'Puyang ', 'China', 67582847081, '12/2030', 777), ('LincolnCastillo', 'xMlslUAj', 'LCastillo@hotmail.com', 'Lincoln', 'Castillo', 'Locust Street ', 9791, 'Taiyuan ', 'China', 88150182557, '8/2030', 799), ('OliviaRogers', 'SbiRtiWN', 'ORogers@yahoo.com', 'Olivia', 'Rogers', '1st Avenue', 3409, 'Shenyang ', 'China', 83053210059, '10/2023', 616), ('OliviaBennet', 'wQZhMHAt', 'OBennet@yahoo.com', 'Olivia', 'Bennet', '9th Street', 3379, 'Abidjan ', "Cote d'Ivoire", 41447723109, '8/2026', 649), ('VioletForest', 'FRAYfXox', 'VForest@hotmail.com', 'Violet', 'Forest', 'Fairway Drive ', 8137, 'Cape Town ', 'South Africa', 65719030396, '2/2023', 562), ('GraysonForest', 'gANTlXWs', 'GForest@live.com', 'Grayson', 'Forest', 'Walnut Street', 7068, 'Yangon ', 'Myanmar', 50938879875, '10/2026', 144), ('DelilahHoward', 'WZLmvUWa', 'DHoward@hotmail.com', 'Delilah', 'Howard', 'Spruce Street ', 5062, 'Kolkata ', 'India', 57968000193, '7/2023', 339), ('OliviaLong', 'jKzYaubF', 'OLong@hotmail.com', 'Olivia', 'Long', 'River Road ', 7680, 'Tianjin ', 'China', 24930219890, '12/2025', 638), ('AuroraCook', 'CpkIwREN', 'ACook@gmail.com', 'Aurora', 'Cook', 'Park Place ', 4669, 'Luanda ', 'Angola', 79603231952, '2/2030', 620), ('KinsleyForest', 'tLOhqKTz', 'KForest@hotmail.com', 'Kinsley', 'Forest', '5th Avenue', 5754, 'Chengdu', 'China', 84060845603, '3/2024', 721), ('JulianCox', 'zsMVvbjC', 'JCox@yahoo.com', 'Julian', 'Cox', 'Elizabeth Street', 6357, 'Nanchong ', 'China', 35644842024, '4/2030', 983), ('IvyMorgan', 'VsrVGGSe', 'IMorgan@gmail.com', 'Ivy', 'Morgan', 'Route ', 2453, 'Bangkok ', 'Thailand', 49868066888, '11/2029', 723), ('EverlyMiller', 'ODKYJXZe', 'EMiller@live.com', 'Everly', 'Miller', 'Walnut Street', 8112, 'Hyderbd ', 'India', 35125132258, '4/2023', 627), ('JacksonRuiz', 'zhETDwAO', 'JRuiz@gmail.com', 'Jackson', 'Ruiz', 'Virginia Avenue ', 7448, 'Kanpur ', 'India', 78718199282, '4/2024', 120), ('ScarlettBennet', 'tMkOzxik', 'SBennet@hotmail.com', 'Scarlett', 'Bennet', 'Hill Street ', 6216, 'Ibadan ', 'Nigeria', 88847083808, '10/2026', 285), ('EverlySanders', 'rXMHXljp', 'ESanders@yahoo.com', 'Everly', 'Sanders', 'Adams Street ', 5639, 'Moscow ', 'Russia', 28520914579, '12/2029', 140), ('GiannaMorgan', 'neKrzZMq', 'GMorgan@live.com', 'Gianna', 'Morgan', 'Park Street ', 9727, 'Istanbul ', 'Turkey', 40455755604, '11/2025', 796), ('NaomiGump', 'bviPONMG', 'NGump@yahoo.com', 'Naomi', 'Gump', '10th Street ', 6734, 'Delhi ', 'India', 75644018189, '12/2030', 325), ('ElenaRuiz', 'JyaKPavU', 'ERuiz@yahoo.com', 'Elena', 'Ruiz', 'Main Street East ', 1978, 'Santiago ', 'Chile', 60755790234, '2/2030', 946), ('EmmaCooper', 'XHzbDHpN', 'ECooper@live.com', 'Emma', 'Cooper', '6th Street', 6612, 'Tehran ', 'Iran', 23242298685, '2/2023', 186)]

class UserWithOrders(User):
  '''Wait time: interval between tasks/events (actions of the user)
     between for a random time between a min and max value - research user interaction times?
      Discussion - computers are not random look at entropy of randomizer
      Possible to have different wait times between different types of tasks? yes create wait time
      Throughput - do I want this? - NO  
      weight - determines proportion of user created
      on stop and interrupt - interesting for differing user behaviour
      
      can do sequential tasks by creating full user flow in a single task with probabilities'''
      
  wait_time = between(1, 5)
  fixed_count = 1

  def __init__(self, parent):
        super().__init__(parent)
        sockshopurl = (self.host)
        client = SockShopClient(sockshopurl)
        self.client = client
        self.reset()
        self.data = []
        self.ip_address = '{}.{}.{}.{}'.format(random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))
        r = random.random()
        if r < 0.1:
            ua = random.choice(['Python','Postman'])
        else:
           ua = random.choice(['Mozilla','Safari','Chrome'])
        self.user_agent =ua

  def reset(self):
    self.user = {}
    self.cart = {}
    self.item = {}
    self.catalogue = {}

  def on_start(self):
    '''will be called for every user when they start'''

    client = self.client
    # register
    username,password,email,firstname,lastname,add, post, city,country, bank, data, ccv = user_credentials.pop()    
    self.user = {
                "username": username,
                "password": password,
                "email": email,
                "firstName": firstname,
                "lastName": lastname,
                "address" : add,
                "postcode" : post,
                "city" : city,
                "country" : country,
                "banknum" : bank,
                "date" : data,
                "ccv" : ccv

              }
    print(self.user_agent)
    res, data1 = client.register(self.user_agent,username=self.user['username'], password=self.user['password'], email=self.user['email'],
                    firstName=self.user['firstName'], lastName=self.user['lastName'])
    

    res, data2 = client.add_address(street=self.user['address'], postcode=self.user['postcode'], city= self.user['city'],country=self.user['country'],number='1')
    
 
    res, data3 = client.add_credit_card(longnum=self.user['banknum'], expires=self.user['date'], ccv=self.user['ccv'])

    
    self.coockie, data4= client.login(self.user_agent,self.user['username'], self.user['password'])
 



  @task(10)
  def browse(self):
    ''''''
    client = self.client
    tags = client.get_tags()
    _tags = random.choices(tags, k=random.randint(0, len(tags)))
    
    self.catalogue, data = client.get_catalogue(_tags)

    if len(self.catalogue) == 0:
      return
    self.item = random.choice(self.catalogue)

    data1 = client.browse_to_item(self.item['id'])


  @task(2)
  def get_cart(self):

    self.cart, data = self.client.get_cart()

  
  @task(10)
  def add_to_cart(self):
    if len(self.catalogue) == 0:
      return

    self.item = random.choice(self.catalogue)
    _,data = self.client.add_to_cart(self.item['id'])

  
  @task(1)
  def empty_cart(self):
    if not self.cart:
      return
    data,times = self.client.empty_cart(self.cart)
    for i in range(len(data)):
        self.data.append((data[i],times[i]))


  @task(5)
  def checkout(self):

    if not self.cart:
      return

    data = self.client.checkout()


class OnlyBrowsingUser(User):
  '''  This object creates a user that can register and login
            But it  is only able to browser'''
#   weight = 3
  wait_time = between(1, 5)
  fixed_count = 1

  def __init__(self, parent):
        '''create user, link client to user'''
        super().__init__(parent)
        sockshopurl = (self.host)
        client = SockShopClient(sockshopurl)
        self.client = client
        self.reset()
        self.data = []
        self.ip_address = '10.{}.{}.{}'.format(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        r = random.random()
        if r < 0.1:
            ua = random.choice(['Python','Postman'])
        else:
           ua = random.choice(['Mozilla','Safari','Chrome'])
        self.user_agent = ua
  def on_start(self):
    '''will be called for every user when they start'''
    client = self.client
    # register
    username,password,email,firstname,lastname,add, post, city,country, bank, data, ccv = user_credentials.pop()    
    self.user = {
                "username": username,
                "password": password,
                "email": email,
                "firstName": firstname,
                "lastName": lastname,
                "address" : add,
                "postcode" : post,
                "city" : city,
                "country" : country,
                "banknum" : bank,
                "date" : data,
                "ccv" : ccv

              }
    res, data1 = client.register(self.user_agent,username=self.user['username'], password=self.user['password'], email=self.user['email'],firstName=self.user['firstName'], lastName=self.user['lastName'])
    res, data2 = client.add_address(street=self.user['address'], postcode=self.user['postcode'], city= self.user['city'],country=self.user['country'],number='0')
    res, data3 = client.add_credit_card(longnum=self.user['banknum'], expires=self.user['date'], ccv=self.user['ccv'])
    self.coockie, data4 = client.login(self.user_agent,self.user['username'], self.user['password'])


  def reset(self):
    self.user = {}
    self.cart = {}
    self.item = {}
    self.catalogue = {}

  @task
  def browse(self):
    client = self.client
    tags = client.get_tags()
    _tags = random.choices(tags, k=random.randint(0, len(tags)))
    self.catalogue, data = client.get_catalogue(_tags)
    if len(self.catalogue) == 0:
      return 
    self.item = random.choice(self.catalogue)

    data1 = client.browse_to_item(self.item['id'])



class SockShopClient(object):
    def __init__(self, url):
        self._url = url
        self._s = None
        self.responses = []

    def _build_url(self, url):
        return self._url + url

    def login(self, user_agent, username, password):
        # proxies = {"http": "10.10.0.1"}
        self._s = requests.Session()


        self._s.headers.update({'content-type': 'application/json','User-agent': user_agent})
        res = self._s.get(self._build_url('/login'), auth=HTTPBasicAuth(username, password))
        print(self._s.cookies)
        return self._s.cookies, dump.dump_all(res).decode('utf-8')


    def logout(self):
        self._s = None

    def register(self,user_agent, username, password, email, firstName, lastName):
        self._s = requests.Session()
        self._s.headers.update({'content-type': 'application/json','User-agent': user_agent})

        data = {
            'username': username,
            'password': password,
            'email': email,
            'firstName': firstName,
            'lastName': lastName
        }
        # proxies = {"http": "10.10.0.1"}
        res = self._s.post(self._build_url('/register'), data=json.dumps(data))
        
        return res, dump.dump_all(res).decode('utf-8')

    def get_tags(self):
        # dynamic tag pulling removed because of detected issues in /tags - duplicated elements
        # res = requests.get(self._build_url('/tags'))
        # if res.status_code != 200 or res.json()['err']:
        #     raise Exception(f"Failed to get tags: {res} {res.json().get('err')}")
        # return res.json()['tags']
        res = '{"tags":["brown","geek","formal","blue","skin","red","action","sport","black","magic","green"],"err":null}'
        return json.loads(res)['tags']
        

    def get_catalogue(self, tags=[]):
        params = {
            'tags': ','.join(tags),
            'page': 1,
            'size': 100
        }
        res = requests.get(self._build_url('/catalogue'), params=params)
       
        if res.status_code != 200:
            raise Exception(f"Failed to get catalogue: {res} {res.json()}")
        return res.json(), dump.dump_all(res).decode('utf-8')

    def get_cart(self):
        res = self._s.get(self._build_url('/cart'))
        if res.status_code != 200:
            raise Exception(f"failed to get cart: {res} {res.json()}")
        
        return res.json(), dump.dump_all(res).decode('utf-8')

    def empty_cart(self, cart=None):
        if not cart:
            cart = self.get_cart()
        data = []
        times = []
        for item in cart:
            times.append(time.strftime("%a, %d %b %Y %H:%M:%S GMT",  time.gmtime()))
            res, data1 = self.remove_from_cart(item['itemId'])
            data.append(data1)
        return data,times

    def add_to_cart(self, item):
        data = {
            'id': item
        }

        res = self._s.post(self._build_url('/cart'), data=json.dumps(data))
        if res.status_code != 201:
            raise Exception(f"Failed to add {item} to cart: {res} {res.json()}")
        return res, dump.dump_all(res).decode('utf-8')

    def remove_from_cart(self, item):
        res = self._s.delete(self._build_url(f'/cart/{item}'))
        if res.status_code != 202:
            raise Exception(f"Failed to remove {item} from cart: {res} {res.json()}")

        return res, dump.dump_all(res).decode('utf-8')

    def checkout(self):
        res = self._s.post(self._build_url('/orders'))
        return dump.dump_all(res).decode('utf-8')

        # if res.status_code != 201:
        #     raise Exception(f"Failed to checkout: {res} {res.json()}")
        # return res.json(), 
    def add_address(self, street, number, city, postcode, country):
        data = {
            "street": street,
            "number": number,
            "city": city,
            "postcode": postcode,
            "country": country
        }
        res = self._s.post(self._build_url('/addresses'), data=json.dumps(data))
        if res.status_code != 200:
            raise Exception(f"Failed to add address: {res} {res.json()}")
        return res.json(), dump.dump_all(res).decode('utf-8')

    def get_address(self):
        res = self._s.get(self._build_url('/address'))
        if res.status_code != 200:
            raise Exception(f"Failed to get address: {res} {res.json()}")
        if res.json().get('status_code') == 500:
            return {}
        return res.json(), dump.dump_all(res).decode('utf-8')

    def get_card(self):
        res = self._s.get(self._build_url('/card'))
        if res.status_code != 200:
            raise Exception(f"Failed to get card: {res} {res.json()}")
        if res.json().get('status_code') == 500:
            return {}
        return res.json(), dump.dump_all(res).decode('utf-8')

    def get_orders(self):
        res = self._s.get(self._build_url('/orders'))
        if res.status_code != 201:
            raise Exception(f"Failed to get orders: {res} {res.json()}")
        return res.json(), dump.dump_all(res).decode('utf-8')

    def add_credit_card(self, longnum, expires, ccv):
        data = {
            "longNum": longnum,
            "expires": expires,
            "ccv": ccv,
        }
        res = self._s.post(self._build_url('/cards'), data=json.dumps(data))
        if res.status_code != 200:
            raise Exception(f"Failed to add credit card: {res} {res.json()}")
        return res.json(), dump.dump_all(res).decode('utf-8')

    def browse_to_item(self, id):
        res = self._s.get(self._build_url(f'/detail.html?id={id}'))
        if res.status_code not in [304, 200]:
            raise Exception(f"failed to browse to item {id}: {res} ")
        return dump.dump_all(res).decode('utf-8')


