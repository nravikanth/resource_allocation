# Author
# -*- coding: utf-8 -*-
import pudb, pprint
import simplejson
# cpu in each server
server_cpu_data = {
    "large":1,
    "xlarge":2,
    "2xlarge":4,
    "4xlarge":8,
    "8xlarge":16,
    "10xlarge":32
}


class InstancePricing(object):
    """docstring for InstancePricing"""
    def __init__(self):
        super(InstancePricing, self).__init__()
        self.instances_pricing_tup = []
        pass

    def load_data(self, kwargs):
        """
        loading data and returning in required format
        """
        resp = {'success':True}
        try:
            self.__init__()
            if not kwargs.get('hours', 0):
                resp['success'] = False
                resp['msg'] = 'Required hours input'
                return resp
            hours = kwargs.get('hours')
            self.instances_pricing_data = kwargs.get('instances_pricing_data', False)
            if not self.instances_pricing_data:
                # loads default data, if instance data is not given
                with open('server_pricing.json') as data:
                    self.instances_pricing_data = eval(data.read().replace("\xc2\xad"," "))
            self.cpu_based_server_tup = tuple([tuple([server,server_cpu_data[server]]) for server in server_cpu_data])
            if kwargs.get('price', False):
                for region in self.instances_pricing_data:
                    for server in self.instances_pricing_data[region]:
                        self.instances_pricing_tup.append(tuple([server,float("{0:.3f}".format(self.instances_pricing_data[region][server]*hours)),region]))
            self.instances_pricing_tup = tuple(self.instances_pricing_tup)
        except Exception, e:
            print "Error executing load_data method, Error: %s" % str(e)
            resp['success'] = False
            resp['msg'] = "Failed with Exception: %s" % str(e)
        return resp


    def get_cost(self, **kwargs):
        """
        Base module which invoke submodules to get the cost and servers
        input: key-worded argument which take cpu count, price, hours and instances_pricing_data (if any specific)
        ouput: returns the calculate response in json format

        param instances_pricing_data should be json format

        sample output response:
        [
            {
                'region': 'us east',
                'servers': [
                            ('10xlarge', 7),
                            ('4xlarge', 1)
                ],
                'total_cost': '$123.084'
            },
            {
                'region': 'us west',
                'servers': [
                    ('10xlarge', 7),
                    ('4xlarge', 1)
                ],
                'total_cost': '$130.08'
            },
            {
                'region': 'uk west',
                'servers': [
                    ('8xlarge', 14),
                    ('4xlarge', 1)
                ],
                'total_cost': '$149.94'
            }
        ]
        """
        resp = {'success': True}
        try:
            if kwargs.has_key('price') and kwargs.has_key('cpus'):
                # 3rd case has not been implmented, returns error in try
                resp['success'] = False
                resp['msg'] = "Method not implemented yet"
                return resp
            resp_data = self.load_data(kwargs)
            if not resp_data['success']:
                return resp_data
            hours = kwargs.get('hours')
            server_cpus = {}
            mapping_server = {}
            server_pricing = []
            for server in self.instances_pricing_data:
                if kwargs.get('price'):
                    target = kwargs.get('price')
                    list_values= [prc*hours for prc in self.instances_pricing_data[server].values()]
                    mapping_tuple = self.instances_pricing_tup
                else:
                    target = kwargs.get('cpus')
                    list_values = server_cpu_data.copy()
                    # logic to get server count based on region
                    for unique in list(set(server_cpu_data) - set(self.instances_pricing_data[server])):
                        list_values.pop(unique, None)
                    list_values = list_values.values()
                    mapping_tuple = self.cpu_based_server_tup
                server_cpus_data = self.get_server_base_cpus(target, list_values,{})
                if not server_cpus_data['success']:
                    return server_cpu_data
                server_cpus[server] = server_cpus_data['data']
                mapping_server_data = self.map_server_base_cpu_count(server_cpus[server], mapping_tuple)
                if not mapping_server_data['success']:
                    return mapping_server_data
                mapping_server[server] = mapping_server_data['data']
                server_pricing_data = self.calculate_price(mapping_server[server],self.instances_pricing_data,hours,server)
                if not server_pricing_data['success']:
                    return server_pricing_data
                server_pricing.append(server_pricing_data['data'])
            resp['data'] = sorted(server_pricing, key=lambda x:x['total_cost'])
        except Exception, e:
            print "Error executing get_cost method, Error: %s" % str(e)
            resp['success'] = False
            resp['msg'] = "Failed with Exception: %s" % str(e)
        return resp


    def get_server_base_cpus(self, target, target_values, data={}):
        """
        Recursive method to calculate the possible server that can be assigned based on input given
        method takes either cpu or price as input and calculates
        Input: given cpus or price, list of cpus available in each server or prices for each server
        Output: returns possible servers that can be assigned
        """
        resp = {'success': True}
        try:
            if not target:
                return data
            if target == 1:
                data[1] = data.get(1, 0) + 1
                return data
            close_subset = tuple([(i, abs(i-target)) for i in target_values if i<=target])
            if len(close_subset)<=0:
                return data
            close_subset = tuple(sorted(close_subset, key=lambda x:x[1]))
            d_mod = divmod(target, close_subset[0][0])
            if isinstance(close_subset[0][0], float):
                data[float("{0:.3f}".format(close_subset[0][0]))]=data.get(close_subset[0][0],0)+int(d_mod[0])
            else:
                data[close_subset[0][0]]=data.get(close_subset[0][0],0)+int(d_mod[0])
            target = d_mod[1]
            self.get_server_base_cpus(target, target_values, data)
            resp['data'] = data
        except Exception,e:
            print "Error executing get_server_base_cpus method, Error: %s" % str(e)
            resp['success'] = False
            resp['msg'] = "Failed with Exception: %s" % str(e)
        return resp

    def map_server_base_cpu_count(self,server,cpu_count_tup):
        """
            Returns final mapping, that include total number of servers that can be assigned to user
            Input: Base server details
            Output: Final server that can be assigned
        """

        resp = {'success': True}
        try:
            map_servers = {}
            for s in server:
                map_servers[filter(lambda x:x[1]==s,cpu_count_tup)[0][0]] = server.get(s)
            resp['data'] = map_servers
        except Exception, e:
            print "Error executing map_server_base_cpu_count method, Error: %s" % str(e)
            resp['success'] = False
            resp['msg'] = "Failed with Exception: %s" % str(e)
        return resp

    def calculate_price(self, map_server, instance_price, hours, region):
        """
        Calculates the price of total number of servers that is assinged to user
        Input: Server Mapped data, server price data, hours, and region
        Ouput: Total cost for all servers assigned based on region
        """
        resp = {'success': True}
        try:
            temp_region={'total_cost':0}
            temp_list = []
            for k,v in map_server.items():
                temp_region['total_cost'] = float("{0:.3f}".format(temp_region.get('total_cost',0)+instance_price[region][k]*float(hours)*float(v)))
                temp_list.append(tuple([k,v]))
            temp_region['total_cost'] = '$' + str(temp_region['total_cost'])
            temp_region['servers'] = temp_list
            temp_region['region']=region
            resp['data'] = temp_region
        except Exception, e:
            print "Error executing calculate_price method, Error: %s" % str(e)
            resp['success'] = False
            resp['msg'] = "Failed with Exception: %s" % str(e)
        return resp

    def print_output(self, data):
        if data['success']:
            pprint.pprint(data['data'], width=45)
        else:
            pprint.pprint(data['msg'], width=45)


if __name__ == '__main__':
    #pudb.set_trace()
    obj = InstancePricing()
    print '----------\n----------'
    with open('server_pricing.json') as data:
        instances = eval(data.read().replace("\xc2\xad"," "))
    # specific instances passing to method
    # case 1: providing cpus and hours
    data = obj.get_cost(hours=6, cpus=232, instances_pricing_data=instances)
    print "Total servers can assgined to user based on cpus as input"
    obj.print_output(data)
    print '----------\n----------'

    # case 2: providing price and hours
    print "Total servers can assgined to user based on price as input"
    data = obj.get_cost(hours=6, price=130)
    obj.print_output(data)
    print '----------\n----------'

    # case 3: providing price, cpus and hours
    print "Total servers can assgined to user based on price & cpus as inputs"
    data = obj.get_cost(hours=6, price=130, cpus=130)
    obj.print_output(data)
    print '----------\n----------'
