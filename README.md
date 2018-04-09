# IRProject

Webapp build with Danjago framework

To start server:
python manage.py runserver

go to: 
http://127.0.0.1:8000/

Ensure that corenlp-ib and solr url is defined in IRProject/mysite/setting.py


For example:

SOLR_URL = 'http://127.0.0.1:8983/solr/irproject/'

CORENLP = r'C:\Users\ShaoJie\Desktop\IR Pre-processing\stanford-corenlp-full-2018-02-27'

Ensure ./crawled_data/Company exist in the django project folder

Ensure IRProject/solr config/server/irproject/conf (from this clone) is copied to ./solr-7.2.1/server/solr/irproject/

Modules:
myapp  (webapp module),
glassdoor  (crawler module)

Sample crawled data: https://goo.gl/hQQFuH

