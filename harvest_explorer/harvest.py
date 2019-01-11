import requests

class Harvest(object):

    API_URL = "https://api.harvestapp.com/api/v2/"

    def __init__(self, logger, token, accountid):
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            'Harvest-Account-ID': accountid,
            'Authorization': 'Bearer {}'.format(token)
        })

    def call(self, endpoint, parameters={}):
        self.logger.debug(
            'Making a request to the endpoint {}'.format(endpoint))
        r = self.session.get(url=self.API_URL + endpoint, params=parameters)
        if r.status_code == 200:
            return r.json()
        else:
            self.logger.debug(r.text)
            raise Exception('Error accessing the /me.json endpoint')

    def get_paged_results(self, endpoint, objectid, parameters={}):
        first_request = self.call(endpoint,{**parameters, **{'per_page': 100, 'page': 1}})
        results = first_request[objectid]
        total_pages = first_request['total_pages']
        entries = first_request['total_entries']
        if total_pages > 1:
            self.logger.debug('The request needs up to {} paged requests for a total of {} entries'.format(total_pages, entries))
            for page in range(2,total_pages+1):
                request = self.call(endpoint, {**parameters, **{'per_page': 100, 'page': page}})
                results = results + request[objectid]
        return results

    def check(self):
        return self.call('/users/me.json')

    def projects(self, active, client=None):
        params = {}
        if active == 'active':
            params['is_active'] = "true"
        elif active == 'inactive':
            params['is_active'] = "false"
        
        if client:
            params['client_id'] = client

        return self.get_paged_results('/projects','projects',params)

    def project(self, project_id):
        return self.call('/projects/{}'.format(project_id))

    def company(self):
        return self.call('/company')

    def clients(self, active="all"):
        params = {}
        if active == 'active':
            params['is_active'] = "true"
        elif active == 'inactive':
            params['is_active'] = "false"

        return self.get_paged_results('/clients','clients',params)

    def task_assignments(self, projectid=None):
        if projectid:
            endpoint = 'projects/{}/task_assignments'.format(projectid)
        else:
            endpoint = '/task_assignments'
        return self.get_paged_results(endpoint,'task_assignments')

    def time_entries(self, projectid):
        return self.get_paged_results('/time_entries', 'time_entries', {'project_id': projectid})

    def update_time_entry(self, time_entry_id, project_id, task_id):
        url = self.API_URL + '/time_entries/{}'.format(time_entry_id)
        params = {
            'project_id': project_id,
            'task_id': task_id
        }

        self.logger.debug('Calling PATCH for updating the time entry')
        r = self.session.patch(url=url, params=params)

        if r.status_code == 200:
            return r.json()
        else:
            self.logger.debug(r.text)
            raise Exception('Error accessing the /time_entries endpoint')
