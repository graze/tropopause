from tropopause import Tags
from troposphere import GetAtt, Ref, Template
from troposphere import Tags as upstreamTags
from troposphere.ec2 import EIP
from troposphere.ec2 import Subnet
from troposphere.ec2 import VPC
from troposphere.ec2 import InternetGateway
from troposphere.ec2 import NatGateway
from troposphere.ec2 import Route, RouteTable, SubnetRouteTableAssociation
from troposphere.ec2 import VPCGatewayAttachment


def AddTagsFromVPC(func):
    """ Helper to inject VPC tags into **kwargs """
    def wrapper(*args, **kwargs):
        tags = Tags()
        if isinstance(args[-1], Template):
            vpc = next(
                i for i in args[-1].resources.items()
                if isinstance(i[-1], VPC)
            )[-1]
        if isinstance(vpc, VPC):
            tags = tags + vpc.properties['Tags']
        if 'Tags' in kwargs and isinstance(kwargs['Tags'], upstreamTags):
            tags = tags + kwargs['Tags']
        kwargs['Tags'] = tags
        return(func(*args, **kwargs))
    return wrapper


class InternetGatewayVPC(VPC):
    ''' Overrides the standard Troposphere VPC to deal with boilerplate '''
    def __init__(self, title, template, *args, **kwargs):
        if 'Tags' not in kwargs:
            kwargs['Tags'] = Tags()
        super().__init__(title, template, *args, **kwargs)
        internet_gateway = InternetGateway(
            'internetgateway',
            template,
            Tags=kwargs['Tags']
        )
        VPCGatewayAttachment(
            'vpcgatewayattachment',
            template,
            InternetGatewayId=Ref(internet_gateway),
            VpcId=Ref(self)
        )


class PublicSubnet(Subnet):
    ''' Overrides Subnet, creates a NAT gateway '''
    @AddTagsFromVPC
    def __init__(self, title, template, *args, **kwargs):
        super().__init__(title, template, *args, **kwargs)
        EIP(
            title + 'eip',
            template,
            Domain='vpc',
            DependsOn='vpcgatewayattachment'
        )
        NatGateway(
            title + 'natgateway',
            template,
            AllocationId=GetAtt(title + 'eip', 'AllocationId'),
            SubnetId=Ref(self),
            DependsOn=title + 'eip'
        )
        RouteTable(
            title + 'routetable',
            template,
            VpcId=self.properties['VpcId'],
            Tags=kwargs['Tags']
        )
        Route(
            title + 'route',
            template,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=Ref('internetgateway'),
            RouteTableId=Ref(title + 'routetable')
        )
        SubnetRouteTableAssociation(
            title + 'subnetroutetableassociation',
            template,
            RouteTableId=Ref(title + 'routetable'),
            SubnetId=Ref(self)
        )


class PrivateSubnet(Subnet):
    ''' Overrides Subnet, routes traffic through an existing NAT gateway '''
    @AddTagsFromVPC
    def __init__(self, title, template, *args, **kwargs):
        super().__init__(title, template, *args, **kwargs)
        RouteTable(
            title + 'routetable',
            template,
            VpcId=self.properties['VpcId'],
            Tags=kwargs['Tags']
        )
        Route(
            title + 'route',
            template,
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=Ref(
                'public' + self.properties['AvailabilityZone'].replace('-', '')
                + 'natgateway'
            ),
            RouteTableId=Ref(self.name + 'routetable')
        )
        SubnetRouteTableAssociation(
            title + 'subnetroutetableassociation',
            template,
            RouteTableId=Ref(self.name + 'routetable'),
            SubnetId=Ref(self)
        )


class SecureSubnet(Subnet):
    """ Overrides Subnet """
    @AddTagsFromVPC
    def __init__(self, title, template, *args, **kwargs):
        super().__init__(title, template, *args, **kwargs)
