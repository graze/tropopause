import unittest
from troposphere import Template, Ref
from tropopause.iam import RoleFromYaml, PolicyFromYaml, PolicyTypeFromYaml


class TestIAM(unittest.TestCase):
    """ Unit Tests for tropopause.IAM """

    def _create_test_document(self):
        template = Template()
        role_from_yaml = RoleFromYaml(
            'role',
            template,
            Path='/',
            Policies=[
                PolicyFromYaml(
                    'policy',
                    PolicyName='policy',
                    PolicyDocument='tests/data/iam_policy.yaml'
                )
            ],
            AssumeRolePolicyDocument='tests/data/iam_role.yaml'
        )
        PolicyTypeFromYaml(
            'policytype',
            template,
            PolicyName='policytype',
            PolicyDocument="tests/data/iam_policy_type.yaml",
            Roles=[
                Ref(role_from_yaml)
            ]
        )
        return template

    def test_role_from_yaml(self):
        pass

    def test_policy_from_yaml(self):
        pass

    def test_policy_type_from_yaml(self):
        pass
