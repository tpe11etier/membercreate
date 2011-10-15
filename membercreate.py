#!/usr/bin/env python

import suds
import ConfigParser
import csv


CONF = ConfigParser.ConfigParser()
CONF.read("soap.props")
url = CONF.get("Auth Header", "url")

class Service(object):

    def __init__(self, url=url):
        self.client = suds.client.Client(url)
        header = self.client.factory.create('AuthHeader')
        header.Domain = CONF.get("Auth Header", "domain")
        header.UserId = CONF.get("Auth Header", "userid")
        header.UserPassword = CONF.get("Auth Header", "userpassword")
        header.OemId = CONF.get("Auth Header", "oemid")
        header.OemPassword = CONF.get("Auth Header", "oempassword")
        self.client.set_options(soapheaders=header)
        self.orgid = self.client.service.OrganizationQueryRoot()[0]

        
class Member(object):
    def __init__(self,
                 service,
                 username,
                 firstname,
                 lastname,
                 password,
                 accountenabled):
        self.member = m = service.client.factory.create('Member')
        m.Username = username
        m.FirstName = firstname
        m.LastName = lastname
        m.Password = password
        m.AccountEnabled = accountenabled
        m.OrganizationId = service.orgid
        
class MemberCreate(object):
    def __init__(self, svc):
        self.service = svc
        self.members = svc.client.factory.create('ArrayOfMember')

    def append(self, *args):
        if len(args) == 1:
            arg = args[0]
            if not isinstance(arg, Member):
                arg = Member(self.service, *arg)
        else:
            arg = Member(self.service, *args)
        self.members.Member.append(arg.member)

    def __call__(self):
        try:
            print self.service.client.service.MemberCreate(self.members)
        except suds.WebFault as e:
            print e.fault.detail


               
def main():
    service = Service(url)
    mc = MemberCreate(service)
    reader = csv.reader(open("members.csv", "r"))
    for row in reader:
        mc.append(row[:5])
    print mc()

if __name__ == '__main__':
    main()
