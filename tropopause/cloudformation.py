from troposphere import Join, Ref
from troposphere.cloudformation import InitConfig
from troposphere.cloudformation import InitFile, InitFiles
from troposphere.cloudformation import InitService, InitServices
from tropopause.validators import valid_url


def FilesDecorator(func):
    """ Create the conf files for cfn-hup """
    def wrapper(*args, **kwargs):
        kwargs['files'] = InitFiles(
            {
                '/etc/cfn/cfn-hup.conf': InitFile(
                    content=Join('', [
                            '[main]\n',
                            'stack=',
                            Ref('AWS::StackId'),
                            '\n',
                            'region=',
                            Ref('AWS::Region'),
                            '\n'
                        ]
                    ),
                    mode='00400',
                    owner='root',
                    group='root'
                ),
                '/etc/cfn/hooks.d/cfn-auto-reloader.conf': InitFile(
                    content=Join('', [
                            '[cfn-auto-reloader-hook]\n',
                            'triggers=post.update\n',
                            'path=Resources.ContainerInstances',
                            '.Metadata.AWS::CloudFormation::Init\n',
                            'action=/opt/aws/bin/cfn-init -v ',
                            '--stack ',
                            Ref('AWS::StackName'),
                            ' ',
                            '--resource ContainerInstances ',
                            '--region ',
                            Ref('AWS::Region'),
                            '\n',
                            'runas=root\n'
                        ]
                    ),
                    mode='00400',
                    owner='root',
                    group='root'
                )
            }
        )
        return(func(*args, **kwargs))
    return wrapper


def ServicesDecorator(func):
    """ Make sure cfn-hup is running """
    def wrapper(*args, **kwargs):
        kwargs['services'] = {
            'sysvinit': InitServices(
                {
                    'cfn-hup': InitService(
                        ensureRunning='true',
                        enabled='true',
                        files=[
                            '/etc/cfn/cfn-hup.conf',
                            '/etc/cfn/hooks.d/cfn-auto-reloader.conf'
                        ]
                    )
                }
            )
        }
        return(func(*args, **kwargs))
    return wrapper


def CommandsDecoratorHTTP(func):
    """ Run shell script from http/https """
    def wrapper(*args, **kwargs):
        if 'url' in kwargs and valid_url(kwargs['url']):
            kwargs['commands'] = {
                '01_bootstrap_from_http': {
                    'command': '/usr/bin/curl -s '
                    + kwargs['url']
                    + ' | /bin/sh'
                }
            }
        return(func(*args, **kwargs))
    return wrapper


def CommandsDecoratorS3(func):
    """ Run shell script from s3 """
    def wrapper(*args, **kwargs):
        if 'url' in kwargs:
            kwargs['commands'] = {
                '01_bootstrap_from_http': {
                    'command': '/usr/bin/aws s3 cp '
                    + kwargs['url']
                    + ' - | /bin/sh'
                }
            }
        return(func(*args, **kwargs))
    return wrapper


class InitConfigFromHTTP(InitConfig):
    """ Bootstrap an instance from HTTP(S) """
    @ServicesDecorator
    @FilesDecorator
    @CommandsDecoratorHTTP
    def __init__(self, *args, **kwargs):
        self.props['url'] = (str, True)
        super().__init__(*args, **kwargs)


class InitConfigFromS3(InitConfig):
    """ Bootstrap an instance from S3 """
    @ServicesDecorator
    @FilesDecorator
    @CommandsDecoratorS3
    def __init__(self, *args, **kwargs):
        self.props['url'] = (str, True)
        super().__init__(*args, **kwargs)
