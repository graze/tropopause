from tropopause.iam import RoleFromYaml, PolicyFromYaml, PolicyTypeFromYaml
from troposphere import Ref, Template
from troposphere.ec2 import VPC

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
role = RoleFromYaml(
    'vpcrole',
    template,
    Path='/',
    Policies=[
        PolicyFromYaml(
            'vpcpolicy',
            PolicyName='Policy',
            PolicyDocument='policies/policy_monitoring_agent.yaml'
        )
    ],
    AssumeRolePolicyDocument='policies/policy_assumerole.yaml'
)
PolicyTypeFromYaml(
    'vpcpolicytype',
    template,
    PolicyName='PolicyType',
    PolicyDocument="policies/policy_ecr.yaml",
    Roles=[
        Ref(role)
    ]
)

print(template.to_json())
