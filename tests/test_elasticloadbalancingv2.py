import unittest
from troposphere import Ref, Template
from troposphere.elasticloadbalancingv2 import (
    Certificate, LoadBalancer, TargetGroup, Action
)
from troposphere.ec2 import VPC, Subnet
from tropopause import Tags
from tropopause.elasticloadbalancingv2 import SecureLoadBalancerWithListener


class TestElasticLoadBalancingV2(unittest.TestCase):
    """ Unit Tests for tropopause.autoscalingv2 """
    certificate_arn = 'arn:aws:acm:us-east-1::certificate/x'

    def _create_test_document(self):
        template = Template()
        vpc = VPC(
            'default',
            template,
            CidrBlock='10.0.0.0/16',
            Tags=Tags(
                a='set',
                b='unset'
            )
        )
        subnet = Subnet(
            'subnet',
            template,
            CidrBlock='10.0.0.0/24',
            VpcId=Ref(vpc)
        )
        SecureLoadBalancerWithListener(
            'loadbalancer',
            template,
            Certificates=[
                Certificate(
                    CertificateArn=self.certificate_arn
                )
            ],
            Port='443',
            Subnets=[
                subnet
            ],
            Tags=Tags(
                b='set',
                c='set'
            ),
            VpcId=Ref(vpc)
        )
        return template

    def test_target_group_exists(self):
        template = self._create_test_document()
        target_group = template.resources['loadbalancerdummy']
        self.assertIsInstance(
            target_group,
            TargetGroup
        )

    def test_listener_has_certificate_and_is_tls(self):
        template = self._create_test_document()
        listener = template.resources['loadbalancerhttpslistener']
        cert = listener.properties['Certificates'][0]
        self.assertEqual(
            cert.properties['CertificateArn'],
            self.certificate_arn
        )
        self.assertEqual(
            listener.properties['Protocol'],
            'HTTPS'
        )

    def test_listener_default_action(self):
        template = self._create_test_document()
        listener = template.resources['loadbalancerhttpslistener']
        self.assertIsInstance(
            listener.properties['DefaultActions'][0],
            Action
        )

    def test_listener_loadbalancer_association(self):
        template = self._create_test_document()
        listener = template.resources['loadbalancerhttpslistener']
        self.assertIsInstance(
            template.resources['loadbalancer'],
            LoadBalancer
        )
        self.assertEqual(
            listener.properties['LoadBalancerArn'].data['Ref'],
            'loadbalancer'
        )

    def test_tags_are_inherited(self):
        template = self._create_test_document()
        loadbalancer = template.resources['loadbalancer']
        tags = loadbalancer.properties['Tags'].tags
        self.assertIn(
            {'Key': 'a', 'Value': 'set'},
            tags
        )
        self.assertIn(
            {'Key': 'b', 'Value': 'set'},
            tags
        )
        self.assertIn(
            {'Key': 'c', 'Value': 'set'},
            tags
        )
