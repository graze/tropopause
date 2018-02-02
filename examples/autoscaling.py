from troposphere import Ref, Template
from troposphere.autoscaling import Metadata
from troposphere.cloudformation import Init
from troposphere.ec2 import Subnet, VPC
from tropopause.autoscaling import AutoScalingGroup, LaunchConfigurationRPM
from tropopause.cloudformation import InitConfigFromS3


CidrBlock = '10.10.0.0/20'
region = 'us-east-1'

template = Template()
template.add_version('2010-09-09')
template.add_description('Example VPC')
vpc = VPC(
    'vpc',
    template,
    CidrBlock=CidrBlock
)


subnet = Subnet(
    'subnet',
    template,
    AvailabilityZone='us-east1a',
    CidrBlock=CidrBlock,
    MapPublicIpOnLaunch=False,
    VpcId=Ref(vpc)
)

launchconfig = LaunchConfigurationRPM(
    "launchconfig",
    template,
    ImageId='ami-13f7226a',
    InstanceType='t2.micro',
    Metadata=Metadata(
        Init(
                {
                    'config': InitConfigFromS3(
                        url="https://s3.amazonaws.com/example/example.sh"
                    )
                }
            )
    )
)

asg = AutoScalingGroup(
    "asg",
    template,
    MinSize=0,
    MaxSize=1,
    DesiredCapacity=1,
    LaunchConfigurationName=Ref("launchconfig"),
    VPCZoneIdentifier=[
        Ref(subnet)
    ]
)


print(template.to_json())
