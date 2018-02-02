from ipaddress import ip_network
from troposphere import Ref, Tags, Template
from tropopause.ec2 import InternetGatewayVPC
from tropopause.ec2 import PublicSubnet, PrivateSubnet, SecureSubnet

CidrBlock = '10.10.0.0/20'
region = 'us-east-1'
subnets = list(ip_network(CidrBlock).subnets(prefixlen_diff=4))

template = Template()
template.add_version('2010-09-09')
template.add_description('Example VPC')
vpc = InternetGatewayVPC(
    'vpc',
    template,
    CidrBlock=CidrBlock,
    Tags=Tags(a='a')
)

zones = ['a', 'b', 'c']

i = 0
for zone in zones:
    PublicSubnet(
        'public' + region.replace('-', '') + zone,
        template,
        AvailabilityZone=region + zone,
        CidrBlock=str(subnets[i % len(zones) + 0 * len(zones)]),
        MapPublicIpOnLaunch=True,
        VpcId=Ref(vpc)
    )
    PrivateSubnet(
        'private' + region.replace('-', '') + zone,
        template,
        AvailabilityZone=region + zone,
        CidrBlock=str(subnets[i % len(zones) + 1 * len(zones)]),
        MapPublicIpOnLaunch=False,
        VpcId=Ref(vpc)
    )
    SecureSubnet(
        'secure' + region.replace('-', '') + zone,
        template,
        AvailabilityZone=region + zone,
        CidrBlock=str(subnets[i % len(zones) + 2 * len(zones)]),
        MapPublicIpOnLaunch=False,
        VpcId=Ref(vpc)
    )
    i = i + 1

print(template.to_json())
