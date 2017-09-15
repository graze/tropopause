from tropopause import Tags
from tropopause.ec2 import InternetGatewayVPC, PublicSubnet
from troposphere import Ref, Template

CidrBlock = '10.10.0.0/20'
region = 'us-east-1'

template = Template()
template.add_version('2010-09-09')
template.add_description('Example VPC')
vpc = InternetGatewayVPC(
    'vpc',
    template,
    CidrBlock=CidrBlock,
    Tags=Tags(
        Global='Global Value',
        Local='Local Value'
    )
)

PublicSubnet(
    'public',
    template,
    AvailabilityZone='us-east-1a',
    CidrBlock=CidrBlock,
    MapPublicIpOnLaunch=True,
    VpcId=Ref(vpc),
    Tags=Tags(
        Local='Override the Local Value'
    )
)

print(template.to_json())
