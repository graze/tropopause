from troposphere import Ref, Template
from tropopause.ec2 import VPC, PublicSubnet, PrivateSubnet, SecureSubnet
from ipaddress import ip_network

CidrBlock = '10.10.0.0/20'
region = 'us-east-1'
subnets = list(ip_network(CidrBlock).subnets(prefixlen_diff=4))

template = Template()
template.add_version('2010-09-09')
template.add_description('Example VPC')
vpc = VPC(
    'vpc',
    template,
    CidrBlock=CidrBlock
)

i = 0
zones = ['a', 'b', 'c']
for zone in zones:
    PublicSubnet(
        'public' + region.replace('-', '') + zone,
        template,
        AvailabilityZone=region + zone,
        CidrBlock=str(subnets[i]),
        MapPublicIpOnLaunch=True,
        VpcId=Ref(vpc)
    )
    PrivateSubnet(
        'private' + region.replace('-', '') + zone,
        template,
        AvailabilityZone=region + zone,
        CidrBlock=str(subnets[i + len(zones)]),
        MapPublicIpOnLaunch=False,
        VpcId=Ref(vpc)
    )
    SecureSubnet(
        'secure' + region.replace('-', '') + zone,
        template,
        AvailabilityZone=region + zone,
        CidrBlock=str(subnets[i + 2 * len(zones)]),
        MapPublicIpOnLaunch=False,
        VpcId=Ref(vpc)
    )
    i = i + 1



print(template.to_json())

