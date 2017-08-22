#tropopause github
# from troposphere import Ref, Template
# from troposphere.ec2 import VPC as _VPC
# from troposphere.ec2 import Subnet as _Subnet

# class VPC(_VPC):
#     def __init__(self, *args, **kwargs):
#         super(VPC, self).__init__(*args, **kwargs)
#         subnet = _Subnet(
#             "subnet",
#             t,
#             CidrBlock=kwargs['CidrBlock'],
#             VpcId=Ref(self)
#         )

# t = Template()
# vpc = VPC(
#     "porcorosso",
#     t,
#     CidrBlock = "10.0.0.0/20"
# )

# print(t.to_json())
import sys
def troposphere():
    import sys
    for d in sys.path:
        print(d)