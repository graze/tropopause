from tropopause import Tags
from troposphere import GetAtt, Ref, Template
from troposphere import Tags as upstreamTags
from troposphere.ec2 import (
    EIP, Subnet, VPC, InternetGateway, NatGateway,
    Route, RouteTable, SubnetRouteTableAssociation,
    VPCPeeringConnection, VPCGatewayAttachment,
    SecurityGroup, SecurityGroupRule, SecurityGroupIngress
)
import yaml


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
    """ Overrides Subnet, no route to the Internet """
    @AddTagsFromVPC
    def __init__(self, title, template, *args, **kwargs):
        super().__init__(title, template, *args, **kwargs)


class RoutedVPCPeeringConnection(VPCPeeringConnection):
    ''' Initiates peering with another VPC, adds
        Routes from all local subnets with Route Table associations
    '''
    def __init__(self, title, template, *args, **kwargs):
        self.props['PeerCidrBlock'] = (str, True)
        super().__init__(title, template, *args, **kwargs)
        for index in list(template.resources):
            resource = template.resources[index]
            if isinstance(resource, RouteTable):
                Route(
                    index + 'to' + title + 'route',
                    template,
                    DestinationCidrBlock=kwargs['PeerCidrBlock'],
                    RouteTableId=Ref(resource),
                    VpcPeeringConnectionId=Ref(self)
                )
        SecurityGroup(
            title + "securitygroup",
            template,
            GroupDescription="Allow SSH & ICMP from " + title,
            VpcId=kwargs['VpcId']
        )
        SecurityGroupIngress(
            title + "sshingress",
            template,
            GroupId=Ref(title + "securitygroup"),
            CidrIp=kwargs['PeerCidrBlock'],
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22"
        )
        SecurityGroupIngress(
            title + "icmpingress",
            template,
            GroupId=Ref(title + "securitygroup"),
            CidrIp=kwargs['PeerCidrBlock'],
            IpProtocol="icmp",
            FromPort="-1",
            ToPort="-1"
        )
        self.props.pop('PeerCidrBlock')
        self.properties.pop('PeerCidrBlock')


class SecurityGroupFromYaml(SecurityGroup):
    """ Allows for a config yaml to be passed in instead of Ingress/Egress """
    def _rulesFromYaml(self, obj):
        sgrules = []
        try:
            with open(obj, 'r') as stream:
                doc = yaml.load(stream)
                for ruleset in doc:
                    for cidr in doc[ruleset]['cidr']:
                        for protocol in doc[ruleset]['protocols']:
                            for port in doc[ruleset]['protocols'][protocol]:
                                sgrules.append(
                                    SecurityGroupRule(
                                        ''.join(
                                            ch for ch in (
                                                cidr + protocol + port
                                            ) if ch.isalnum()
                                        ),
                                        CidrIp=cidr,
                                        IpProtocol=protocol,
                                        FromPort=port,
                                        ToPort=port
                                    )
                                )
        except Exception as e:
            print(e)
            exit(1)
        finally:
            return sgrules

    def __init__(self, title, template, *args, **kwargs):
        if 'SecurityGroupIngress' in kwargs and isinstance(
            kwargs['SecurityGroupIngress'], str
        ):
            kwargs['SecurityGroupIngress'] = self._rulesFromYaml(
                kwargs['SecurityGroupIngress']
            )
        if 'SecurityGroupEgress' in kwargs and isinstance(
            kwargs['SecurityGroupEgress'], str
        ):
            kwargs['SecurityGroupEgress'] = self._rulesFromYaml(
                kwargs['SecurityGroupEgress']
            )
        super().__init__(title, template, *args, **kwargs)
