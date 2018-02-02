from troposphere import Tags as baseTags
from troposphere import Base64, Join, Ref
from troposphere.autoscaling import Tag, Tags
from troposphere.autoscaling import AutoScalingGroup as upstreamASG
from troposphere.autoscaling import LaunchConfiguration


def AddGenericUserDataRPM(func):
    """ Add sensible cloudinit into UserData for RPM based systems """
    def wrapper(*args, **kwargs):
        if 'UserData' not in kwargs:
            name = args[1]
            cfn_signal = Join(
                '',
                [
                    'INSTANCE=$(curl http://169.254.169.254/latest/meta-data/instance-id 2> /dev/null)',  # noqa
                    ' && ',
                    'QUERY=AutoScalingInstances[?InstanceId==\\\'$INSTANCE\\\'].[AutoScalingGroupName]',  # noqa
                    ' && ',
                    'RESOURCE=$(/usr/bin/aws --region=',
                    Ref('AWS::Region'),
                    ' ',
                    'autoscaling describe-auto-scaling-instances --query=$QUERY --output=text 2> /dev/null) ',  # noqa
                    ' && ',
                    '/opt/aws/bin/cfn-signal -e $? ',
                    '--stack ',
                    Ref('AWS::StackName'),
                    ' ',
                    '--resource ',
                    '$RESOURCE ',
                    ' ',
                    '--region ',
                    Ref('AWS::Region'),
                    '\n'
                ]
            )
            kwargs['UserData'] = Base64(Join(
                ' ',
                [
                    '#!/bin/bash -xe\n',
                    'yum install -y aws-cfn-bootstrap aws-cli\n',
                    '/opt/aws/bin/cfn-init -v ',
                    '--stack ',
                    Ref('AWS::StackName'),
                    '--resource',
                    name,
                    '--region',
                    Ref('AWS::Region'),
                    '\n',
                    cfn_signal
                ]
            ))
        return(func(*args, **kwargs))
    return wrapper


def InheritAndCastTags(func):
    """ Make sure tags correctly have PropagateAtLaunch """
    def wrapper(*args, **kwargs):
        result = []
        if 'VPCZoneIdentifier' in kwargs:
            for ref in kwargs['VPCZoneIdentifier']:
                if isinstance(ref, Ref):
                    subnet = args[-1].resources[ref.data['Ref']]
                    if 'Tags' in subnet.properties:
                        append = True
                        for tag in subnet.properties['Tags'].tags:
                            for r_tag in result:
                                if r_tag.data['Key'] == tag['Key']:
                                    append = False
                            if append is True:
                                result.append(Tag(
                                    tag['Key'], tag['Value'], True)
                                             )
        if 'Tags' in kwargs and isinstance(kwargs['Tags'], baseTags):
            for tag in kwargs['Tags'].tags:
                result.append(Tag(tag['Key'], tag['Value'], True))
        if 'Tags' in kwargs and isinstance(kwargs['Tags'], Tags):
            result.append(kwargs['Tags'])
        kwargs['Tags'] = result
        return func(*args, **kwargs)
    return wrapper


class AutoScalingGroup(upstreamASG):
    """ Improved Tag Support """
    @InheritAndCastTags
    def __init__(self, title, template, *args, **kwargs):
        super().__init__(title, template, *args, **kwargs)


class LaunchConfigurationRPM(LaunchConfiguration):
    """ Adds a simple UserData that handles cloudinit """
    @AddGenericUserDataRPM
    def __init__(self, title, template, *args, **kwargs):
        super().__init__(title, template, *args, **kwargs)
