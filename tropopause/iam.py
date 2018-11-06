from troposphere.iam import PolicyType, Role, Policy
import yaml


class RoleFromYaml(Role):
    def __init__(self, title, template, *args, **kwargs):
        with open(kwargs['AssumeRolePolicyDocument'], 'r') as stream:
            document = yaml.load(stream)
        kwargs['AssumeRolePolicyDocument'] = document
        super().__init__(title, template, *args, **kwargs)


class PolicyFromYaml(Policy):
    def __init__(self, title, *args, **kwargs):
        with open(kwargs['PolicyDocument'], 'r') as stream:
            document = yaml.load(stream)
        kwargs['PolicyDocument'] = document
        super().__init__(title, *args, **kwargs)


class PolicyTypeFromYaml(PolicyType):
    def __init__(self, title, template, *args, **kwargs):
        with open(kwargs['PolicyDocument'], 'r') as stream:
            document = yaml.load(stream)
        kwargs['PolicyDocument'] = document
        super().__init__(title, template, *args, **kwargs)
