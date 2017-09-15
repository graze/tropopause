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


class InternetGatewayVPC(VPC):
    ''' Overrides the standard Troposphere VPC to deal with boilerplate '''
    def __init__(self, title, template, **kwargs):
        if not ('Tags' in kwargs and isinstance(kwargs['Tags'], upstreamTags)):
            kwargs['Tags'] = Tags()
        super(InternetGatewayVPC, self).__init__(title, template, **kwargs)
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


def AddTagsFromVPC(func):
    """ helper to inject VPC tags into **kwargs """
    def wrapper(*args, **kwargs):
        tags = Tags()
        if isinstance(args[-1], Template):
            vpc = next(
                i for i in args[-1].resources.items()
                if isinstance(i[-1], VPC)
            )[-1]
        if isinstance(vpc, VPC):
            tags = tags + vpc.properties['Tags']
        if 'Tags' in kwargs and isinstance(kwargs['Tags'], Tags):
            tags = tags + kwargs['Tags']
        kwargs['Tags'] = tags
        return(func(*args, **kwargs))
    return wrapper


class PublicSubnet(Subnet):
    ''' Overrides Subnet, creates a NAT gateway '''
    @AddTagsFromVPC
    def __init__(self, title, template, **kwargs):
        super(PublicSubnet, self).__init__(title, template, **kwargs)
        eip = EIP(
            title + 'eip',
            template,
            Domain='vpc',
            DependsOn='vpcgatewayattachment'
        )
        NatGateway(
            title + 'natgateway',
            template,
            AllocationId=GetAtt(self.title + 'eip', 'AllocationId'),
            SubnetId=Ref(self),
            DependsOn=eip.title
        )
        route_table = RouteTable(
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
            RouteTableId=Ref(route_table)
        )
        SubnetRouteTableAssociation(
            title + 'subnetroutetableassociation',
            template,
            RouteTableId=Ref(route_table),
            SubnetId=Ref(self)
        )


class PrivateSubnet(Subnet):
    ''' Overrides Subnet, routes traffic through an existing NAT gateway '''
    @AddTagsFromVPC
    def __init__(self, title, template, **kwargs):
        # TODO: depends on public NAT
        super(PrivateSubnet, self).__init__(title, template, **kwargs)
        route_table = RouteTable(
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
            RouteTableId=Ref(route_table)
        )
        SubnetRouteTableAssociation(
            title + 'subnetroutetableassociation',
            template,
            RouteTableId=Ref(route_table),
            SubnetId=Ref(self)
        )


class SecureSubnet(Subnet):
    """ Overrides Subnet """
    @AddTagsFromVPC
    def __init__(self, title, template, **kwargs):
        super(SecureSubnet, self).__init__(title, template, **kwargs)
