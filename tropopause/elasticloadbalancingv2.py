from troposphere import Ref, Template
from troposphere import Tags as upstreamTags
from troposphere.ec2 import VPC
from troposphere.elasticloadbalancingv2 import (
    LoadBalancer, TargetGroup, Listener, Action
)
from tropopause import Tags


def AddTagsFromVPC(func):
    """ Helper to inject VPC tags into **kwargs """
    def wrapper(*args, **kwargs):
        tags = Tags()
        if isinstance(args[-1], Template):
            vpc = next(
                i for i in args[-1].resources.items()
                if isinstance(i[-1], VPC)
            )[-1]
        if isinstance(vpc, VPC) and 'Tags' in vpc.properties:
            tags = tags + vpc.properties['Tags']
        if 'Tags' in kwargs and isinstance(kwargs['Tags'], upstreamTags):
            tags = tags + kwargs['Tags']
        kwargs['Tags'] = tags
        return(func(*args, **kwargs))
    return wrapper


class SecureLoadBalancerWithListener(LoadBalancer):
    ''' Creates an Application LoadBalancer with a Listener. '''
    @AddTagsFromVPC
    def __init__(self, title, template, *args, **kwargs):
        self.props['Port'] = (str, True)
        self.props['Certificates'] = (list, True)
        self.props['VpcId'] = (str, True)
        super().__init__(title, template, *args, **kwargs)
        target_group = TargetGroup(
            title + 'dummy',
            VpcId=self.properties['VpcId'],
            Port='80',
            Protocol='HTTP'
        )
        template.add_resource(target_group)
        template.add_resource(
            Listener(
                title + "httpslistener",
                LoadBalancerArn=Ref(self),
                Port=self.properties['Port'],
                Protocol='HTTPS',
                Certificates=self.properties['Certificates'],
                DefaultActions=[
                    Action(
                        Type='forward',
                        TargetGroupArn=Ref(target_group)
                    )
                ]
            )
        )
        self.props.pop('Port')
        self.properties.pop('Port')
        self.props.pop('Certificates')
        self.properties.pop('Certificates')
        self.props.pop('VpcId')
        self.properties.pop('VpcId')
