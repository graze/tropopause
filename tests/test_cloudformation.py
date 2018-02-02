import json
import unittest
from troposphere import Template
from troposphere.autoscaling import LaunchConfiguration, Metadata
from troposphere.cloudformation import Init
from tropopause.cloudformation import InitConfigFromHTTP


class TestEc2(unittest.TestCase):
    """ Unit Tests for tropopause.cloudformation """
    def _create_test_document(self):
        template = Template()
        LaunchConfiguration(
            "launchconfig",
            template,
            ImageId='ami-809f84e6',
            InstanceType='t2.micro',
            Metadata=Metadata(
                Init(
                        {
                            'config': InitConfigFromHTTP(
                                url='http://www.example.com'
                            )
                        }
                    )
            )
        )
        return json.loads(template.to_json())

    def test_init_config_from_http_has_config(self):
        document = self._create_test_document()
        lc = document['Resources']['launchconfig']
        md = lc['Metadata']
        init = md['AWS::CloudFormation::Init']
        self.assertIn('config', init)

    def test_init_config_from_http_has_commands(self):
        document = self._create_test_document()
        lc = document['Resources']['launchconfig']
        md = lc['Metadata']
        init = md['AWS::CloudFormation::Init']
        self.assertIn('commands', init['config'])

    def test_init_config_from_http_has_files(self):
        document = self._create_test_document()
        lc = document['Resources']['launchconfig']
        md = lc['Metadata']
        init = md['AWS::CloudFormation::Init']
        self.assertIn('files', init['config'])

    def test_init_config_from_http_has_service(self):
        document = self._create_test_document()
        lc = document['Resources']['launchconfig']
        md = lc['Metadata']
        init = md['AWS::CloudFormation::Init']
        self.assertIn('services', init['config'])
