from troposphere import Ref
from troposphere.ec2 import EIP
from troposphere.ec2 import Subnet as _Subnet
from troposphere.ec2 import VPC as _VPC
from troposphere.ec2 import InternetGateway
from troposphere.ec2 import NatGateway
from troposphere.ec2 import Route, RouteTable, SubnetRouteTableAssociation
from troposphere.ec2 import VPCGatewayAttachment


class PublicSubnet(_Subnet):
    def __init__(self, *args, **kwargs):
        template = args[1]
        super(PublicSubnet, self).__init__(*args, **kwargs)
        eip = EIP(
            self.title + "eip",
            template,
            Domain="vpc",
            DependsOn='vpcgatewayattachment'
        )
        NatGateway(
            self.title + "natgateway",
            template,
            AllocationId=Ref(eip),
            SubnetId=Ref(self)
        )
        routetable = RouteTable(
            self.title + "routetable",
            template,
            VpcId=self.properties['VpcId']
        )
        Route(
            self.title + "route",
            template,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=Ref('internetgateway'),
            RouteTableId=Ref(routetable)
        )
        SubnetRouteTableAssociation(
            self.title + "subnetroutetableassociation",
            template,
            RouteTableId = Ref(routetable),
            SubnetId = Ref(self)
        )

class PrivateSubnet(_Subnet):
    def __init__(self, *args, **kwargs):
        template = args[1]
        super(PrivateSubnet, self).__init__(*args, **kwargs)
        routetable = RouteTable(
            self.title + "routetable",
            template,
            VpcId=self.properties['VpcId']
        )
        Route(
            self.title + "route",
            template,
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=Ref('public' + self.properties['AvailabilityZone'].replace("-", "") + 'natgateway'),
            RouteTableId=Ref(routetable)
        )
        SubnetRouteTableAssociation(
            self.title + "subnetroutetableassociation",
            template,
            RouteTableId = Ref(routetable),
            SubnetId = Ref(self)
        )

class SecureSubnet(_Subnet):
    def __init__(self, *args, **kwargs):
        template = args[1]
        super(SecureSubnet, self).__init__(*args, **kwargs)

class VPC(_VPC):
    """ Overrides the standard Troposphere VPC to deal with boilerplate """
    def __init__(self, *args, **kwargs):
        super(VPC, self).__init__(*args, **kwargs)
        internetgateway = InternetGateway(
            'internetgateway',
            args[1]
        )
        VPCGatewayAttachment(
            'vpcgatewayattachment', 
            args[1], 
            InternetGatewayId=Ref(internetgateway), 
            VpcId=Ref(self)
        )
