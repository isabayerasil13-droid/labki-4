from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from bank.models import Client, Account

class BankAPITests(APITestCase):
    def setUp(self):
        get_user_model().objects.create_user(username='tester', password='Test-pass-for-CI-123!')
    def login(self):
        response = self.client.post('/api/auth/token/', {'username':'tester','password':'Test-pass-for-CI-123!'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+response.data['access'])
        return response.data
    def test_authentication(self):
        for path in ['/api/clients/', '/api/accounts/']:
            self.assertEqual(self.client.get(path).status_code, 401)
            self.assertEqual(self.client.post(path, {}, format='json').status_code, 401)
        self.assertEqual(self.client.post('/api/auth/token/', {'username':'tester','password':'wrong'}, format='json').status_code, 401)
        tokens = self.login()
        self.assertEqual(self.client.post('/api/auth/refresh/', {'refresh':tokens['refresh']}, format='json').status_code, 200)
        self.assertEqual(self.client.post('/api/auth/refresh/', {'refresh':tokens['refresh']}, format='json').status_code, 401)
    def test_full_crud_and_relations(self):
        self.login()
        data = {'full_name':'Учебный клиент','iin':'000000000001','phone':'','email':'demo@example.com'}
        created = self.client.post('/api/clients/', data, format='json')
        self.assertEqual(created.status_code, 201)
        cid = created.data['id']; cp = f'/api/clients/{cid}/'
        self.assertEqual(self.client.get(cp).data['iin'], data['iin'])
        self.assertEqual(len(self.client.get('/api/clients/?search=Учебный').data), 1)
        data['full_name'] = 'Изменённый клиент'
        self.assertEqual(self.client.put(cp, data, format='json').status_code, 200)
        account = {'client':cid,'number':'KZ000000000000000001','currency':'KZT','balance':'120.50'}
        result = self.client.post('/api/accounts/', account, format='json')
        self.assertEqual(result.status_code, 201)
        ap = f"/api/accounts/{result.data['id']}/"
        self.assertEqual(self.client.get(ap).data['balance'], '120.50')
        self.assertEqual(len(self.client.get(f'/api/accounts/?client={cid}&currency=KZT').data), 1)
        self.assertEqual(self.client.get('/api/accounts/?currency=USD').data, [])
        account['balance']='200.00'
        self.assertEqual(self.client.put(ap, account, format='json').status_code, 200)
        self.assertEqual(self.client.patch(ap, {'balance':'250.00'}, format='json').status_code, 200)
        self.assertEqual(self.client.delete(cp).status_code, 409)
        self.assertEqual(self.client.delete(ap).status_code, 204)
        self.assertEqual(self.client.delete(cp).status_code, 204)
        self.assertEqual(self.client.get(cp).status_code, 404)
    def test_validation(self):
        self.login()
        self.assertEqual(self.client.post('/api/clients/', {'full_name':'A','iin':'123'}, format='json').status_code, 400)
        c=Client.objects.create(full_name='Тест', iin='000000000002')
        self.assertEqual(self.client.post('/api/clients/', {'full_name':'B','iin':c.iin}, format='json').status_code,400)
        data={'client':c.id,'number':'KZ000000000000000002','balance':'-1','currency':'KZT'}
        self.assertEqual(self.client.post('/api/accounts/',data,format='json').status_code,400)
        data['balance']='0';data['client']=999999
        self.assertEqual(self.client.post('/api/accounts/',data,format='json').status_code,400)
        self.assertEqual(self.client.get('/api/accounts/?client=abc').status_code,400)
        self.assertEqual(self.client.get('/api/accounts/?currency=INVALID').status_code,400)
    def test_logout(self):
        tokens=self.login()
        self.assertEqual(self.client.post('/api/auth/logout/', {'refresh':tokens['refresh']}, format='json').status_code,200)
        self.assertEqual(self.client.post('/api/auth/refresh/', {'refresh':tokens['refresh']}, format='json').status_code,401)
    def test_interface(self):
        response=self.client.get('/')
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Банковские клиенты и счета')
