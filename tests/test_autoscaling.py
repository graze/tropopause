import unittest

from tropopause import Tags as BaseTags
from tropopause.ec2 import InternetGatewayVPC, PublicSubnet
from tropopause.autoscaling import AutoScalingGroup, LaunchConfigurationRPM
from troposphere import Ref, Template
from troposphere.autoscaling import LaunchConfiguration, Tag


class TestAutoscaling(unittest.TestCase):
    """ Unit Tests for tropopause.autoscaling """

    def _create_test_document(self):
        template = Template()
        vpc = InternetGatewayVPC(
            'igw',
            template,
            CidrBlock='10.0.0.0/16',
            Tags=BaseTags(a='b')
        )
        PublicSubnet(
            'subnet',
            template,
            CidrBlock='10.0.0.0/24',
            VpcId=Ref(vpc),
            Tags=BaseTags(f='fpp')
        )
        return template

    def test_user_data_decorator(self):
        template = self._create_test_document()
        lc = LaunchConfigurationRPM(
            "launchconfig",
            template,
            ImageId="ami-123456",
            InstanceType="t2.micro"
        )
        self.assertIsInstance(lc.props['UserData'], tuple)

    def test_tag_inheritance_decorator_vpc(self):
        template = self._create_test_document()
        lc = LaunchConfigurationRPM(
            'launchconfig',
            template,
            ImageId='ami-12345678',
            InstanceType='t2.micro'
        )
        AutoScalingGroup(
            'asg',
            template,
            MinSize=0,
            MaxSize=1,
            LaunchConfigurationName=Ref(lc),
            VPCZoneIdentifier=[
                Ref('subnet')
            ]
        )
        self.assertIsInstance(
             template.resources['asg'].properties['Tags'][0],
             Tag
        )

    def test_launch_configuration_rpm(self):
        template = self._create_test_document()
        lc = LaunchConfigurationRPM(
            'launchconfig',
            template,
            ImageId='ami-12345678',
            InstanceType='t2.micro'
        )
        self.assertIsInstance(
             lc,
             LaunchConfiguration
        )
