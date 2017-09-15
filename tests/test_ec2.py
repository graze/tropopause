import unittest
from tropopause import Tags
from tropopause.ec2 import InternetGatewayVPC
from tropopause.ec2 import PublicSubnet, PrivateSubnet, SecureSubnet
from troposphere import Ref, Template
from troposphere.ec2 import EIP, InternetGateway, NatGateway, Route, RouteTable
from troposphere.ec2 import Subnet, SubnetRouteTableAssociation
from troposphere.ec2 import VPC, VPCGatewayAttachment


class TestEc2(unittest.TestCase):
    """ Unit Tests for tropopause.ec2 overrides """
    AvailabilityZone = 'us-east-1a'
    CidrBlock = '10.0.0.0/24'
    PublicSubnetName = 'publicsubnet'
    PrivateSubnetName = 'privatesubnet'
    SecureSubnetName = 'securesubnet'
    VpcName = 'vpc'

    def _create_test_document(self):
        template = Template('testtemplate')
        test_vpc = InternetGatewayVPC(
            self.VpcName,
            template,
            CidrBlock=self.CidrBlock,
            Tags=Tags(Test='test')
        )
        PublicSubnet(
            self.PublicSubnetName,
            template,
            AvailabilityZone=self.AvailabilityZone,
            CidrBlock=self.CidrBlock,
            Tags=Tags(Test='subtest', SubTest='subtest'),
            VpcId=Ref(test_vpc)
        )
        PrivateSubnet(
            self.PrivateSubnetName,
            template,
            AvailabilityZone=self.AvailabilityZone,
            CidrBlock=self.CidrBlock,
            Tags=Tags(Test='subtest', SubTest='subtest'),
            VpcId=Ref(test_vpc)
        )
        SecureSubnet(
            self.SecureSubnetName,
            template,
            AvailabilityZone=self.AvailabilityZone,
            CidrBlock=self.CidrBlock,
            Tags=Tags(Test='subtest', SubTest='subtest'),
            VpcId=Ref(test_vpc)
        )
        return template

    def test_internet_vpc_exists(self):
        template = self._create_test_document()
        vpc = template.resources[self.VpcName]
        self.assertIsInstance(
            vpc,
            VPC
        )

    def test_internet_gateway_exists(self):
        template = self._create_test_document()
        internet_gateway = template.resources['internetgateway']
        self.assertIsInstance(
            internet_gateway,
            InternetGateway
        )

    def test_internet_gateway_attached_to_vpc(self):
        template = self._create_test_document()
        vpc_gateway_attachment = template.resources['vpcgatewayattachment']
        self.assertIsInstance(
            vpc_gateway_attachment,
            VPCGatewayAttachment
        )

    def test_public_subnet_exists(self):
        template = self._create_test_document()
        subnet = template.resources[self.PublicSubnetName]
        self.assertIsInstance(
            subnet,
            Subnet
        )

    def test_eip_exists(self):
        template = self._create_test_document()
        self.assertIsInstance(
            template.resources[self.PublicSubnetName + 'eip'],
            EIP
        )

    def test_public_subnet_has_nat_gateway_attached(self):
        template = self._create_test_document()
        subnet = template.resources[self.PublicSubnetName]
        nat_gateway = template.resources[self.PublicSubnetName + 'natgateway']
        self.assertIsInstance(
            nat_gateway,
            NatGateway
        )
        self.assertEqual(
            subnet.name,
            nat_gateway.properties['SubnetId'].data['Ref']
        )

    def test_nat_gateway_for_eip_attachment(self):
        template = self._create_test_document()
        eip = template.resources[self.PublicSubnetName + 'eip']
        nat_gateway = template.resources[self.PublicSubnetName + 'natgateway']
        self.assertEqual(
            eip.name,
            nat_gateway.properties['AllocationId'].data['Fn::GetAtt'][0]
        )

    def test_public_route_exists(self):
        template = self._create_test_document()
        route = template.resources[self.PublicSubnetName + 'route']
        self.assertIsInstance(
            route,
            Route
        )

    def test_public_route_is_correct(self):
        template = self._create_test_document()
        route = template.resources[self.PublicSubnetName + 'route']
        self.assertEqual(
            route.properties['DestinationCidrBlock'],
            '0.0.0.0/0'
        )

    def test_public_route_table_exists(self):
        template = self._create_test_document()
        route_table = template.resources[self.PublicSubnetName + 'routetable']
        self.assertIsInstance(
            route_table,
            RouteTable
        )

    def test_public_route_associated_with_public_route_table(self):
        template = self._create_test_document()
        route = template.resources[self.PublicSubnetName + 'route']
        route_table = template.resources[self.PublicSubnetName + 'routetable']
        self.assertEqual(
            route_table.name,
            route.properties['RouteTableId'].data['Ref']
        )

    def test_public_route_table_associated_with_public_subnet(self):
        template = self._create_test_document()
        route_table = template.resources[self.PublicSubnetName + 'routetable']
        subnet = template.resources[self.PublicSubnetName]
        subnet_route_table_association = template.resources[
            self.PublicSubnetName + 'subnetroutetableassociation'
        ]
        self.assertIsInstance(
            subnet_route_table_association,
            SubnetRouteTableAssociation
        )
        self.assertEqual(
            subnet_route_table_association.properties['RouteTableId']
            .data['Ref'],
            route_table.name
        )
        self.assertEqual(
            subnet_route_table_association.properties['SubnetId'].data['Ref'],
            subnet.name
        )

    def test_private_subnet_exists(self):
        template = self._create_test_document()
        subnet = template.resources[self.PrivateSubnetName]
        self.assertIsInstance(
            subnet,
            Subnet
        )

    def test_private_route_exists(self):
        template = self._create_test_document()
        route = template.resources[self.PrivateSubnetName + 'route']
        self.assertIsInstance(
            route,
            Route
        )

    def test_private_route_is_correct(self):
        template = self._create_test_document()
        route = template.resources[self.PrivateSubnetName + 'route']
        self.assertEqual(
            route.properties['DestinationCidrBlock'],
            '0.0.0.0/0'
        )

    def test_private_route_table_exists(self):
        template = self._create_test_document()
        route_table = template.resources[self.PrivateSubnetName + 'routetable']
        self.assertIsInstance(
            route_table,
            RouteTable
        )

    def test_private_route_associated_with_private_route_table(self):
        template = self._create_test_document()
        route = template.resources[self.PrivateSubnetName + 'route']
        route_table = template.resources[self.PrivateSubnetName + 'routetable']
        self.assertEqual(
            route_table.name,
            route.properties['RouteTableId'].data['Ref']
        )

    def test_private_route_table_associated_with_private_subnet(self):
        template = self._create_test_document()
        route_table = template.resources[self.PrivateSubnetName + 'routetable']
        subnet = template.resources[self.PrivateSubnetName]
        subnet_route_table_association = template.resources[
            self.PrivateSubnetName + 'subnetroutetableassociation'
        ]
        self.assertIsInstance(
            subnet_route_table_association,
            SubnetRouteTableAssociation
        )
        self.assertEqual(subnet_route_table_association.properties[
            'RouteTableId'].data['Ref'],
            route_table.name
        )
        self.assertEqual(
            subnet_route_table_association.properties['SubnetId'].data['Ref'],
            subnet.name
        )

    def test_vpc_has_tags(self):
        template = self._create_test_document()
        vpc = template.resources[self.VpcName]
        self.assertIsInstance(
            vpc.properties['Tags'],
            Tags
        )
        self.assertIn(
            {'Key': 'Test', 'Value': 'test'},
            vpc.properties['Tags'].tags
        )

    def test_internet_gateway_has_tags(self):
        template = self._create_test_document()
        internet_gateway = template.resources['internetgateway']
        self.assertIsInstance(
            internet_gateway.properties['Tags'],
            Tags
        )
        self.assertIn(
            {'Key': 'Test', 'Value': 'test'},
            internet_gateway.properties['Tags'].tags
        )

    def test_public_subnet_has_tags(self):
        template = self._create_test_document()
        subnet = template.resources[self.PublicSubnetName]
        self.assertIsInstance(
            subnet.properties['Tags'],
            Tags
        )
        self.assertIn(
            {'Key': 'Test', 'Value': 'subtest'},
            subnet.properties['Tags'].tags
        )
        self.assertIn(
            {'Key': 'SubTest', 'Value': 'subtest'},
            subnet.properties['Tags'].tags
        )

    def test_public_route_table_has_tags(self):
        template = self._create_test_document()
        route_table = template.resources[self.PublicSubnetName + 'routetable']
        self.assertIsInstance(
            route_table.properties['Tags'],
            Tags
        )
        self.assertIn(
            {'Key': 'Test', 'Value': 'subtest'},
            route_table.properties['Tags'].tags
        )
        self.assertIn(
            {'Key': 'SubTest', 'Value': 'subtest'},
            route_table.properties['Tags'].tags
        )

    def test_private_subnet_has_tags(self):
        template = self._create_test_document()
        subnet = template.resources[self.PrivateSubnetName]
        self.assertIsInstance(
            subnet.properties['Tags'],
            Tags
        )
        self.assertIn(
            {'Key': 'Test', 'Value': 'subtest'},
            subnet.properties['Tags'].tags
        )
        self.assertIn(
            {'Key': 'SubTest', 'Value': 'subtest'},
            subnet.properties['Tags'].tags
        )

    def test_private_route_table_has_tags(self):
        template = self._create_test_document()
        route_table = template.resources[self.PrivateSubnetName + 'routetable']
        self.assertIsInstance(
            route_table.properties['Tags'],
            Tags
        )
        self.assertIn(
            {'Key': 'Test', 'Value': 'subtest'},
            route_table.properties['Tags'].tags
        )
        self.assertIn(
            {'Key': 'SubTest', 'Value': 'subtest'},
            route_table.properties['Tags'].tags
        )

    def test_secure_subnet_has_tags(self):
        template = self._create_test_document()
        subnet = template.resources[self.SecureSubnetName]
        self.assertIsInstance(
            subnet.properties['Tags'],
            Tags
        )
        self.assertIn(
            {'Key': 'Test', 'Value': 'subtest'},
            subnet.properties['Tags'].tags
        )
        self.assertIn(
            {'Key': 'SubTest', 'Value': 'subtest'},
            subnet.properties['Tags'].tags
        )


if __name__ == '__main__':
    unittest.main()
