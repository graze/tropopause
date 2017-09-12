# tropopause

[![Software License](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square)](LICENSE.md)
[![Build Status](https://img.shields.io/travis/graze/tropopause/master.svg?style=flat-square)](https://travis-ci.org/graze/tropopause)

## About

tropopause - a wrapper for [troposphere](https://github.com/cloudtools/troposphere) to create Cloudformation templates and abstracts away boilerplate.

The tropopause library extends troposphere by adding composite objects that create the Cloudformation objects required to support specific tasks. 

## Installation

This library has been developed and tested against Python 3.

tropopause can be installed using the pip distribution system for Python by issuing:

`$ pip install graze-tropopause`

Alternatively, you can run use setup.py to install by cloning this repository and issuing:

`$ python setup.py install  # you may need sudo depending on your python installation`

## Development

For development, consult [CONTRIBUTING.md](https://github.com/graze/tropopause/blob/master/CONTRIBUTING.md):

## Usage

tropopause usage is similar to that of troposphere, the principle difference is that the composite objects always expect the template object to be passed in as the second parameter.

```python
>>> from troposphere import Template
>>> from tropopause.ec2 import InternetGatewayVPC
>>> t = Template()
>>> vpc = InternetGatewayVPC("example", t, CidrBlock="10.0.0.0/24")
>>> print(t.to_json())
{
    "Resources": {
        "example": {
            "Properties": {
                "CidrBlock": "10.0.0.0/24"
            },
            "Type": "AWS::EC2::VPC"
        },
        "internetgateway": {
            "Type": "AWS::EC2::InternetGateway"
        },
        "vpcgatewayattachment": {
            "Properties": {
                "InternetGatewayId": {
                    "Ref": "internetgateway"
                },
                "VpcId": {
                    "Ref": "example"
                }
            },
            "Type": "AWS::EC2::VPCGatewayAttachment"
        }
    }
}
```

## Available Objects

### tropopause.ec2
* `InternetGatewayVPC` - Creates a VPC, an InternetGateway and the required VPCGatewayAttachment
* `PublicSubnet` - Creates a Subnet, EIP and a NatGateway. Connects everything together and routes all traffic via an existing InternetGateway
* `PrivateSubnet` - Creates a Subnet, attempts to find a Public Subnet in the same Availability Zone and then routes all traffic via an existing NatGateway
* `SecureSubnet` - Creates a Subnet, does not route traffic to the Internet

## Licensing

tropopause is licensed under the MIT license. See [LICENSE.md](https://github.com/graze/tropopause/blob/master/LICENSE.md) for the tropopause full license text.
